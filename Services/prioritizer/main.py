from fastapi import FastAPI
from pydantic import BaseModel
import json


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
    with open("data/actions.json") as f:
        actions = f.read()
        actions = json.loads(actions)
        return {"actions": actions}



    return {"actions": []}

@app.post("/actions/{action_id}/explain")
def explain_action(action_id: int):
    return {"action_id": action_id, "explanation": "This is a placeholder explanation."}


@app.post("/actions/rank")
def rank_actions(user_profile: UserProfile):
    return {"ranked_actions": []}

