"""Session management service"""

import logging
from typing import Optional
from pydantic import BaseModel

from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner

from ..config import get_settings
from ..agents import create_dev_flow_agent


logger = logging.getLogger(__name__)


class SessionManager(BaseModel):
    """Manages session, artifacts, and runner for the application"""
    
    session_service: InMemorySessionService
    artifacts_service: InMemoryArtifactService
    session: object
    runner: Optional[Runner] = None
    
    model_config = {"arbitrary_types_allowed": True}
    
    async def initialize_runner(self) -> Runner:
        """
        Initialize the runner with the dev flow agent
        
        Returns:
            Configured Runner instance
        """
        if self.runner is None:
            settings = get_settings()
            dev_agent = create_dev_flow_agent()
            
            self.runner = Runner(
                app_name=settings.app_name,
                agent=dev_agent,
                artifact_service=self.artifacts_service,
                session_service=self.session_service,
            )
            
            logger.info("Runner initialized successfully")
        
        return self.runner
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.runner and hasattr(self.runner, 'agent'):
                # The agent cleanup is handled in the orchestrator
                pass
            logger.info("Session cleanup completed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


async def create_session_manager() -> SessionManager:
    """
    Create and configure a session manager
    
    Returns:
        Configured SessionManager instance
    """
    settings = get_settings()
    
    # Create services
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    
    # Create session
    session = await session_service.create_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id
    )
    
    logger.info(f"Session created: {settings.session_id}")
    
    return SessionManager(
        session_service=session_service,
        artifacts_service=artifacts_service,
        session=session
    )