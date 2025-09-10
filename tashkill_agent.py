# @title Import necessary libraries
import os
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types 
import warnings
from dotenv import load_dotenv
from prompt import prompt

load_dotenv()
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)
MODEL_ = os.getenv('MODEL')
os.environ["GOOGLE_API_KEY"] = os.getenv('GEMINI_API_KEY')
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv('TARGET_FOLDER_PATH'))
REACT_MANAGE_PROJECT_MCP_PATH = os.getenv('REACT_MANAGE_PROJECT_MCP_PATH')

async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server."""
    toolset_file_system = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params = StdioServerParameters(
                command='npx', 
                args=["-y",
                    "@modelcontextprotocol/server-filesystem",
                    TARGET_FOLDER_PATH],
            ),
        )
    )
    toolset_manage_react_project = MCPToolset(
            connection_params = StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3',
                    args=[
                        REACT_MANAGE_PROJECT_MCP_PATH
                    ]
                ),
                timeout=20
            )
        )
    
    root_agent = LlmAgent(
        name = "app_developper_v1",
        model = MODEL_,
        description = "full stack web developper ",
        instruction = prompt,
        tools=[toolset_file_system, toolset_manage_react_project],
    )
    return root_agent, toolset_file_system, toolset_manage_react_project


async def async_main(query, session_service, artifacts_service, session):
    
    print(f"User Query: '{query}'")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    root_agent, toolset_file_system, toolset_manage_react_project = await get_agent_async()

    runner = Runner(
        app_name='mcp_filesystem_app',
        agent=root_agent,
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    print("Running agent...")
    events_async = runner.run_async(
        session_id=session.id, user_id=session.user_id, new_message=content
    )
    final_response_text = ""
    async for event in events_async:
        if event.is_final_response():
            if event.content and event.content.parts:
                try:
                    print(event.content.parts[0].text)
                except Exception as e:
                    print({'event': event, "error":str(e)})
                    
            elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                print(f"Agent escalated: {event.error_message or 'No specific message.'}")
            # Add more checks here if needed (e.g., specific error codes)
            try:
                texts = [p.text for p in event.content.parts if hasattr(p, "text")]
                final_response_text = "\n".join(t.strip() for t in texts if t)
                print(final_response_text)
                return final_response_text
            except Exception as e:
                print(str(e))
                return("done !")
    print("Closing MCP server connection...")
    await toolset_file_system.close()
    await toolset_manage_react_project.close()
    print("Cleanup complete.")

import traceback

async def run_agent(query, session_service, artifacts_service, session):
    try:
        return await async_main(query, session_service, artifacts_service, session)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
