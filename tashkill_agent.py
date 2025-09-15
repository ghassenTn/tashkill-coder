"""
Tashkill Agent - Legacy compatibility module
This module now uses the new modular structure for better maintainability.
"""

# Import from new modular structure
from main import run_agent_async, run_agent
from src.config import get_settings
from src.agents import create_dev_flow_agent
from src.tools import create_filesystem_toolset, create_react_project_toolset
from src.services import create_session_manager
from src.utils import setup_logging

# Legacy compatibility
async def get_custom_agent_async():
    """
    Legacy function - now uses modular structure
    Creates agents using the new modular approach
    """
    # Create agents using new structure
    dev_agent = create_dev_flow_agent()
    toolset_file_system = create_filesystem_toolset()
    toolset_manage_react_project = create_react_project_toolset()
    
    return dev_agent, toolset_file_system, toolset_manage_react_project


async def async_main(query, session_service=None, artifacts_service=None, session=None):
    """
    Legacy function - now uses modular structure
    """
    return await run_agent_async(query)


# Export the main functions for backward compatibility
__all__ = ["run_agent", "async_main", "get_custom_agent_async"]