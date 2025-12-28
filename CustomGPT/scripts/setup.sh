#!/bin/bash

# Setup script for Srivatsav Job Search GPT
# This script sets up the environment and installs dependencies

set -e

echo "🚀 Setting up Srivatsav Job Search GPT Assistant..."
echo "=================================================="

# Check if Python 3.9+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.9+ is required but not installed."
    echo "Please install Python 3.9 or later and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ is required, but you have $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Check if data files exist
echo "🔍 Checking data files..."
if [ ! -f "data/resume.md" ]; then
    echo "⚠️  data/resume.md not found. Please add your resume."
fi

if [ ! -f "data/linkedin_profile.txt" ]; then
    echo "⚠️  data/linkedin_profile.txt not found. Please add your LinkedIn profile."
fi

if [ ! -f "data/roles_target_list.csv" ]; then
    echo "⚠️  data/roles_target_list.csv not found. Please add your target roles."
fi

# Check environment variables
echo "🔐 Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Please set it in your environment or .env file."
fi

# Make run script executable
chmod +x run.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your OpenAI API key: export OPENAI_API_KEY='your_key_here'"
echo "2. Add your data files to the data/ directory"
echo "3. Run the application: ./run.py"
echo ""
echo "Or activate the virtual environment and run:"
echo "source venv/bin/activate"
echo "python run.py"
echo ""
echo "Happy job searching! 🎯"
