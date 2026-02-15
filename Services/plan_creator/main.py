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


@app.post("/plans/generate")
def generate_plan(user_profile: UserProfile):
    return {"plan": "This is a placeholder plan."}

@app.get("/plans/{plan_id}/")
def explain_plan(plan_id: int):
    return {"plan_id": plan_id, "explanation": "This is a placeholder explanation."}