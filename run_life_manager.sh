#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Run the Life Manager script using uv
uv run python src/life_manager.py
