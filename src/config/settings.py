"""Application settings and configuration"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    
    # API Keys
    gemini_api_key: str = os.getenv('GEMINI_API_KEY', '')
    
    # Models
    model: str = os.getenv('MODEL', 'gemini-1.5-flash')
    text_generation_model: str = os.getenv('TEXT_GENERATION_MODEL', 'gemini-1.5-flash')
    advanced_programming_model: str = os.getenv('ADVANCED_PROGRAMMING_MODEL', 'gemini-1.5-pro')
    # Paths
    target_folder_path: str = os.getenv('TARGET_FOLDER_PATH', './output')
    react_manage_project_mcp_path: str = os.getenv('REACT_MANAGE_PROJECT_MCP_PATH', './tools.py')
    parent_project_path: str = os.getenv('PARENT_PROJECT_PATH', './react_parent_project/tachkill-project-template')
    
    # Session Configuration
    app_name: str = "tashkil_coder"
    user_id: str = "12345"
    session_id: str = "123344"
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'logs.log')
    
    # MCP Configuration
    mcp_timeout: int = int(os.getenv('MCP_TIMEOUT', '120'))
    
    def __post_init__(self):
        """Set up environment variables after initialization"""
        if self.gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key
    
    @property
    def target_folder_absolute_path(self) -> str:
        """Get absolute path for target folder"""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', self.target_folder_path)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.__post_init__()
    return _settings