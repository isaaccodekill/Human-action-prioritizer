import asyncio
from openai import AsyncOpenAI
from prioritizer.settings import settings
from prioritizer.models import UserProfile, Action
from pydantic import BaseModel
from typing import Literal
from pathlib import Path
import json

client = AsyncOpenAI(api_key=settings.openai_api_key)

CONCURRENCY = 10

class ActionPair(BaseModel):
    action_a: Action
    action_b: Action
    user_profile: UserProfile


class ScoreResult(BaseModel):
    score: Literal[0, 1]  # 1 if action_a is better, 0 if action_b is better

class ScoredActionPair(BaseModel):
    action_a: Action
    action_b: Action
    user_profile: UserProfile
    score: int  # 1 if action_a is better, 0 if action_b is better

async def generate_synthetic_action_pair_scoring(action_a: Action, action_b: Action, user_profile: UserProfile) -> int:

    response = await client.responses.parse(
        model="gpt-5-mini-2025-08-07",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a climate action expert helping prioritize carbon reduction actions for individuals. "
                    "Given two climate actions and a user profile, determine which action would have MORE OVERALL IMPACT for this specific user.\n\n"
                    "Consider ALL of these factors in your decision:\n\n"
                    "1. CO2 reduction potential — how much greenhouse gas does each action reduce? Weight this heavily.\n"
                    "2. Relevance to user's lifestyle — does the action address the user's primary emission sources? "
                    "A transport action matters more for someone who drives daily. A diet action matters more for a heavy meat eater. "
                    "An energy action matters more for someone on grid electricity.\n"
                    "3. Cost relative to income — expensive actions are less feasible for low-income users. "
                    "Actions with net savings are more attractive for budget-conscious users.\n"
                    "4. Speed of action — \"Emergency Brake\" actions have immediate atmospheric impact. "
                    "\"Gradual\" actions take time. \"Delayed\" actions take even longer. Prefer faster actions when impact is similar.\n"
                    "5. Co-benefits — consider environment benefits (air quality, water quality, nature protection) "
                    "and human wellbeing benefits (health, income, food security, equality) that are relevant to the user's context.\n"
                    "6. Climate adaptation — if the user lives in an area prone to floods, droughts, or extreme heat, "
                    "actions with matching adaptation benefits are more valuable.\n"
                    "7. Feasibility — is this action realistic for the user's situation? "
                    "Solar panels matter less for apartment dwellers. Public transit matters less in cities without infrastructure.\n\n"
                    "You must choose one action. No ties allowed. Pick the action with the best combination of impact, relevance, and feasibility for this specific user.\n\n"
                    "Return 1 if Action A is better, 0 if Action B is better."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Compare these two climate actions for this user and pick which has more overall impact.\n\n"
                    f"USER PROFILE:\n"
                    f"- City: {user_profile.city}\n"
                    f"- Climate zone: {user_profile.climate_zone}\n"
                    f"- Primary transport: {user_profile.primary_transport}\n"
                    f"- Diet: {user_profile.diet}\n"
                    f"- Housing: {user_profile.housing_type}\n"
                    f"- Energy source: {user_profile.energy_source}\n"
                    f"- Income level: {user_profile.income_level}\n\n"
                    f"ACTION A:\n"
                    f"- Solution: {action_a.solution}\n"
                    f"- Sector: {action_a.sector}\n"
                    f"- GHG Impact (Gt CO2): {action_a.ghg_impact}\n"
                    f"- Cost ($/t CO2): {action_a.cost}\n"
                    f"- Speed of action: {action_a.speed_of_action}\n"
                    f"- Mode: {action_a.mode}\n"
                    f"- Climate pollutants: {action_a.climate_pollutants_mitigated}\n"
                    f"- Adaptation benefits: {action_a.climate_adaptation_benefits}\n"
                    f"- Environment benefits: {action_a.environment_benefits}\n"
                    f"- Wellbeing benefits: {action_a.human_wellbeing_benefits}\n\n"
                    f"ACTION B:\n"
                    f"- Solution: {action_b.solution}\n"
                    f"- Sector: {action_b.sector}\n"
                    f"- GHG Impact (Gt CO2): {action_b.ghg_impact}\n"
                    f"- Cost ($/t CO2): {action_b.cost}\n"
                    f"- Speed of action: {action_b.speed_of_action}\n"
                    f"- Mode: {action_b.mode}\n"
                    f"- Climate pollutants: {action_b.climate_pollutants_mitigated}\n"
                    f"- Adaptation benefits: {action_b.climate_adaptation_benefits}\n"
                    f"- Environment benefits: {action_b.environment_benefits}\n"
                    f"- Wellbeing benefits: {action_b.human_wellbeing_benefits}\n\n"
                    f"Which action has more overall impact for this user? You must pick A or B."
                )
            }
        ],
        text_format=ScoreResult
    )

    score = response.output_parsed.score
    return score


completed_count = 0
failed_count = 0

async def score_combo(i: int, total: int, combo: dict, semaphore: asyncio.Semaphore) -> dict | None:
    global completed_count, failed_count
    async with semaphore:
        action_a = Action(**combo['action_a'])
        action_b = Action(**combo['action_b'])
        user_profile = UserProfile(**combo['user_profile'])

        try:
            score = await generate_synthetic_action_pair_scoring(action_a, action_b, user_profile)
            completed_count += 1
            print(f"[{completed_count}/{total}] {action_a.solution} vs {action_b.solution} ({user_profile.city}) -> {score}", flush=True)

            return ScoredActionPair(
                action_a=action_a,
                action_b=action_b,
                user_profile=user_profile,
                score=score
            ).model_dump()
        except Exception as e:
            failed_count += 1
            print(f"[FAILED {failed_count}] {action_a.solution} vs {action_b.solution} ({user_profile.city}): {e}", flush=True)
            return None


async def main():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    action_pairing_path = data_dir / "synthetic_action_combinations.json"
    action_scores_path = data_dir / "synthetic_action_pair_scores.json"

    with open(action_pairing_path, "r") as f:
        action_combinations = json.load(f)

    total = len(action_combinations)
    print(f"Starting scoring of {total} action combinations with {CONCURRENCY} concurrent workers...", flush=True)

    semaphore = asyncio.Semaphore(CONCURRENCY)
    tasks = [
        score_combo(i, total, combo, semaphore)
        for i, combo in enumerate(action_combinations, 1)
    ]
    results = await asyncio.gather(*tasks)
    scored_pairs = [r for r in results if r is not None]

    with open(action_scores_path, "w") as f:
        json.dump(scored_pairs, f, indent=2)
    print(f"\nDone! {len(scored_pairs)} scored, {failed_count} failed. Written to {action_scores_path}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
