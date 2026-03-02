#!/usr/bin/env python3
import subprocess
import sys
import time
from typing import Sequence, Union

print("=" * 60)
print("FFPAS - Football Prediction System")
print("Complete System Startup")
print("=" * 60)

def run_command(description: str, command: Union[str, Sequence[str]]) -> int:
    print(f"\n{description}")
    print(f"Command: {command}")
    result = subprocess.run(command, shell=isinstance(command, str))
    if result.returncode != 0:
        print(f"Warning: {description} returned code {result.returncode}")
    return result.returncode

# Step 1: Clean duplicates
print("\n[1/4] Cleaning duplicate data...")
run_command("Cleaning duplicates", "python3 clean_duplicates.py")

# Step 2: Train model
print("\n[2/4] Training AI model...")
run_command("Training model", "python3 analyze_and_train_advanced.py")

# Step 3: Start backend
print("\n[3/4] Starting backend API...")
backend_process = subprocess.Popen(
    ["python3", "ai/auto_analyze.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
print(f"Backend started (PID: {backend_process.pid})")

# Step 4: Start frontend
print("\n[4/4] Starting frontend server...")
frontend_process = subprocess.Popen(
    ["python3", "-m", "http.server", "8080"],
    cwd="frontend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
print(f"Frontend started (PID: {frontend_process.pid})")

print("\n" + "=" * 60)
print("FFPAS System Started Successfully!")
print("=" * 60)
print(f"Backend API: Running (PID: {backend_process.pid})")
print(f"Frontend: http://localhost:8080")
print("\nPress Ctrl+C to stop all services")
print("=" * 60)

try:
    while True:
        time.sleep(1)
        # Check if processes are still running
        if backend_process.poll() is not None:
            print("\nWarning: Backend process stopped")
        if frontend_process.poll() is not None:
            print("\nWarning: Frontend process stopped")
except KeyboardInterrupt:
    print("\n\nStopping services...")
    backend_process.terminate()
    frontend_process.terminate()
    backend_process.wait()
    frontend_process.wait()
    print("All services stopped.")
    sys.exit(0)
