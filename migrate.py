#!/usr/bin/env python3
"""
Migration script for Tashkil Coder modular refactoring
Helps users transition from old structure to new modular structure
"""

import os
import sys
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pydantic
        import dotenv
        print("✅ Dependencies check passed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def check_environment():
    """Check environment configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("Creating sample .env file...")
        
        sample_env = """# Tashkil Coder Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL=gemini-1.5-flash
TEXT_GENERATION_MODEL=gemini-1.5-flash
ADVANCED_PROGRAMMING_MODEL=gemini-1.5-pro
TARGET_FOLDER_PATH=./output
REACT_MANAGE_PROJECT_MCP_PATH=./tools.py
PARENT_PROJECT_PATH=./react_parent_project/tachkill-project-template
LOG_LEVEL=INFO
MCP_TIMEOUT=120
"""
        
        with open('.env', 'w') as f:
            f.write(sample_env)
        
        print("📝 Sample .env file created. Please update with your API keys.")
        return False
    else:
        print("✅ .env file found")
        return True


def test_new_structure():
    """Test if the new modular structure works"""
    try:
        from src.config import get_settings
        settings = get_settings()
        print("✅ Configuration module working")
        
        from src.utils import setup_logging
        logger = setup_logging()
        print("✅ Logging module working")
        
        from src.agents import create_specialized_agents
        print("✅ Agents module working")
        
        from src.tools import create_filesystem_toolset
        print("✅ Tools module working")
        
        from src.services import create_session_manager
        print("✅ Services module working")
        
        print("✅ All modules loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing new structure: {e}")
        return False


def backup_old_files():
    """Backup old files before migration"""
    backup_dir = Path('backup_old_structure')
    if backup_dir.exists():
        print("⚠️  Backup directory already exists")
        return
    
    backup_dir.mkdir()
    
    # Files to backup
    old_files = ['tashkill_agent.py', 'tests/test.py', 'app.py']
    
    for file_path in old_files:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir / Path(file_path).name)
            print(f"📦 Backed up {file_path}")
    
    print(f"✅ Backup created in {backup_dir}")


def run_migration():
    """Run the complete migration process"""
    print("🚀 Starting Tashkil Coder Migration to Modular Structure")
    print("=" * 60)
    
    # Step 1: Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Step 2: Check environment
    print("\n2. Checking environment configuration...")
    env_ok = check_environment()
    
    # Step 3: Test new structure
    print("\n3. Testing new modular structure...")
    if not test_new_structure():
        return False
    
    # Step 4: Create backup
    print("\n4. Creating backup of old files...")
    backup_old_files()
    
    # Step 5: Final check
    print("\n5. Running final compatibility test...")
    try:
        from main import run_agent
        print("✅ Legacy compatibility maintained")
    except Exception as e:
        print(f"❌ Legacy compatibility issue: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with proper API keys if needed")
    print("2. Test the application: streamlit run app.py")
    print("3. Check the new README_NEW.md for detailed documentation")
    print("4. Old files are backed up in 'backup_old_structure/' directory")
    
    if not env_ok:
        print("\n⚠️  Don't forget to update your .env file with proper values!")
    
    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)