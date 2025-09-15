"""
Legacy test module - now uses the new modular structure
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import run_agent_async
from src.services import create_session_manager
from src.utils import setup_logging

import traceback
import asyncio

# Setup logging
logger = setup_logging()


# Legacy compatibility - agents are now created in the modular structure

async def run_agent(query, session_service=None, artifacts_service=None, session=None):
    """
    Legacy compatibility function - now uses the new modular structure
    """
    try:
        return await run_agent_async(query)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
        return f"Error: {str(e)}"
