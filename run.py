#!/usr/bin/env python3
"""
Launch script for the AI Documentation Assistant
"""

import os
import sys
import subprocess
from pathlib import Path

def create_missing_files():
    """Create any missing __init__.py files"""
    directories = ['agents', 'utils', 'orchestrator']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.write_text("# Auto-generated init file\n")
            print(f"Created {init_file}")

def check_requirements():
    """Check if all requirements are met"""
    required_packages = [
        'streamlit', 'langchain', 'langchain-openai', 'openai', 
        'textstat', 'weasyprint', 'beautifulsoup4', 'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("⚠️ OpenAI API key not configured")
        print("Please set your API key in the .env file or as an environment variable")
        return False
    return True

def test_imports():
    """Test if our modules can be imported"""
    try:
        from agents.documentation_analyzer import DocumentationAnalyzerAgent
        from orchestrator.agent_orchestrator import AgentOrchestrator
        from utils.content_scraper import ContentScraper
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main launch function"""
    print("🚀 Starting AI Documentation Assistant")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found. Make sure you're in the project directory.")
        sys.exit(1)
    
    # Create missing files
    create_missing_files()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Module import failed. Please check your installation.")
        sys.exit(1)
    
    # Check API key (warning only)
    if not check_api_key():
        print("You can still run the app and enter the API key in the sidebar.")
        print()
    
    # Launch Streamlit
    print("🌟 Launching Streamlit application...")
    print("The app will open in your default browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 40)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()