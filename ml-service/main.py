from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "ML Service Running"}

@app.post("/predict")
def predict(data: dict):
    income = data.get("income", 0)
    
    # simple dummy logic
    if income < 250000:
        return {"eligible": True}
    else:
        return {"eligible": False}