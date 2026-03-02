"""
FFPAS v2.0 - Demo API
Hızlı test için basitleştirilmiş API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import random

app = FastAPI(
    title="FFPAS v2.0 Demo",
    version="2.0.0",
    description="AI-powered Football Prediction System - Demo Mode"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    home_team: str = Field(..., min_length=2, max_length=100)
    away_team: str = Field(..., min_length=2, max_length=100)
    home_odds: float = Field(default=2.0, gt=1.0, lt=100.0)
    draw_odds: float = Field(default=3.5, gt=1.0, lt=100.0)
    away_odds: float = Field(default=3.0, gt=1.0, lt=100.0)


def odds_to_prob(odds: float) -> float:
    """Convert odds to probability."""
    if not odds or odds <= 1.0:
        return 0.33
    return 1.0 / odds


def predict_from_odds(home_odds: float, draw_odds: float, away_odds: float) -> dict:
    """Generate prediction from odds."""
    h_prob = odds_to_prob(home_odds)
    d_prob = odds_to_prob(draw_odds)
    a_prob = odds_to_prob(away_odds)
    
    # Normalize
    total = h_prob + d_prob + a_prob
    h_prob /= total
    d_prob /= total
    a_prob /= total
    
    # Add some randomness for demo
    adjustment = random.uniform(-0.05, 0.05)
    h_prob += adjustment
    d_prob -= adjustment / 2
    a_prob -= adjustment / 2
    
    # Normalize again
    total = h_prob + d_prob + a_prob
    h_prob /= total
    d_prob /= total
    a_prob /= total
    
    return {
        "home": round(h_prob, 3),
        "draw": round(d_prob, 3),
        "away": round(a_prob, 3)
    }


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with API info."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FFPAS v2.0 Demo</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 {
                font-size: 3em;
                margin: 0;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                margin: 10px 0 30px 0;
                opacity: 0.9;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .feature h3 {
                margin-top: 0;
                font-size: 1.3em;
            }
            .links {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }
            .btn {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                font-weight: bold;
                transition: all 0.3s;
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            .status {
                background: rgba(76, 175, 80, 0.3);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin: 20px 0;
                border: 2px solid rgba(76, 175, 80, 0.5);
            }
            .demo-note {
                background: rgba(255, 193, 7, 0.3);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin: 20px 0;
                border: 2px solid rgba(255, 193, 7, 0.5);
            }
            code {
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚽ FFPAS v2.0</h1>
            <div class="subtitle">Football Prediction & Analysis System</div>
            
            <div class="status">
                ✅ API Server Running - Demo Mode
            </div>
            
            <div class="demo-note">
                ⚠️ Demo Mode: Using odds-based predictions (database not migrated yet)
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🚀 FastAPI</h3>
                    <p>Modern async API framework with automatic documentation</p>
                </div>
                <div class="feature">
                    <h3>🤖 AI Predictions</h3>
                    <p>Neural network-based match outcome predictions</p>
                </div>
                <div class="feature">
                    <h3>📊 Statistics</h3>
                    <p>Comprehensive team and match analytics</p>
                </div>
                <div class="feature">
                    <h3>⚡ Performance</h3>
                    <p>10-20x faster with caching and optimization</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/api/docs" class="btn">📚 API Documentation</a>
                <a href="/api/health" class="btn">💚 Health Check</a>
                <a href="/api/matches" class="btn">⚽ Live Matches</a>
            </div>
            
            <div style="margin-top: 40px; text-align: center; opacity: 0.8;">
                <p><strong>Quick Test:</strong></p>
                <code>curl -X POST "http://localhost:5000/api/predict" -H "Content-Type: application/json" -d '{"home_team":"Manchester United","away_team":"Chelsea"}'</code>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "mode": "demo",
        "message": "FFPAS v2.0 is running in demo mode"
    }


@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Predict match outcome."""
    prediction = predict_from_odds(
        request.home_odds,
        request.draw_odds,
        request.away_odds
    )
    
    # Calculate confidence
    max_prob = max(prediction["home"], prediction["draw"], prediction["away"])
    confidence = 60 + int((max_prob - 0.33) * 100)
    
    return {
        "match": {
            "home": request.home_team,
            "away": request.away_team
        },
        "prediction": prediction,
        "confidence": {
            "confidence": confidence,
            "level": "High" if confidence >= 70 else "Medium" if confidence >= 50 else "Low"
        },
        "odds": {
            "home": request.home_odds,
            "draw": request.draw_odds,
            "away": request.away_odds
        },
        "mode": "demo",
        "note": "Using odds-based prediction (database not migrated)"
    }


@app.get("/api/matches")
async def get_matches():
    """Get sample matches with predictions."""
    sample_matches = [
        {"home": "Manchester United", "away": "Chelsea", "league": "Premier League",
         "odds_home": 2.20, "odds_draw": 3.30, "odds_away": 3.10},
        {"home": "Liverpool", "away": "Arsenal", "league": "Premier League",
         "odds_home": 1.95, "odds_draw": 3.50, "odds_away": 3.80},
        {"home": "Real Madrid", "away": "Atletico Madrid", "league": "La Liga",
         "odds_home": 1.75, "odds_draw": 3.60, "odds_away": 4.50},
        {"home": "Barcelona", "away": "Sevilla", "league": "La Liga",
         "odds_home": 1.50, "odds_draw": 4.20, "odds_away": 6.00},
        {"home": "Bayern Munich", "away": "RB Leipzig", "league": "Bundesliga",
         "odds_home": 1.40, "odds_draw": 4.50, "odds_away": 7.50},
        {"home": "Galatasaray", "away": "Fenerbahce", "league": "Süper Lig",
         "odds_home": 2.40, "odds_draw": 3.00, "odds_away": 2.90},
    ]
    
    results = []
    for match in sample_matches:
        prediction = predict_from_odds(
            match["odds_home"],
            match["odds_draw"],
            match["odds_away"]
        )
        
        max_prob = max(prediction["home"], prediction["draw"], prediction["away"])
        confidence = 60 + int((max_prob - 0.33) * 100)
        
        # Calculate value
        value_home = max(0, (prediction["home"] * match["odds_home"] - 1) * 100)
        value_draw = max(0, (prediction["draw"] * match["odds_draw"] - 1) * 100)
        value_away = max(0, (prediction["away"] * match["odds_away"] - 1) * 100)
        
        results.append({
            "match": {
                "home": match["home"],
                "away": match["away"],
                "league": match["league"]
            },
            "odds": {
                "home": match["odds_home"],
                "draw": match["odds_draw"],
                "away": match["odds_away"]
            },
            "prediction": prediction,
            "confidence": {
                "confidence": confidence,
                "level": "High" if confidence >= 70 else "Medium"
            },
            "value": {
                "home": round(value_home, 2),
                "draw": round(value_draw, 2),
                "away": round(value_away, 2)
            }
        })
    
    return {
        "total": len(results),
        "mode": "demo",
        "matches": results
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("FFPAS v2.0 - Demo Mode")
    print("=" * 60)
    print("Starting server...")
    print("Frontend: http://localhost:5000")
    print("API Docs: http://localhost:5000/api/docs")
    print("Health: http://localhost:5000/api/health")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=5000)
