#!/bin/bash
# FFPAS Complete System Startup Script

echo "=========================================="
echo "FFPAS - Football Prediction System"
echo "Complete System Startup"
echo "=========================================="

# 1. Clean duplicates
echo ""
echo "[1/4] Cleaning duplicate data..."
python3 clean_duplicates.py

# 2. Train/Update AI model
echo ""
echo "[2/4] Training AI model with all data..."
python3 analyze_and_train_advanced.py

# 3. Start backend API
echo ""
echo "[3/4] Starting backend API server..."
cd ai
python3 auto_analyze.py &
BACKEND_PID=$!
cd ..

# 4. Start frontend server
echo ""
echo "[4/4] Starting frontend server..."
cd frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "FFPAS System Started Successfully!"
echo "=========================================="
echo "Backend API: Running (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
