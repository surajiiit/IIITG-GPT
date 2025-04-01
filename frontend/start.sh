# start.sh
# Shell script to start the FastAPI server

#!/bin/bash

# Activate virtual environment if needed (Uncomment and modify if using a venv)
# source venv/bin/activate

# Run FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
