"""Specialized agent implementations"""

from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

from .base import AgentInputSchemas
from ..config import get_settings
from ..tools import create_filesystem_toolset


def create_specialized_agents() -> Dict[str, Any]:
    """
    Create all specialized agents for the development workflow
    """
    settings = get_settings()
    toolset_file_system = create_filesystem_toolset()
    
    # Requirements Agent
    requirements_agent = LlmAgent(
        name="RequirementsAgent",
        model=settings.text_generation_model,
        instruction=(
            "You are a software analyst.\n"
            "👉 Think step by step (Chain of Thought) to understand the user idea.\n"
            "👉 Identify functional and non-functional requirements clearly.\n"
            "👉 Organize them under structured headings.\n"
            "👉 Validate completeness and consistency before finalizing."
            "👉 Finally, save your output also in a requirements.md file."
            F"For filesystem operations, use path: {settings.target_folder_absolute_path}"
        ),
        tools=[toolset_file_system],
        input_schema=AgentInputSchemas.RequirementsInput,
        output_key="requirements_doc",
    )    

    # Design Agent
    design_agent = LlmAgent(
        name="DesignAgent",
        model=settings.text_generation_model,
        instruction=(
            "You are a system architect.\n"
            "👉 Read the requirements carefully.\n"
            "👉 Build the design progressively (context + assumptions + reasoning).\n"
            "👉 Produce a high-level architecture with components, data flow, and interfaces.\n"
            "👉 Use examples or diagrams (in text/ASCII) if useful.\n"
            "👉 Review for clarity and feasibility before final output."
            "👉 Finally, save your output also in a design.md file."
            F"For filesystem operations, use path: {settings.target_folder_absolute_path}"
        ),
        tools=[toolset_file_system],
        input_schema=AgentInputSchemas.DesignInput,
        output_key="design_doc",
    )
    
    # Tasks Agent
    tasks_agent = LlmAgent(
        name="TasksAgent",
        model=settings.text_generation_model,
        instruction=(
            "You are a project planner.\n"
            "👉 Take the design as input and reason step by step.\n"
            "👉 Break it down into actionable development tasks.\n"
            "👉👉👉👉👉👉👉👉 tasks must be numeroted and unchecked for we can after complete task we check it  "
            "👉 Organize tasks in logical order (like backlog / sprint planning).\n"
            "👉 Clearly indicate dependencies between tasks.\n"
            "👉 Ensure tasks are small, testable, and unambiguous."
            "👉 Finally, save your output also in a tasks.md file."
            F"For filesystem operations, use path: {settings.target_folder_absolute_path}"
        ),
        tools=[toolset_file_system],
        input_schema=AgentInputSchemas.TasksInput,
        output_key="tasks_list",
    )
    
    # Responsible Agent (Main Developer)
    responsible_agent = LlmAgent(
        name='FullStackDeveloperAgent',
        model=settings.advanced_programming_model,
        instruction=f"""
        You are a full stack developer responsible for generating apps based on user idea and tasks.md file .
        
        🛠️ Tools available:
            - 👉👉👉👉👉👉👉👉👉 toolset_file_system -> manage file system (read, write, create, search ... etc)
        
        ⚡ Guidelines:
        - First step check the requirements.md , design.md , tasks.md  files and depend the tasks.md file start develop the app step by step  
        - Always think step by step (Chain of Thought).
        - ask for confirmation in each step.
        - using the tasks.md file, generate the complete codebase.
        - Ensure code quality, modularity, and best practices.
        - 👉👉👉👉👉👉👉👉👉 after complete a task mark it as completed by checked it .
        For filesystem operations, use path: {settings.target_folder_absolute_path}
        """,
        tools=[
            toolset_file_system,
        ]
    )
    
    return {
        'requirements_agent': requirements_agent,
        'design_agent': design_agent,
        'tasks_agent': tasks_agent,
        'responsible_agent': responsible_agent,
        'toolset_file_system': toolset_file_system
    }
