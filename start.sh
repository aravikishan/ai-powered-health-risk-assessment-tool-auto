#!/bin/bash
set -e
echo "Starting AI-Powered Health Risk Assessment Tool..."
uvicorn app:app --host 0.0.0.0 --port 9098 --workers 1
