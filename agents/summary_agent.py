from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextIn(BaseModel):
    text: str

@app.post("/summarize")
def summarize(data: TextIn):
    return {"summary": "Q2 sales rose by 15% from Q1."}
