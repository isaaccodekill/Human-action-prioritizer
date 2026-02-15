import json
from importlib import resources

from fastapi import FastAPI
from pydantic import BaseModel


class UserProfile(BaseModel):
    city: str
    lifestyle: str
    transportation: str
    diet: str
    energy: str


app = FastAPI()

@app.get("/health")
def read_root():
    return {"status": "healthy"}


@app.get("/actions")
def get_actions():
    data_file = resources.files("prioritizer.data").joinpath("actions.json")
    actions = json.loads(data_file.read_text())
    return {"actions": actions}

@app.post("/actions/{action_id}/explain")
def explain_action(action_id: int):
    return {"action_id": action_id, "explanation": "This is a placeholder explanation."}


@app.post("/actions/rank")
def rank_actions(user_profile: UserProfile):
    return {"ranked_actions": []}

