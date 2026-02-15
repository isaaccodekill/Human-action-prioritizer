import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent / "data"
scores_path = data_dir / "synthetic_action_pair_scores.json"

with open(scores_path, "r") as f:
    scored_pairs = json.load(f)

mirrored = []
for pair in scored_pairs:
    # keep the original
    mirrored.append(pair)
    # add the reversed: swap action_a and action_b, flip the score
    mirrored.append({
        "action_a": pair["action_b"],
        "action_b": pair["action_a"],
        "user_profile": pair["user_profile"],
        "score": 1 if pair["score"] == 0 else 0
    })

with open(scores_path, "w") as f:
    json.dump(mirrored, f, indent=2)

print(f"Original: {len(scored_pairs)} pairs")
print(f"Mirrored: {len(mirrored)} pairs")
