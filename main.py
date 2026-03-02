from fastapi import FastAPI
from fastapi.responses import FileResponse
from ai.prediction.engine import predict_match

app = FastAPI()


@app.get("/")
def home():
    return FileResponse("ui/index.html")


@app.post("/predict")
def predict(data: dict):

    home = data.get("home")
    away = data.get("away")

    probs, pred = predict_match(home, away)

    return {
        "home": home,
        "away": away,
        "prob_home": probs["home"],
        "prob_draw": probs["draw"],
        "prob_away": probs["away"],
        "prediction": pred
    }
