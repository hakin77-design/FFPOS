#!/bin/bash

set -e

cd ~/ffpas
source venv/bin/activate

echo "Installing AI modules..."

pip install \
    sentence-transformers \
    transformers \
    accelerate \
    datasets \
    optuna \
    gymnasium \
    stable-baselines3 \
    ta \
    yfinance \
    pyarrow \
    duckdb

echo "Creating AI folders..."

mkdir -p ai/models
mkdir -p ai/training
mkdir -p ai/prediction
mkdir -p ai/crawler
mkdir -p ai/features

echo "Creating crawler skeleton..."

cat > ai/crawler/google_crawler.py <<EOF
import requests
from bs4 import BeautifulSoup

def search_google(query):
    url = "https://www.google.com/search"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    results = []
    for g in soup.select("a"):
        href = g.get("href")
        if href and "http" in href:
            results.append(href)

    return results
EOF

echo "Creating Poisson model..."

cat > ai/models/poisson.py <<EOF
import numpy as np
from scipy.stats import poisson

def match_matrix(lam_home, lam_away, max_goals=6):
    matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            matrix[i,j] = poisson.pmf(i, lam_home) * poisson.pmf(j, lam_away)

    return matrix
EOF

echo "Creating neural model..."

cat > ai/models/neural.py <<EOF
import torch
import torch.nn as nn

class MatchNet(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n,128),
            nn.ReLU(),
            nn.Linear(128,64),
            nn.ReLU(),
            nn.Linear(64,3)
        )

    def forward(self,x):
        return self.net(x)
EOF

echo "Creating training script..."

cat > ai/training/train.py <<EOF
print("Training pipeline placeholder")
EOF

echo "AI INSTALL COMPLETE"
