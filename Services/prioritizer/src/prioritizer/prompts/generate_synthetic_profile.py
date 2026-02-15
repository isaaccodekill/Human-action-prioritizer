from pathlib import Path
from openai import OpenAI
from prioritizer.settings import settings
from prioritizer.models import UserProfile
from pydantic import BaseModel


client = OpenAI(api_key=settings.openai_api_key)

class UserProfiles(BaseModel):
    profiles: list[UserProfile]

def generate_synthetic_profiles(num_profiles: int = 25) -> UserProfiles:

    response = client.responses.parse(
        model="gpt-5-mini-2025-08-07",
        input=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates synthetic user profiles for a carbon footprint action prioritizer. Each profile includes: city, climate_zone (tropical/temperate/cold/arid), primary_transport (car/motorcycle/bicycle/public_transit/walking), diet (heavy_meat/moderate_meat/vegetarian/vegan), housing_type (apartment/house), energy_source (grid/solar/generator), income_level (low/medium/high). The profiles should be globally diverse, including cities from Africa, Asia, Europe, South America, and North America. Return the profiles as a JSON array."
            },
            {
                "role": "user",
                "content": f"Generate {num_profiles} diverse user profiles for a carbon footprint action prioritizer. Each profile should include: city, climate_zone (tropical/temperate/cold/arid), primary_transport (car/motorcycle/bicycle/public_transit/walking), diet (heavy_meat/moderate_meat/vegetarian/vegan), housing_type (apartment/house), energy_source (grid/solar/generator), income_level (low/medium/high). Make them globally diverse — include cities from Africa, Asia, Europe, South America, North America. Return as JSON array."
            }
        ],
        text_format=UserProfiles
    )

    profiles = response.output_parsed
    return profiles


if __name__ == "__main__":
    synthetic_profiles = generate_synthetic_profiles()
    # write the output to a json file
    output_path = Path(__file__).resolve().parent.parent / "data" / "synthetic_profiles.json"
    with open(output_path, "w") as f:
        f.write(synthetic_profiles.model_dump_json(indent=2))