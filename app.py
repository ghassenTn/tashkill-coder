import asyncio
import re
import streamlit as st
import os 
from pydantic import BaseModel

# Import from new modular structure
from main import run_agent_async
from src.config import get_settings
from src.services import create_session_manager
from src.utils import setup_logging

st.set_page_config(
    page_title="Tashkil Coder",
    page_icon=":material/code:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize settings and logging
settings = get_settings()
logger = setup_logging()

# Environment variables from settings
FOLDER_PATH = settings.target_folder_absolute_path
MODEL = settings.advanced_programming_model

class SessionModel(BaseModel):
    """Legacy session model for compatibility"""
    session_manager: object
    model_config = {"arbitrary_types_allowed": True}

# Session management functions
async def create_session_async():
    """Create session using new modular structure"""
    session_manager = await create_session_manager()
    return SessionModel(session_manager=session_manager)

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
    """Generate response using new modular structure"""
    response =  run_agent_async(prompt, session_model.session_manager)
    async for event in response:
        yield event.content.parts[0].text


def sync_from_async_generator(async_gen):
    """
    Read an async generator from sync code using an event loop.
    Works by calling __anext__ with loop.run_until_complete until StopAsyncIteration.
    """
    try:
        loop = get_or_create_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    while True:
        try:
            item = loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            break
        except Exception as e:
            # log and break on unexpected errors from the generator
            logger.exception("Error while reading async generator: %s", e)
            break
        else:
            yield item
# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

@st.fragment
def chatWithAgent():

    msg_container =  st.container(height=850, border=False)

        
    col1, col2 = st.columns([4, 1.2])
    with col2:
        with st.popover(":material/network_intelligence: Model", use_container_width=True):
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

    with col1:
        prompt = st.chat_input("💭 Type your message...", key="chat_input")
        if prompt:
            with st.spinner("Thinking...", show_time=True):
                # Ensure session exists
                if "session_model" not in st.session_state:
                    st.session_state.session_model = create_session()
                session_model: SessionModel = st.session_state.session_model

                # Append user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with msg_container:
                    # Display all messages
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            with st.chat_message("user", avatar=":material/person:"):
                                st.markdown(msg["content"])
                        else:
                            with st.chat_message("assistant", avatar=":material/neurology:"):
                                st.markdown(msg["content"])
                # Prepare async response stream
                async_gen = response_generator(prompt, session_model)

                # Append empty assistant message (will stream into it)
                st.session_state.messages.append({"role": "assistant", "content": ""})
                with msg_container:

                    with st.chat_message("assistant", avatar=":material/neurology:"):
                        stream_placeholder = st.empty()

                        # Consume async generator chunk by chunk
                        for chunk in sync_from_async_generator(async_gen):
                            chunk_text = "" if chunk is None else str(chunk)
                            st.session_state.messages[-1]["content"] += chunk_text
                            
                            # live update inside SAME chat bubble
                            stream_placeholder.markdown(st.session_state.messages[-1]["content"])
                        # final render
                        stream_placeholder.markdown(st.session_state.messages[-1]["content"])
                            

        
# Enhanced Sidebar
with st.sidebar:
    chatWithAgent()
    

def preview():    
    # Check project type
    package_json_path = os.path.join(FOLDER_PATH, "package.json")
    has_react_project = os.path.exists(package_json_path)
    
    if not has_react_project:
        st.html("""
            <div style='text-align: center; padding: 3rem;'>
                <h2>🎨 No Project Yet</h2>
                <p>Start by creating a React project in the chat!</p>
            </div>
        """)
        return
    

    preview_url = "http://localhost:8080"
    
    import requests
    try:
        response = requests.get(preview_url, timeout=5)
        if response.status_code == 200:
            st.components.v1.iframe(preview_url, height=800, scrolling=True)
        else:
            st.warning("Server not responding correctly")
    except:
        st.warning("""
            :material/warning: Dev server not running
            
            Start it with: `npm run dev` in the project folder
        """)
    

# Navigation setup with custom styling
pages = [
    st.Page(preview, title="Preview", icon=":material/eye_tracking:"),
]

# Run navigation
nav = st.navigation(pages, position="top")
nav.run()