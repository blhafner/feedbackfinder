#!/bin/bash
# Helper script to run win8.py with the correct Python environment

cd "$(dirname "$0")"
source venv/bin/activate
python win8.py

