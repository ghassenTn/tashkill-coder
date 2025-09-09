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

load_dotenv()
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)
MODEL_ = os.getenv('model')
os.environ["GOOGLE_API_KEY"] = os.getenv('GEMINI_API_KEY')
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv('TARGET_FOLDER_PATH'))
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
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
      ),
      
  ) 

  root_agent = LlmAgent(
    name = "app_developper_v1",
    model = MODEL_,
    description = "full stack web developper ",
    instruction = "You are full stack web developper creator and enhanceur"
                  "When u receive the idea of an app u must develop it using a old school style"
                  "any operation in the project must be passed from the provided tools",
      tools=[toolset_file_system],
  )
  return root_agent, toolset_file_system


async def async_main(query, session_service, artifacts_service, session):
    
    print(f"User Query: '{query}'")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    root_agent, toolset_file_system = await get_agent_async()

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
                # Assuming text response in the first part
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
    print("Closing MCP server connection...")
    await toolset_file_system.close()
    print("Cleanup complete.")

import traceback

async def run_agent(query, session_service, artifacts_service, session):
    try:
        return await async_main(query, session_service, artifacts_service, session)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
