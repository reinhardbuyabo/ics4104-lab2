from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

SERVER_ID = os.environ.get("SERVER_ID", "[ID]")

class ServerResponse(BaseModel):
    message: str
    status: str

@app.get("/home", response_model=ServerResponse)
def home():
    return ServerResponse(
        message=f"Hello from Server: {SERVER_ID}",
        status="successful"
    )

@app.get("/heartbeat")
def heartbeat():
    return {}
