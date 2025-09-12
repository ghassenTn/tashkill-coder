import logging
import os
from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.tools import AgentTool
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.runners import Runner
from google.adk.events import Event
from dotenv import load_dotenv
import traceback
import json

load_dotenv()

# --- Constants ---
APP_NAME = "dev_app"
USER_ID = "12345"
SESSION_ID = "123344"
TEXT_GENERATION_MODEL = os.getenv('TEXT_GENERATION_MODEL')
ADVANCED_PROGRAMMING_MODEL = os.getenv('ADVANCED_PROGRAMMING_MODEL')
TARGET_FOLDER_PATH = os.getenv('TARGET_FOLDER_PATH')
# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Custom Orchestrator Agent ---
class DevFlowAgent(BaseAgent):
    """
    Custom agent for a software development workflow.
    """

    requirements_agent: LlmAgent
    design_agent: LlmAgent
    tasks_agent: LlmAgent
    responsable_agent: LlmAgent 
    toolset_file_system: MCPToolset
    model_config = {"arbitrary_types_allowed": True}


    def __init__(
        self,
        name: str,
        requirements_agent: LlmAgent,
        design_agent: LlmAgent,
        tasks_agent: LlmAgent,
        responsable_agent: LlmAgent,
        toolset_file_system: MCPToolset

    ):
        

        sub_agents_list = [responsable_agent]

        super().__init__(
            name=name,
            requirements_agent=requirements_agent,
            design_agent=design_agent,
            tasks_agent=tasks_agent,
            responsable_agent=responsable_agent,
            toolset_file_system=toolset_file_system,
            sub_agents=sub_agents_list,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            logger.info(f"[{self.name}] Starting development workflow.")
            async for event in self.responsable_agent.run_async(ctx):
                logger.info(
                    f"[{self.name}] Event from DevWorkflow: "
                    f"{event.model_dump_json(indent=2, exclude_none=True)}"
                )
                yield event
            logger.info(f"[{self.name}] Workflow finished.")
            if self.toolset_file_system:
                await self.toolset_file_system.close()
            return
        except Exception as e:
            logger.error(f"Error in DevFlowAgent: {e}")
            traceback.print_exc()
            if self.toolset_file_system:
                await self.toolset_file_system.close()
            raise e
# --- Define the individual LLM agents ---


toolset_file_system = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            # Replace 'npx' with the full path
            command='/home/ghassen/.nvm/versions/node/v20.18.1/bin/npx', 
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                TARGET_FOLDER_PATH
            ],
        ),
        timeout=120
    )
)

requirements_agent = LlmAgent(
    name="RequirementsAgent",
    model=TEXT_GENERATION_MODEL,
    instruction='''You are a software analyst. Take the user idea and generate clear, structured functional and non-functional requirements.'''
                "u must generate ur work and make it in file named requirements.md using your tool for u can create and write files",
    tools=[toolset_file_system],
    input_schema=None,
    output_key="requirements_doc",
)

design_agent = LlmAgent(
    name="DesignAgent",
    model=TEXT_GENERATION_MODEL,
    instruction='''You are a system architect. Based on the requirements, produce a high-level system design: architecture, components, and data flow.'''
                    "u must generate ur work and make it in file named design.md using your tool for u can create and write files",
    tools=[toolset_file_system],
    input_schema=None,
    output_key="design_doc",
)

tasks_agent = LlmAgent(
    name="TasksAgent",
    model=TEXT_GENERATION_MODEL,
    instruction='''You are a project planner. From the system design, list actionable development tasks in a logical order (like a backlog).'''
                    "u must generate ur work and make it in file named tasks.md using your tool for u can create and write files",
    tools=[toolset_file_system],
    input_schema=None,
    output_key="tasks_list",
)

responsable_agent = LlmAgent(
    name = 'FullStackDeveloperAgent',
    model = ADVANCED_PROGRAMMING_MODEL,
    instruction = f"""
        You are a full stack  developer responsable for genrate app depend on user idea
        You have the following agents tools at your disposal:
            - RequirementsAgent: generates clear, structured functional and non-functional requirements from the user idea.
            - DesignAgent: produces a high-level system design based on the requirements.
            - TasksAgent: lists actionable development tasks from the system design.
        En the development processe u must update the tasks.md by adding mark for the completed tasks every when u complete a task 
        For the integration with the filesystem tool u must use this allowed path dir :{TARGET_FOLDER_PATH}
    """,
                  
    tools = [

            AgentTool(agent=requirements_agent),
            AgentTool(agent=design_agent),
            AgentTool(agent=tasks_agent),
            toolset_file_system,
        ]
)

# --- Create the custom agent instance ---
dev_flow_agent = DevFlowAgent(
    name="AppDevOrchestrator",
    requirements_agent=requirements_agent,
    design_agent=design_agent,
    tasks_agent=tasks_agent,
    responsable_agent = responsable_agent,
    toolset_file_system = toolset_file_system
)

# --- Setup Session and Runner ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=dev_flow_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return session_service, runner


# --- Function to Interact with the Agent ---
async def call_agent_async(user_input_topic: str, session_service, artifacts_service, session):
    runner = Runner(
        agent=dev_flow_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    current_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"Updated session state topic to: {user_input_topic}")

    content = types.Content(
        role="user", parts=[types.Part(text=f"{user_input_topic}")]
    )
    events = runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    )

    final_response = ""
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(
                f"Potential final response from [{event.author}]: "
                f"{event.content.parts[0].text}"
            )
            final_response += event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("Final Session State:")
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")
    return final_response


# --- Run Agent Safely ---
async def run_agent(query, session_service, artifacts_service, session):
    try:
        return await call_agent_async(query, session_service, artifacts_service, session)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
