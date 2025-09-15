"""MCP (Model Context Protocol) tools configuration"""

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from ..config import get_settings


def create_filesystem_toolset() -> MCPToolset:
    """
    Create MCP toolset for filesystem operations
    
    Returns:
        Configured MCPToolset for filesystem operations
    """
    settings = get_settings()
    
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    settings.target_folder_absolute_path
                ],
            ),
            timeout=settings.mcp_timeout
        )
    )


def create_react_project_toolset() -> MCPToolset:
    """
    Create MCP toolset for React project management
    
    Returns:
        Configured MCPToolset for React project operations
    """
    settings = get_settings()
    
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='python3',
                args=[settings.react_manage_project_mcp_path]
            ),
            timeout=settings.mcp_timeout
        )
    )