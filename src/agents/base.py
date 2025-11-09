"""Base agent definitions and schemas"""

from pydantic import BaseModel, Field


class AgentInputSchemas:
    """Input schemas for different agent types"""
    
    class RequirementsInput(BaseModel):
        """Input schema for requirements generation agent"""
        app_idea: str = Field(description='The application idea')
    
    class DesignInput(BaseModel):
        """Input schema for design generation agent"""
        app_requirements: str = Field(description='The application requirements')
    
    class TasksInput(BaseModel):
        """Input schema for tasks generation agent"""
        app_design: str = Field(description='The application design')
    
class AgentOutputSchemas:
    """Output schemas for different agent types"""
    
    class RequirementsOutput(BaseModel):
        """Output schema for requirements generation agent"""
        requirements_doc: str = Field(description='The generated requirements document')

    class DesignOutput(BaseModel):
        """Output schema for design generation agent"""
        design_doc: str = Field(description='The generated design document')

    class TasksOutput(BaseModel):
        """Output schema for tasks generation agent"""
        tasks_doc: str = Field(description='The generated tasks document')
