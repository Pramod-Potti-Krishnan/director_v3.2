#!/usr/bin/env python
"""
Test script to verify all imports work correctly in the standalone Director Agent.
"""
import sys
import os

# Add the director_agent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing Director Agent imports...")
    print("-" * 50)

    errors = []

    # Test main module
    try:
        import main
        print("✓ main.py imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import main.py: {e}")
        errors.append(str(e))

    # Test config
    try:
        from config import settings
        print("✓ config.settings imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import config.settings: {e}")
        errors.append(str(e))

    # Test agents
    try:
        from src.agents import director
        print("✓ src.agents.director imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.agents.director: {e}")
        errors.append(str(e))

    try:
        from src.agents import intent_router
        print("✓ src.agents.intent_router imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.agents.intent_router: {e}")
        errors.append(str(e))

    # Test handlers
    try:
        from src.handlers import websocket
        print("✓ src.handlers.websocket imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.handlers.websocket: {e}")
        errors.append(str(e))

    # Test models
    try:
        from src.models import agents
        print("✓ src.models.agents imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.models.agents: {e}")
        errors.append(str(e))

    try:
        from src.models import session
        print("✓ src.models.session imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.models.session: {e}")
        errors.append(str(e))

    try:
        from src.models import websocket_messages
        print("✓ src.models.websocket_messages imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.models.websocket_messages: {e}")
        errors.append(str(e))

    # Test storage
    try:
        from src.storage import supabase
        print("✓ src.storage.supabase imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.storage.supabase: {e}")
        errors.append(str(e))

    # Test utils
    try:
        from src.utils import logger
        print("✓ src.utils.logger imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.utils.logger: {e}")
        errors.append(str(e))

    try:
        from src.utils import session_manager
        print("✓ src.utils.session_manager imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.utils.session_manager: {e}")
        errors.append(str(e))

    # Test workflows
    try:
        from src.workflows import state_machine
        print("✓ src.workflows.state_machine imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import src.workflows.state_machine: {e}")
        errors.append(str(e))

    print("-" * 50)

    if errors:
        print(f"\n❌ {len(errors)} import error(s) found:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All imports successful!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: python main.py")
        return True

def test_env():
    """Check if .env file exists and has required variables."""
    print("\n" + "=" * 50)
    print("Checking environment configuration...")
    print("-" * 50)

    env_file = os.path.join(os.path.dirname(__file__), '.env')

    if not os.path.exists(env_file):
        print("⚠️  No .env file found!")
        print("   Copy .env.example to .env and add your API keys:")
        print("   cp .env.example .env")
        return False

    print("✓ .env file exists")

    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    optional_vars = ['GOOGLE_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']

    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
            print(f"✗ {var} is not set")
        else:
            print(f"✓ {var} is configured")

    ai_keys_found = False
    for var in optional_vars:
        if os.getenv(var):
            print(f"✓ {var} is configured")
            ai_keys_found = True
        else:
            print(f"○ {var} is not set (optional)")

    if not ai_keys_found:
        print("\n⚠️  No AI API keys found!")
        print("   At least one AI service key is required:")
        print("   - GOOGLE_API_KEY")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY")
        return False

    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        return False

    print("\n✅ Environment configuration is valid!")
    return True

if __name__ == "__main__":
    print("Director Agent - Import and Configuration Test")
    print("=" * 50)

    imports_ok = test_imports()
    env_ok = test_env()

    print("\n" + "=" * 50)
    if imports_ok and env_ok:
        print("🎉 All checks passed! The Director Agent is ready to run.")
        print("\nStart the server with:")
        print("  python main.py")
    else:
        print("⚠️  Some issues need to be resolved before running the agent.")
        sys.exit(1)