# Tashkil Coder - Modular AI Development Assistant

A clean, modular AI-powered development assistant that helps you build applications through an intelligent workflow of requirements analysis, system design, task planning, and code implementation.

## 🏗️ New Modular Architecture

The project has been refactored into a clean, maintainable modular structure:

```
├── src/                          # Main source code
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Centralized settings with Pydantic
│   ├── agents/                   # AI agent definitions
│   │   ├── __init__.py
│   │   ├── base.py              # Base schemas and types
│   │   ├── specialized_agents.py # Individual agent implementations
│   │   └── orchestrator.py      # Main workflow orchestrator
│   ├── tools/                    # MCP and other tools
│   │   ├── __init__.py
│   │   └── mcp_tools.py         # MCP toolset configurations
│   ├── services/                 # Session and service management
│   │   ├── __init__.py
│   │   └── session_service.py   # Session lifecycle management
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── logging_config.py    # Logging configuration
├── main.py                       # Main entry point
├── app.py                        # Streamlit web interface
├── tashkill_agent.py            # Legacy compatibility layer
└── tests/test.py                # Updated test module
```

## 🚀 Key Improvements

### 1. **Separation of Concerns**
- **Configuration**: Centralized in `src/config/settings.py` with environment variable management
- **Agents**: Modular agent definitions with clear responsibilities
- **Tools**: Isolated MCP tool configurations
- **Services**: Session and artifact management
- **Utils**: Reusable utility functions

### 2. **Type Safety**
- Pydantic models for configuration and data validation
- Proper type hints throughout the codebase
- Input/output schemas for agents

### 3. **Error Handling & Logging**
- Centralized logging configuration
- Proper exception handling with cleanup
- Structured logging with different levels

### 4. **Resource Management**
- Proper cleanup of MCP connections
- Session lifecycle management
- Memory-efficient operations

### 5. **Backward Compatibility**
- Legacy functions maintained for existing integrations
- Gradual migration path
- Same external API

## 🛠️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   MODEL=gemini-1.5-flash
   TEXT_GENERATION_MODEL=gemini-1.5-flash
   ADVANCED_PROGRAMMING_MODEL=gemini-1.5-pro
   TARGET_FOLDER_PATH=./output
   REACT_MANAGE_PROJECT_MCP_PATH=./tools.py
   PARENT_PROJECT_PATH=./react_parent_project/tachkill-project-template
   LOG_LEVEL=INFO
   MCP_TIMEOUT=120
   ```

## 📖 Usage

### Web Interface
```bash
streamlit run app.py
```

### Programmatic Usage
```python
from main import run_agent_async

# Simple usage
result = await run_agent_async("Create a todo app with React")

# With custom session management
from src.services import create_session_manager

session_manager = await create_session_manager()
result = await run_agent_async("Build a dashboard", session_manager)
```

### Legacy Compatibility
```python
# Old way still works
from tashkill_agent import run_agent
result = await run_agent("Create an app", None, None, None)
```

## 🔧 Configuration

### Settings Management
The `Settings` class in `src/config/settings.py` manages all configuration:

```python
from src.config import get_settings

settings = get_settings()
print(settings.model)  # Access any setting
```

### Custom Agent Configuration
```python
from src.agents import create_specialized_agents

agents = create_specialized_agents()
# Access individual agents: agents['requirements_agent'], etc.
```

### MCP Tools Configuration
```python
from src.tools import create_filesystem_toolset, create_react_project_toolset

fs_tools = create_filesystem_toolset()
react_tools = create_react_project_toolset()
```

## 🏃‍♂️ Development Workflow

The system follows a structured development workflow:

1. **Requirements Analysis** - Analyzes user ideas and generates structured requirements
2. **System Design** - Creates high-level architecture and component design
3. **Task Planning** - Breaks down the design into actionable development tasks
4. **Implementation** - Executes the tasks using filesystem and project management tools

## 🧪 Testing

Run tests with the updated test module:
```bash
python tests/test.py
```

Or use the main entry point:
```bash
python main.py
```

## 📝 Migration Guide

### From Old Structure
If you were using the old `tashkill_agent.py` directly:

**Before:**
```python
from tashkill_agent import run_agent, async_main
```

**After (Recommended):**
```python
from main import run_agent_async, run_agent
```

**After (Legacy Compatible):**
```python
from tashkill_agent import run_agent, async_main  # Still works
```

### Configuration Migration
**Before:**
```python
MODEL_ = os.getenv('MODEL')
TARGET_FOLDER_PATH = os.getenv('TARGET_FOLDER_PATH')
```

**After:**
```python
from src.config import get_settings
settings = get_settings()
model = settings.model
target_path = settings.target_folder_absolute_path
```

## 🔍 Key Components

### DevFlowAgent (Orchestrator)
The main orchestrator that manages the entire development workflow:
- Coordinates between specialized agents
- Handles resource cleanup
- Manages workflow state

### Specialized Agents
- **RequirementsAgent**: Analyzes ideas and generates requirements
- **DesignAgent**: Creates system architecture and design
- **TasksAgent**: Plans development tasks
- **FullStackDeveloperAgent**: Implements the actual code

### Session Management
- Handles session lifecycle
- Manages artifacts and state
- Provides cleanup mechanisms

## 🚦 Benefits of New Structure

1. **Maintainability**: Clear separation makes code easier to understand and modify
2. **Testability**: Each module can be tested independently
3. **Scalability**: Easy to add new agents, tools, or services
4. **Reliability**: Better error handling and resource management
5. **Performance**: More efficient resource usage and cleanup
6. **Developer Experience**: Better IDE support with proper typing

## 🔮 Future Enhancements

The modular structure enables easy addition of:
- New agent types
- Additional MCP tools
- Different session backends
- Custom workflow orchestrators
- Plugin system
- API endpoints

## 📄 License

This project maintains the same license as the original codebase.

---

**Note**: This refactoring maintains full backward compatibility while providing a much cleaner, more maintainable codebase for future development.