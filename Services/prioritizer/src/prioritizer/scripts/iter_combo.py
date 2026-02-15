# exists only to help create combination of actions with synthetic user profiles, to create synthetic action pair scoring data. Not intended for production use.
import random
from itertools import combinations
from prioritizer.models import UserProfile, Action
import json
from pathlib import Path

def generate_action_combinations(actions: list[Action], user_profiles: list[UserProfile], pairs_per_profile: int = 150) -> list[dict]:
    all_pairs = list(combinations(actions, 2))

    result = []
    for profile in user_profiles:
        sampled = random.sample(all_pairs, min(pairs_per_profile, len(all_pairs)))
        for action_a, action_b in sampled:
            result.append({
                "action_a": action_a.model_dump(),
                "action_b": action_b.model_dump(),
                "user_profile": profile.model_dump()
            })

    return result

if __name__ == "__main__":
    data_path = Path(__file__).resolve().parent.parent / "data"
    action_path = data_path / "actions.json"
    profiles_path = data_path / "synthetic_profiles.json"

    with open(action_path, "r") as f:
        actions_data = json.load(f)
        actions = [Action(**action) for action in actions_data]

    with open(profiles_path, "r") as f:
        profiles_data = json.load(f)
        user_profiles = [UserProfile(**profile) for profile in profiles_data['profiles']]

    action_combinations = generate_action_combinations(actions, user_profiles, pairs_per_profile=150)

    print(f"Generated {len(action_combinations)} action combinations")

    output_path = data_path / "synthetic_action_combinations.json"
    with open(output_path, "w") as f:
        json.dump(action_combinations, f, indent=2)
