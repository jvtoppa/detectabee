#!/bin/bash

PIDS=()

cleanup() {
    echo -e "\n\n[System] Shutting down all processes..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
        fi
    done
    echo "[System] All processes stopped. Exiting."
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "[System] Starting all API and source processes..."

if [ -f "src/main.py" ]; then
    python3 src/main.py &
    PIDS+=($!)
    echo " -> Started src/main.py (PID: $!)"
else
    echo " -> [Warning] src/main.py not found."
fi

if [ -f "api/api.py" ]; then
    python3 api/api.py &
    PIDS+=($!)
    echo " -> Started api/api.py (PID: $!)"
else
    echo " -> [Warning] api/api.py not found."
fi

echo " -> Starting Uvicorn server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
PIDS+=($!)
echo " -> Started Uvicorn (PID: $!)"

echo -e "[System] All services running. Press Ctrl+C to stop everything.\n"

wait