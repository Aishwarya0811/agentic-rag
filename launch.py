#!/usr/bin/env python3
"""
Launch script for the Advanced RAG System.
Provides easy commands to start, test, and manage the system.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    print("🔍 Checking requirements...")
    
    # Check if requirements.txt exists
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    # Try to import key dependencies
    missing_deps = []
    
    try:
        import streamlit
        print("   ✓ Streamlit available")
    except ImportError:
        missing_deps.append("streamlit")
    
    try:
        import chromadb
        print("   ✓ ChromaDB available")
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        import openai
        print("   ✓ OpenAI available")
    except ImportError:
        missing_deps.append("openai")
    
    try:
        import agents
        print("   ✓ OpenAI Agents SDK available")
    except ImportError:
        missing_deps.append("openai-agents")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All requirements satisfied!")
    return True

def check_environment():
    """Check environment configuration."""
    print("🔍 Checking environment configuration...")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            print("⚠️  .env file not found, but .env.example exists")
            print("💡 Copy .env.example to .env and add your OpenAI API key")
        else:
            print("❌ No .env file or .env.example found")
        return False
    
    # Check for OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Add your OpenAI API key to the .env file")
        return False
    
    if api_key.startswith("sk-") and len(api_key) > 40:
        print("✅ OpenAI API key configured")
        return True
    else:
        print("⚠️  OpenAI API key format seems incorrect")
        print("   Expected format: sk-...")
        return False

def install_requirements():
    """Install requirements using pip."""
    print("📦 Installing requirements...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def run_tests():
    """Run the comprehensive test suite."""
    print("🧪 Running system tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                               capture_output=False, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ test_system.py not found")
        return False

def start_fastapi():
    """Start the FastAPI application."""
    print("🚀 Starting FastAPI application...")
    
    # Check if fastapi_app.py exists
    app_file = Path("fastapi_app.py")
    if not app_file.exists():
        print("❌ fastapi_app.py not found!")
        return False
    
    try:
        print("🌐 FastAPI server will be available at:")
        print("   - Web Interface: http://localhost:8000")
        print("   - API Documentation: http://localhost:8000/api/docs")
        print("   - Press Ctrl+C to stop")
        
        # Start FastAPI
        subprocess.run([sys.executable, "fastapi_app.py"], check=False)
        return True
    except KeyboardInterrupt:
        print("\n👋 FastAPI application stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")
        return False

def start_streamlit():
    """Start the Streamlit application."""
    print("🚀 Starting Streamlit application...")
    
    # Check if streamlit_app.py exists
    app_file = Path("streamlit_app.py")
    if not app_file.exists():
        print("❌ streamlit_app.py not found!")
        return False
    
    try:
        print("🌐 Streamlit will be available at: http://localhost:8501")
        print("   - Press Ctrl+C to stop")
        
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], 
                      check=False)
        return True
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return False

def create_env_file():
    """Create a .env file from template."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Cancelled")
            return False
    
    if env_example.exists():
        # Copy from example
        with open(env_example, 'r') as src:
            content = src.read()
        
        with open(env_file, 'w') as dst:
            dst.write(content)
        
        print("✅ Created .env file from template")
        print("💡 Don't forget to add your OpenAI API key!")
        return True
    else:
        # Create basic .env file
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        print("✅ Created basic .env file")
        print("💡 Add your OpenAI API key to the .env file")
        return True

def setup_system():
    """Complete system setup."""
    print("🔧 Setting up Advanced RAG System...")
    print("=" * 50)
    
    # Create .env file if needed
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating environment file...")
        create_env_file()
    
    # Install requirements
    if not check_requirements():
        print("📦 Installing requirements...")
        if not install_requirements():
            print("❌ Setup failed during requirements installation")
            return False
    
    # Check environment
    if not check_environment():
        print("⚠️  Environment configuration incomplete")
        print("💡 Please add your OpenAI API key to the .env file and run setup again")
        return False
    
    print("\n✅ System setup complete!")
    print("🚀 You can now run:")
    print("   - python launch.py start (FastAPI web interface)")
    print("   - python launch.py streamlit (Alternative Streamlit interface)")
    return True

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description="Advanced RAG System Launcher")
    parser.add_argument("command", choices=["setup", "test", "start", "fastapi", "streamlit", "check", "install"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    
    print("🤖 Advanced RAG System Launcher")
    print("=" * 40)
    
    if args.command == "setup":
        success = setup_system()
        sys.exit(0 if success else 1)
    
    elif args.command == "install":
        success = install_requirements()
        sys.exit(0 if success else 1)
    
    elif args.command == "check":
        deps_ok = check_requirements()
        env_ok = check_environment()
        success = deps_ok and env_ok
        
        if success:
            print("\n✅ System is ready to use!")
        else:
            print("\n❌ System needs configuration")
            print("💡 Run: python launch.py setup")
        
        sys.exit(0 if success else 1)
    
    elif args.command == "test":
        if not check_requirements():
            print("❌ Cannot run tests - missing requirements")
            sys.exit(1)
        
        success = run_tests()
        sys.exit(0 if success else 1)
    
    elif args.command == "start" or args.command == "fastapi":
        # Pre-flight checks
        if not check_requirements():
            print("❌ Cannot start - missing requirements")
            print("💡 Run: python launch.py setup")
            sys.exit(1)
        
        if not check_environment():
            print("❌ Cannot start - environment not configured")
            print("💡 Run: python launch.py setup")
            sys.exit(1)
        
        # Start FastAPI (default)
        success = start_fastapi()
        sys.exit(0 if success else 1)
    
    elif args.command == "streamlit":
        # Pre-flight checks
        if not check_requirements():
            print("❌ Cannot start - missing requirements")
            print("💡 Run: python launch.py setup")
            sys.exit(1)
        
        if not check_environment():
            print("❌ Cannot start - environment not configured")
            print("💡 Run: python launch.py setup")
            sys.exit(1)
        
        # Start Streamlit
        success = start_streamlit()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()