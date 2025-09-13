import asyncio
import shutil
import streamlit as st
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService 
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
from tests.test import run_agent
load_dotenv()

# Enhanced page configuration
st.set_page_config(
    page_title="Tashkil Coder",
    page_icon=":material/code:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Enhanced container styling */
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    }
    
    /* Improved sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0e1117 100%);
        border-right: 1px solid rgba(250, 250, 250, 0.1);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(28, 31, 47, 0.5);
        border-radius: 12px;
        margin-bottom: 8px;
        backdrop-filter: blur(10px);
    }
    
    /* Button hover effects */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(28, 31, 47, 0.6);
        border-radius: 8px;
        border: 1px solid rgba(250, 250, 250, 0.1);
    }
    
    /* Download button special styling */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
    }
    
    /* Success elements */
    div[data-testid="stMarkdownContainer"] > div.success {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    
    /* Code blocks enhancement */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid rgba(250, 250, 250, 0.1);
    }
    
    /* Popover styling */
    div[data-testid="stPopover"] {
        background: rgba(28, 31, 47, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Logo with enhanced styling
st.logo("assets/logos/tashkill-coder.png", size="large")

# Environment variables
FOLDER_PATH = os.getenv('TARGET_FOLDER_PATH')
MODEL = os.getenv('ADVANCED_PROGRAMMING_MODEL')
APP_NAME = "dev_app"
USER_ID = "12345"
SESSION_ID = "123344"

class SessionModel(BaseModel):
    session_service: object
    artifacts_service: object
    session: object

# Session management functions
async def create_session_async():
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    return SessionModel(
        session_service=session_service,
        artifacts_service=artifacts_service,
        session=session,
    )

def get_or_create_event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

def create_session():
    loop = get_or_create_event_loop()
    return loop.run_until_complete(create_session_async())

# Response generator
async def response_generator(prompt: str, session_model: SessionModel):
    response = await run_agent(
        prompt,
        session_model.session_service,
        session_model.artifacts_service,
        session_model.session,
    )
    return response

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Enhanced Sidebar
with st.sidebar:
    # Chat container with enhanced styling
    with st.container():
        # st.markdown("### :material/chat: Conversation History")
        msg_container = st.container(height=700, border=False)
        
        with msg_container:
            if not st.session_state.messages:
                st.markdown("""
                    <div style='text-align: center; padding: 2rem; color: #888;'>
                        <p>💡 Start a conversation by typing below</p>
                        <p style='font-size: 0.9rem;'>I can help you build and enhance web applications!</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for message in st.session_state.messages:
                    with st.chat_message(
                        message["role"], 
                        avatar=":material/neurology:" if message["role"] == "assistant" else ":material/alternate_email:"
                    ):
                        st.markdown(message["content"])
    
    # st.divider()
    
    # Input section with model selector
    col1, col2 = st.columns([4, 1.2])
    
    with col1:
        prompt = st.chat_input("💭 Type your message...", key="chat_input")
        if prompt:
            # Show loading spinner
            with st.spinner(":material/sync: Thinking..."):
                if "session_model" not in st.session_state:
                    st.session_state.session_model = create_session()
                session_model: SessionModel = st.session_state.session_model
                
                # Add messages
                st.session_state.messages.append({"role": "user", "content": prompt})
                response = get_or_create_event_loop().run_until_complete(
                    response_generator(prompt, session_model)
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    with col2:
        with st.popover(":material/settings: Model", use_container_width=True):
            st.markdown(f"""
                <div style='padding: 0.5rem;'>
                    <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
                        <span style='color: #00d26a;'>✓</span>
                        <strong>{MODEL if MODEL else 'Default Model'}</strong>
                    </div>
                    <hr style='margin: 0.5rem 0; opacity: 0.2;'>
                    <div style='color: #888; font-size: 0.85rem;'>
                        <p>🔜 GPT-5 Coming Soon</p>
                        <p>🔜 Claude Sonnet 4 Coming Soon</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Footer info
    with st.container():
        st.markdown("""
            <div style='margin-top: 2rem; padding: 1rem; background: rgba(28, 31, 47, 0.5); 
                        border-radius: 8px; text-align: center;'>
                <p style='color: #888; font-size: 0.8rem; margin: 0;'>
                    Session: {SESSION_ID}<br>
                    User: {USER_ID}
                </p>
            </div>
        """.format(SESSION_ID=SESSION_ID[:8], USER_ID=USER_ID), unsafe_allow_html=True)

# Main IDE Function
def ide():
    # Enhanced header with gradient
    st.markdown("""
        <div style='padding-bottom: 1rem;'>
            <h1 style='font-size: 2.5rem; background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; color: transparent;'>
                🚀 Tashkil Coder IDE
            </h1>
            <p style='color: rgba(255,255,255,0.8); font-size: 1.1rem;'>
                Your AI-powered development environment.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # File management toolbar
    col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1, 2])
    
    with col1:
        st.markdown("### :material/folder_code: Project Explorer")
    
    with col2:
        if os.path.exists(FOLDER_PATH) and os.listdir(FOLDER_PATH):
            zip_path = shutil.make_archive("project_source", "zip", FOLDER_PATH)
            with open(zip_path, "rb") as fp:
                st.download_button(
                    label=":material/arrow_circle_down: Download Source",
                    data=fp,
                    file_name="project_source.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        else:
            st.button(":material/arrow_circle_down: Download Source", disabled=True, use_container_width=True)
    
    with col3:
        if st.button(":material/commit: Push to GitHub", use_container_width=True):
            st.toast(" :material/warning: Please configure your GitHub access token first!")
    
    with col4:
        if st.button(":material/refresh: Refresh", use_container_width=True):
            st.rerun()
    
    with col5:
        search_query = st.text_input(":material/search: Search files...", label_visibility="collapsed", 
                                    placeholder="Search files...")
    
    st.divider()
    
    # Enhanced file tree with icons and syntax highlighting
    ICON_MAP = {
        ".py": (":material/code:", "python", "#3776AB"),
        ".js": (":material/javascript:", "javascript", "#F7DF1E"),
        ".jsx": (":material/javascript:", "javascript", "#61DAFB"),
        ".ts": (":material/javascript:", "typescript", "#3178C6"),
        ".tsx": (":material/javascript:", "typescript", "#61DAFB"),
        ".html": (":material/html:", "html", "#E34C26"),
        ".css": (":material/css:", "css", "#1572B6"),
        ".json": (":material/data_object:", "json", "#000000"),
        ".md": (":material/docs:", "markdown", "#000000"),
        ".txt": (":material/docs:", "text", "#000000"),
        ".yml": (":material/yaml:", "yaml", "#CB171E"),
        ".yaml": (":material/yaml:", "yaml", "#CB171E"),
        ".xml": (":material/docs:", "xml", "#FF6600"),
        ".sql": (":material/database:", "sql", "#336791"),
        ".sh": (":material/terminal:", "bash", "#4EAA25"),
        ".env": (":material/key:", "text", "#ECD53F"),
    }

    DEFAULT_ICON = (":material/docs:", None, "#888888")
    IGNORED_DIRS = {"node_modules", ".git", ".venv", "__pycache__", ".idea", ".vscode"}
    
    def get_file_info(filename: str):
        ext = os.path.splitext(filename)[1].lower()
        return ICON_MAP.get(ext, DEFAULT_ICON)
    
    def matches_search(name: str, query: str) -> bool:
        return not query or query.lower() in name.lower()
    
    def render_file_tree(path: str, level: int = 0, search: str = ""):
        """Enhanced recursive file tree with better styling"""
        try:
            entries = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for entry in entries:
                entry_path = os.path.join(path, entry)
                
                # Skip ignored directories
                if os.path.isdir(entry_path) and entry in IGNORED_DIRS:
                    continue
                
                # Apply search filter
                if search and not matches_search(entry, search):
                    # Check if any child matches
                    if os.path.isdir(entry_path):
                        has_match = any(matches_search(child, search) 
                                      for child in os.listdir(entry_path))
                        if not has_match:
                            continue
                    else:
                        continue
                
                if os.path.isdir(entry_path):
                    # Directory with custom styling
                    with st.expander(f":material/folder: **{entry}**", expanded=(level == 0)):
                        render_file_tree(entry_path, level + 1, search)
                else:
                    # File with enhanced display
                    icon, lang, color = get_file_info(entry)
                    file_size = os.path.getsize(entry_path)
                    size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B"
                    
                    with st.expander(f"{icon} {entry} `{size_str}`", expanded=False):
                        try:
                            with open(entry_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            
                            # Add file actions
                            col1, col2, col3 = st.columns([1, 1, 4])
                            with col1:
                                st.caption(f"Language: {lang or 'plain'}")
                            with col2:
                                st.caption(f"Lines: {len(content.splitlines())}")
                            
                            # Display content based on type
                            if lang == "markdown":
                                st.markdown(content)
                            elif lang == "json":
                                st.json(content)
                            elif lang == "text" or lang is None:
                                st.text(content)
                            else:
                                st.code(content, language=lang, line_numbers=True)
                                
                        except UnicodeDecodeError:
                            st.error("⚠️ Binary file - cannot display content")
                        except Exception as e:
                            st.error(f"❌ Error reading file: {str(e)}")
        
        except PermissionError:
            st.error(f"🔒 Permission denied: {path}")
        except Exception as e:
            st.error(f"❌ Error accessing directory: {str(e)}")
    
    # Main file explorer area
    if os.path.exists(FOLDER_PATH):
        if not os.listdir(FOLDER_PATH):
            # Empty folder message with call to action
            st.info("""
                :material/folder_code: **Project folder is empty**  
                Start by typing a command in the chat to generate your first files!
                
                Try something like:
                - "Create a React todo app"
                - "Build a Python Flask API"
                - "Generate a landing page"
            """)
        else:
            # File statistics
            total_files = sum(1 for _, _, files in os.walk(FOLDER_PATH) 
                            for _ in files if not any(ignored in _ for ignored in IGNORED_DIRS))
            total_dirs = sum(1 for _, dirs, _ in os.walk(FOLDER_PATH) 
                           for _ in dirs if _ not in IGNORED_DIRS)
            
            st.markdown(f"""
                <div style='display: flex; gap: 2rem; margin-bottom: 1rem;'>
                    <div style='padding: 0.5rem 1rem; background: rgba(102, 126, 234, 0.1); 
                                border-radius: 8px; border: 1px solid rgba(102, 126, 234, 0.3);'>
                         <strong>{total_files}</strong> Files
                    </div>
                    <div style='padding: 0.5rem 1rem; background: rgba(118, 75, 162, 0.1); 
                                border-radius: 8px; border: 1px solid rgba(118, 75, 162, 0.3);'>
                        <strong>{total_dirs}</strong> Folders
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Render the file tree
            render_file_tree(FOLDER_PATH, search=search_query)
    else:
        st.error(f"""
            ❌ **Project folder not found**  
            The specified folder '{FOLDER_PATH}' does not exist.
            
            Please check your `.env` configuration and ensure the `TARGET_FOLDER_PATH` is set correctly.
        """)

# Agent Trace Page
def agent_trace_page():
    st.markdown("""
        <div style='padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    border-radius: 16px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>:materi: Agent Trace</h1>
            <p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem;'>
                Monitor and debug your AI agent's activity in real-time
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Trace controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        trace_level = st.select_slider(
            "Trace Level",
            options=["Basic", "Detailed", "Verbose"],
            value="Detailed"
        )
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        if auto_refresh:
            st.caption("Refreshing every 5 seconds")
    
    with col3:
        if st.button("Clear Trace", type="secondary"):
            st.success("Trace cleared successfully!")
    
    st.divider()
    
    # Placeholder for trace content
    trace_container = st.container()
    with trace_container:
        st.info(":material/refresh: Agent trace will appear here when the agent is active...")
        # open logs.log file and display its content
        if os.path.exists('logs.log'):
            with open('logs.log', 'r') as f:
                logs = f.read()
                if logs:
                    st.markdown(logs, unsafe_allow_html=True)
                else:
                    st.info("No logs available yet.")
        else:
            st.info("No logs available yet.")
    
# Navigation setup with custom styling
pages = [
    st.Page(ide, title="IDE", icon=":material/code:"),
    st.Page(agent_trace_page, title="Agent Trace", icon=":material/eye_tracking:"),
]

# Run navigation
nav = st.navigation(pages, position="top")
nav.run()