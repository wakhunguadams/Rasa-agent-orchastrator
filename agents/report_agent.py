from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/generate-report")
def generate_report():
    return {"report": "Q2 sales increased by 15% compared to Q1."}
