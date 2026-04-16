from fastapi import FastAPI
from pydantic import BaseModel
from services.pipeline_service import process_query

app = FastAPI()

# Request schema
class User(BaseModel):
    income: int
    occupation: str
    documents: list

class QueryRequest(BaseModel):
    query: str
    user: User

# API route
@app.post("/process")
def process(req: QueryRequest):
    result = process_query(req.query, req.user.dict())
    return result


@app.get("/")
def root():
    return {"message": "ML Service Running"}