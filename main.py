"""
Main entry point for Tashkil Coder
"""

import asyncio
import traceback
from google.genai import types

from src.utils import setup_logging
from src.services import create_session_manager


async def run_agent_async(
    query: str,
    session_manager=None
):
    """
    Run the agent with the given query
    
    Args:
        query: User input query
        session_manager: Optional session manager (will create if not provided)
        
    Returns:
        Agent response text
    """
    logger = setup_logging()
    
    try:
        # Create session manager if not provided
        if session_manager is None:
            session_manager = await create_session_manager()
        
        # Initialize runner
        runner = await session_manager.initialize_runner()
        
        # Create user message
        content = types.Content(
            role='user', 
            parts=[types.Part(text=query)]
        )
        
        logger.info(f"Processing query: {query}")
        
        # Run the agent
        events_async = runner.run_async(
            session_id=session_manager.session.id,
            user_id=session_manager.session.user_id,
            new_message=content
        )
                
        async for event in events_async:
            yield event
        
        # Cleanup
        await session_manager.cleanup()
        
        # return final_response_text or "Task completed successfully!"
        
    except Exception as e:
        logger.error(f"Error in run_agent_async: {e}")
        traceback.print_exc()
        # return f"An error occurred: {e}"


def run_agent(query: str, session_service=None, artifacts_service=None, session=None) -> str:
    """
    Synchronous wrapper for running the agent (for compatibility)
    
    Args:
        query: User input query
        session_service: Legacy parameter (ignored)
        artifacts_service: Legacy parameter (ignored) 
        session: Legacy parameter (ignored)
        
    Returns:
        Agent response text
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_agent_async(query))


if __name__ == "__main__":
    # Example usage
    test_query = "Create a simple todo app with React"
    result = run_agent(test_query)
    print(f"Result: {result}")