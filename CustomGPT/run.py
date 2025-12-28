#!/usr/bin/env python3
"""
Main entry point for Srivatsav Job Search GPT
Run this script to start the Streamlit dashboard.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import streamlit
        import openai
        import langchain
        import faiss
        import pandas
        import plotly
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set."""
    # Check for either OpenRouter or OpenAI API key
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openrouter_key and not openai_key:
        print("❌ Missing required environment variables:")
        print("   Either OPENROUTER_API_KEY or OPENAI_API_KEY must be set")
        print("   Please set one of these variables or create a .env file")
        return False
    
    if openrouter_key:
        print("✅ OpenRouter API key detected")
    elif openai_key:
        print("✅ OpenAI API key detected")
    
    return True

def check_data_directory():
    """Check if data directory exists and has required files."""
    data_dir = Path("data")
    required_files = ["resume.md", "linkedin_profile.txt", "roles_target_list.csv"]
    
    if not data_dir.exists():
        print("❌ Data directory not found")
        return False
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required data files: {', '.join(missing_files)}")
        print("Please ensure all data files are in the data/ directory")
        return False
    
    print("✅ Data directory and files are ready")
    return True

def main():
    """Main function to run the application."""
    print("🚀 Starting Srivatsav Job Search GPT Assistant...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\nTo set up environment variables:")
        print("1. Copy env.example to .env")
        print("2. Edit .env with your API key (OpenRouter or OpenAI)")
        print("3. Run: source .env (or set variables manually)")
        print("\nFor OpenRouter (recommended):")
        print("   export OPENROUTER_API_KEY='your_openrouter_key_here'")
        print("\nFor OpenAI:")
        print("   export OPENAI_API_KEY='your_openai_key_here'")
        sys.exit(1)
    
    # Check data directory
    if not check_data_directory():
        print("\nTo set up data files:")
        print("1. Ensure data/ directory exists")
        print("2. Add your resume.md, linkedin_profile.txt, and roles_target_list.csv")
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting dashboard...")
    print("=" * 50)
    
    # Run Streamlit dashboard
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ui/dashboard.py", 
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
