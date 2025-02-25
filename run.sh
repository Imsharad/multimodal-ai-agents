#!/bin/bash

# Run frontend in background
cd livekit-frontend && pnpm dev &

# Run backend in foreground (so we can see logs and Ctrl+C both)
source venv/bin/activate && python main.py dev

# Cleanup background process when script exits
trap "kill $(jobs -p)" EXIT