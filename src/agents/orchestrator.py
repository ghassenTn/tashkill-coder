"""Main orchestrator agent for development workflow"""

import logging
from typing import AsyncGenerator, Dict, Any
from typing_extensions import override

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from .specialized_agents import create_specialized_agents


logger = logging.getLogger(__name__)


class DevFlowAgent(BaseAgent):
    """
    Custom orchestrator agent for software development workflow.
    Manages the flow from requirements -> design -> tasks -> implementation.
    """

    requirements_agent: LlmAgent
    design_agent: LlmAgent
    tasks_agent: LlmAgent
    responsible_agent: LlmAgent 
    toolset_file_system: MCPToolset
    
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        requirements_agent: LlmAgent,
        design_agent: LlmAgent,
        tasks_agent: LlmAgent,
        responsible_agent: LlmAgent,
        toolset_file_system: MCPToolset
    ):
        """
        Initialize the development flow orchestrator
        
        Args:
            name: Agent name
            requirements_agent: Agent for generating requirements
            design_agent: Agent for creating system design
            tasks_agent: Agent for breaking down tasks
            responsible_agent: Main development agent
            toolset_file_system: Filesystem toolset for file operations
        """
        # Only the responsible agent is in sub_agents as it orchestrates others
        sub_agents_list = [responsible_agent]

        super().__init__(
            name=name,
            description="Orchestrates requirement → design → tasks → coding workflow",
            requirements_agent=requirements_agent,
            design_agent=design_agent,
            tasks_agent=tasks_agent,
            responsible_agent=responsible_agent,
            toolset_file_system=toolset_file_system,
            sub_agents=sub_agents_list,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Execute the development workflow
        
        Args:
            ctx: Invocation context containing session and user input
            
        Yields:
            Events from the development process
        """

        

        # generate project requirements
        if 'requirements_doc' not in ctx.session.state or not ctx.session.state['requirements_doc']:
            logger.error(f"[{self.name}] Starting to generate project requirements .")
            try:
                logger.info(f"[{self.name}] Starting project  requirement ")
                async for event in self.requirements_agent.run_async(ctx):
                    logger.info(
                        f"[{self.name}] Event from workflow: "
                        f"{event.model_dump_json(indent=2, exclude_none=True)}"
                    )
                    yield event
            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
                raise e
            finally:
                # Clean up resources
                if self.toolset_file_system:
                    try:
                        await self.toolset_file_system.close()
                        logger.info(f"[{self.name}] Toolset closed successfully")
                    except Exception as e:
                        logger.warning(f"[{self.name}] Error closing toolset: {e}")

        

            logger.info(f"[{self.name}] Project state after generate requirements: {ctx.session.state.get('requirements_doc')}")

        # generate project design 
        if 'design_doc' not in ctx.session.state or not ctx.session.state['design_doc'] :
            logger.error(f"[{self.name}] Starting to generate project design .")
            try:
                logger.info(f"[{self.name}] Starting project  design  ")
                async for event in self.design_agent.run_async(ctx):
                    logger.info(
                        f"[{self.name}] Event from workflow: "
                        f"{event.model_dump_json(indent=2, exclude_none=True)}"
                    )
                    yield event
            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
                raise e
            finally:
                # Clean up resources
                if self.toolset_file_system:
                    try:
                        await self.toolset_file_system.close()
                        logger.info(f"[{self.name}] Toolset closed successfully")
                    except Exception as e:
                        logger.warning(f"[{self.name}] Error closing toolset: {e}")
            

            logger.info(f"[{self.name}] Project state after generate design: {ctx.session.state.get('design_doc')}")


        # generate project tasks
        if 'tasks_list' not in ctx.session.state or not ctx.session.state['tasks_list'] :
            logger.error(f"[{self.name}] Starting  generate project tasks .")
            try:
                logger.info(f"[{self.name}] Starting project  tasks  ")
                async for event in self.tasks_agent.run_async(ctx):
                    logger.info(
                        f"[{self.name}] Event from workflow: "
                        f"{event.model_dump_json(indent=2, exclude_none=True)}"
                    )
                    yield event
            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
                raise e
            finally:
                # Clean up resources
                if self.toolset_file_system:
                    try:
                        await self.toolset_file_system.close()
                        logger.info(f"[{self.name}] Toolset closed successfully")
                    except Exception as e:
                        logger.warning(f"[{self.name}] Error closing toolset: {e}")
            
            logger.info(f"[{self.name}] Project state after generate tasks: {ctx.session.state.get('tasks_list')}")


        try:
            logger.info(f"[{self.name}] Starting development workflow")
            
            # Execute the responsible agent which will orchestrate the entire flow
            async for event in self.responsible_agent.run_async(ctx):
                logger.info(
                    f"[{self.name}] Event from workflow: "
                    f"{event.model_dump_json(indent=2, exclude_none=True)}"
                )
                yield event
                
            logger.info(f"[{self.name}] Workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            raise e
        finally:
            # Clean up resources
            if self.toolset_file_system:
                try:
                    await self.toolset_file_system.close()
                    logger.info(f"[{self.name}] Toolset closed successfully")
                except Exception as e:
                    logger.warning(f"[{self.name}] Error closing toolset: {e}")


def create_dev_flow_agent() -> DevFlowAgent:
    """
    Factory function to create a configured DevFlowAgent
    
    Returns:
        Configured DevFlowAgent instance
    """
    agents_config = create_specialized_agents()
    
    return DevFlowAgent(
        name="AppDevOrchestrator",
        requirements_agent=agents_config['requirements_agent'],
        design_agent=agents_config['design_agent'],
        tasks_agent=agents_config['tasks_agent'],
        responsible_agent=agents_config['responsible_agent'],
        toolset_file_system=agents_config['toolset_file_system']
    )