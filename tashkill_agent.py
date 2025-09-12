# @title Import necessary libraries
import os
import asyncio
from typing import AsyncGenerator
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent
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

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
# إضافة أي imports لازمة للـ tools MCP إلخ

async def get_custom_agent_async():
    """Creates a custom agent with specific orchestration logic."""
    # تعريف sub-agents
    app_requirements_generator_agent = LlmAgent(
        name='app_requirements_generator_agent',
        model=MODEL_,
        description='application requirements generator',
        instruction='''You are to analyze the idea and generate coherent, complete requirements.''',
        output_key='requirements'
    )
    app_design_generator_agent = LlmAgent(
        name='app_design_generator_agent',
        model=MODEL_,
        description='application design generator',
        instruction='''Based on generated requirements, produce a structured design document.''',
        output_key='design'
    )
    app_tasks_generator_agent = LlmAgent(
        name='app_tasks_generator_agent',
        model=MODEL_,
        description='application tasks generator',
        instruction='''From design, list actionable development tasks in logical order.''',
        output_key='tasks'
    )
    toolset_file_system = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx', 
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    TARGET_FOLDER_PATH
                ],
            ),
        )
    )
    toolset_manage_react_project = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='python3',
                args=[
                    REACT_MANAGE_PROJECT_MCP_PATH
                ]
            ),
            timeout=20
        )
    )
    app_developer_agent = LlmAgent(
        name='app_developer_agent',
        model=MODEL_,
        description='full stack web developer implementing code',
        instruction='''You are a full stack developer. Use the outputs (requirements, design, tasks) to create code. Use the filesystem and project management tools.''',
        output_key='code'
        # تخصيص الأدوات
    )

    # إنشاء custom orchestrator agent
    class AppOrchestratorAgent(BaseAgent):
        # تعريف الحقول لي استعملهم
        requirements_agent: LlmAgent
        design_agent: LlmAgent
        tasks_agent: LlmAgent
        developer_agent: LlmAgent

        # تفعيل types_ALLOW إذا يلزم
        model_config = {"arbitrary_types_allowed": True}

        def __init__(self,
                     name: str,
                     requirements_agent: LlmAgent,
                     design_agent: LlmAgent,
                     tasks_agent: LlmAgent,
                     developer_agent: LlmAgent):
            # تحديد sub_agents لإعلام الـ framework
            sub_agents_list = [
                requirements_agent,
                design_agent,
                tasks_agent,
                developer_agent
            ]
            super().__init__(
                name=name,
                description="Orchestrates requirement → design → tasks → coding",
                requirements_agent=requirements_agent,
                design_agent=design_agent,
                tasks_agent=tasks_agent,
                developer_agent=developer_agent,
                sub_agents=sub_agents_list
            )

        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            # المرحلة 1: توليد requirements
            async for event in self.requirements_agent.run_async(ctx):
                yield event
            # ممكن تتحقق إذا requirements خرجت بنجاح
            if 'requirements' not in ctx.session.state or not ctx.session.state['requirements']:
                # لو فشل، نوقف
                return

            # المرحلة 2: design
            async for event in self.design_agent.run_async(ctx):
                yield event
            if 'design' not in ctx.session.state or not ctx.session.state['design']:
                return

            # المرحلة 3: tasks
            async for event in self.tasks_agent.run_async(ctx):
                yield event
            if 'tasks' not in ctx.session.state or not ctx.session.state['tasks']:
                return

            # المرحلة 4: developer (الكود الفعلي)
            async for event in self.developer_agent.run_async(ctx):
                yield event
            # ممكن تزيد مرحلة تحقق إضافية أو تعديل حسب الحالة إذا يلزم

    # instantiate orchestrator with sub-agents
    orchestrator = AppOrchestratorAgent(
        name='app_orchestrator_agent',
        requirements_agent=app_requirements_generator_agent,
        design_agent=app_design_generator_agent,
        tasks_agent=app_tasks_generator_agent,
        developer_agent=app_developer_agent
    )

    return orchestrator, toolset_file_system, toolset_manage_react_project



async def async_main(query, session_service, artifacts_service, session):
    
    print(f"User Query: '{query}'")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    root_agent, toolset_file_system, toolset_manage_react_project = await get_custom_agent_async()

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
