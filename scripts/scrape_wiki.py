import re
import time
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"
WIKI_API = "https://en.wikipedia.org/w/api.php"


HEADERS = {"User-Agent": "HumanActionPrioritizer/1.0 (educational project)"}


def fetch_article(title: str) -> str | None:
    """Fetch full plain-text extract of a Wikipedia article."""
    resp = requests.get(WIKI_API, params={
        "action": "query",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
    }, headers=HEADERS)
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("extract")


def slugify(name: str) -> str:
    """Turn a topic name into a safe filename."""
    return re.sub(r"[^\w\-]", "_", name.lower()).strip("_")


def scrape_all():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    success = 0
    failed = []

    for topic_name, wiki_title in WIKI_TOPICS.items():
        filename = slugify(topic_name) + ".txt"
        filepath = DATA_DIR / filename

        if filepath.exists():
            print(f"  Skipping {topic_name} (already exists)")
            success += 1
            continue

        print(f"  Fetching: {topic_name} -> {wiki_title}")
        text = fetch_article(wiki_title)

        if not text:
            print(f"  WARNING: No content for '{wiki_title}'")
            failed.append(topic_name)
            continue

        filepath.write_text(f"# {topic_name}\nSource: https://en.wikipedia.org/wiki/{wiki_title.replace(' ', '_')}\n\n{text}", encoding="utf-8")
        success += 1
        time.sleep(0.5)  # Be polite to the API

    print(f"\nDone: {success} saved, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")


WIKI_TOPICS = {
    # Transportation
    "Electric Cars": "Electric car",
    "Hybrid Cars": "Hybrid electric vehicle",
    "Electric Bicycles": "Electric bicycle",
    "Carpooling": "Carpool",
    "Public Transit": "Public transport",
    "Nonmotorized Transportation": "Active transport",
    "High-Speed Rail": "High-speed rail",

    # Electricity
    "Onshore Wind Turbines": "Wind power",
    "Offshore Wind Turbines": "Offshore wind power",
    "Distributed Solar PV": "Solar power",
    "Concentrated Solar": "Concentrated solar power",
    "LED Lighting": "LED lamp",
    "Geothermal Power": "Geothermal energy",
    "Small Hydropower": "Micro hydro",
    "Nuclear Power": "Nuclear power",

    # Buildings
    "Heat Pumps": "Heat pump",
    "Clean Cooking": "Clean cook stove",
    "Alternative Insulation Materials": "Building insulation",
    "Building Envelopes": "Building insulation",
    "Windows & Glass": "Insulated glazing",
    "Solar Hot Water": "Solar water heating",

    # Food & Agriculture
    "Annual Cropping": "Conservation agriculture",
    "Diets": "Plant-based diet",
    "Food Loss & Waste": "Food loss and waste",
    "Rice Production": "Paddy field",
    "Nutrient Management": "Nutrient management",
    "Silvopasture": "Silvopasture",

    # Land & Ecosystems
    "Forests: Tropical": "Tropical forest",
    "Forests: Temperate": "Temperate forest",
    "Forests: Boreal": "Taiga",
    "Forests: Subtropical": "Tropical and subtropical moist broadleaf forests",
    "Peatlands": "Peatland",
    "Coastal Wetlands": "Wetland",
    "Coastal Wetlands: Mangrove": "Mangrove",
    "Coastal Wetlands: Salt marsh": "Salt marsh",
    "Coastal Wetlands: Seagrass": "Seagrass",
    "Grasslands & Savannas": "Grassland",
    "Savannas": "Savanna",
    "Reforestation": "Reforestation",
    "Deforestation": "Deforestation",

    # Industry & Waste
    "Alternative Refrigerants": "Refrigerant",
    "Recycling: Metals": "Recycling",
    "Recycling: Paper and Cardboard": "Paper recycling",
    "Recycling: Plastics": "Plastic recycling",
    "Recycling: Glass": "Glass recycling",
    "Composting": "Compost",
    "Landfill Management": "Landfill gas",
    "Landfill Management: Biocovers": "Landfill gas utilization",
    "Cement Production": "Environmental impact of concrete",

    # Energy & Fugitive Emissions
    "Coal Mine Methane": "Coalbed methane",
    "Oil & Gas Methane": "Fugitive emission",

    # Cross-cutting Concepts
    "Greenhouse Gas": "Greenhouse gas",
    "Black Carbon": "Black carbon",
    "Carbon Sequestration": "Carbon sequestration",
    "Climate Change Mitigation": "Climate change mitigation",
}


if __name__ == "__main__":
    scrape_all()