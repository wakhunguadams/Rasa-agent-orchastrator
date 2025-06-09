from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class EmailIn(BaseModel):
    body: str

@app.post("/send-email")
def send_email(data: EmailIn):
    print(f"Email sent: {data.body}")
    return {"status": "sent"}
