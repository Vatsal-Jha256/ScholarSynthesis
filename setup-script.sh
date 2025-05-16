#!/bin/bash

# Setup script for ScholarSynthesis (formerly LitReviewAgent)

# Check for Python 3.8+
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found Python $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv litreview_env
source litreview_env/bin/activate

# Install required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install -e .

# Create directories
echo "Creating directories..."
mkdir -p output
mkdir -p .cache

echo "Setup complete!"
echo
echo "To use ScholarSynthesis:"
echo "1. Activate the virtual environment:"
echo "   source litreview_env/bin/activate"
echo
echo "2. Run the agent with your paper details:"
echo "   litreview-agent --title \"Your Paper Title\" --abstract \"Your paper abstract\" --num_papers 15"
echo 
echo "3. For more options:"
echo "   litreview-agent --help"
