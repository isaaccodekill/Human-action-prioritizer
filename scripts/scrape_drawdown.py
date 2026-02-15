"""Scrape solution pages from drawdown.org/explorer for context on each action."""

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "documents" / "drawdown"
ACTIONS_JSON = Path(__file__).resolve().parent.parent / "data" / "actions.json"
BASE_URL = "https://drawdown.org/explorer"

HEADERS = {"User-Agent": "HumanActionPrioritizer/1.0 (educational project)"}

# Solutions that Drawdown groups under a single parent page
PARENT_SLUGS = {
    "cement-production": "improve-cement-production",
    "coastal-wetlands": "protect-coastal-wetlands",
    "electric-bicycles": "mobilize-electric-bicycles",
    "forests": "protect-forests",
    "restore-forests": "restore-forests",
    "grasslands-savannas": "protect-grasslands-savannas",
    "landfill-management": "improve-landfill-management",
    "peatlands": "protect-peatlands",
    "recycling": "increase-recycling",
}


def slugify(action: str, solution: str) -> str:
    """Build the Drawdown URL slug from action + solution name."""
    # e.g. "Deploy" + "Alternative Insulation Materials" -> "deploy-alternative-insulation-materials"
    raw = f"{action} {solution}"
    slug = raw.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)  # remove special chars
    slug = re.sub(r"\s+", "-", slug)  # spaces to hyphens
    slug = re.sub(r"-+", "-", slug)  # collapse multiple hyphens
    return slug


def extract_text(html: str) -> str | None:
    """Extract the explanatory text content from a Drawdown solution page."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove nav, footer, scripts, styles, and interactive elements
    for tag in soup.find_all(["nav", "footer", "script", "style", "iframe", "svg"]):
        tag.decompose()

    # Look for the main content area
    main = soup.find("main") or soup.find("article") or soup

    # Collect all meaningful text paragraphs
    paragraphs = []
    for element in main.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = element.get_text(strip=True)
        if len(text) > 20:  # skip tiny fragments
            if element.name.startswith("h"):
                paragraphs.append(f"\n## {text}\n")
            else:
                paragraphs.append(text)

    content = "\n\n".join(paragraphs)
    # Only return if we got substantial content
    return content if len(content) > 200 else None


def load_actions() -> list[dict]:
    """Load the filtered actions from JSON."""
    with open(ACTIONS_JSON, encoding="utf-8") as f:
        return json.loads(f.read())


def scrape_all():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    actions = load_actions()
    success = 0
    failed = []

    for action_data in actions:
        action = action_data["action"]
        solution = action_data["solution"]
        slug = slugify(action, solution)
        filename = slug + ".txt"
        filepath = DATA_DIR / filename
        url = f"{BASE_URL}/{slug}"

        if filepath.exists():
            print(f"  Skipping {solution} (already exists)")
            success += 1
            continue

        # Try exact slug first, then fall back to parent slug
        urls_to_try = [url]
        for parent_key, parent_slug in PARENT_SLUGS.items():
            if parent_key in slug and slug != parent_slug:
                urls_to_try.append(f"{BASE_URL}/{parent_slug}")
                break

        resp = None
        for try_url in urls_to_try:
            print(f"  Fetching: {solution} -> {try_url}")
            try:
                resp = requests.get(try_url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
                break
            except requests.RequestException:
                resp = None
                continue

        if resp is None:
            print(f"  ERROR: All URLs failed for '{solution}'")
            failed.append(solution)
            continue

        text = extract_text(resp.text)
        if not text:
            print(f"  WARNING: No meaningful content for '{solution}'")
            failed.append(solution)
            continue

        header = f"# {action} {solution}\nSource: {url}\n\n"
        filepath.write_text(header + text, encoding="utf-8")
        success += 1
        time.sleep(1)  # be polite

    print(f"\nDone: {success} saved, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    scrape_all()
