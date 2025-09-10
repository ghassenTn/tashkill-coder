
import asyncio
import shutil
import streamlit as st
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService 
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
from tashkill_agent import run_agent
load_dotenv()

st.set_page_config(
    page_title=" Tashkil Coder",
    page_icon=":material/code_blocks: ",
    layout="wide",
)
st.logo("assets/logos/tashkill-coder.png",size="large")

FOLDER_PATH = os.getenv('TARGET_FOLDER_PATH')
MODEL = os.getenv('MODEL')
class SessionModel(BaseModel):
    session_service: object
    artifacts_service: object
    session: object


async def create_session_async():
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    session = await session_service.create_session(
        state={}, app_name="mcp_filesystem_app", user_id="user_fs"
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
    print('hey')
    response = await run_agent(
        prompt,
        session_model.session_service,
        session_model.artifacts_service,
        session_model.session,
    )
    return response

 # Initialize messages
if "messages" not in st.session_state:
        st.session_state.messages = []

with st.sidebar:
    msg_container = st.container(height=670, border=False)
    with msg_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    st.divider()
    user_prompt, choose_model = st.columns([4,1.2])
    with user_prompt:
        if prompt := st.chat_input("Type your message..."):
            if "session_model" not in st.session_state:
                st.session_state.session_model = create_session()
            session_model: SessionModel = st.session_state.session_model

            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append(
                {"role": "assistant", "content": get_or_create_event_loop().run_until_complete(response_generator(prompt, session_model))}
            )
    with msg_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    with choose_model:
        with st.popover('model') :
            st.write(f'{MODEL} :material/verified:')
            st.caption('Chat gpt 5 comming soon')
            st.caption('claude sonnet 4 comming soon') 


def ide():
   

    # Main chat area - display conversation history
    st.title(":material/code_blocks: Tashkil Coder ")
    st.caption("with :material/code_blocks: you can create and enhance your web app using a full stack web developper agent")
    st.divider()

    # Display chat messages
    ICON_MAP = {
        ".py": (":material/code:", "python"),
        ".js": (":material/javascript:", "javascript"),
        ".html": (":material/html:", "html"),
        ".css": (":material/css:", "css"),
        ".json": (":material/data_object:", "json"),
        ".md": (":material/markdown:", "markdown"),
        ".txt": (":material/description:", "text"),
    }

    DEFAULT_ICON = ":material/insert_drive_file:"
    def get_file_info(filename: str):
        ext = os.path.splitext(filename)[1].lower()
        return ICON_MAP.get(ext, (DEFAULT_ICON, None))

    IGNORED_DIRS = {"node_modules", ".git", ".venv", "__pycache__"}

    def render_file_tree(path: str):
        """Recursive file tree browser with Material Icons"""
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)

            # ✨ Skip ignored dirs
            if os.path.isdir(entry_path) and entry in IGNORED_DIRS:
                continue

            if os.path.isdir(entry_path):
                with st.expander(f":material/folder: {entry}", expanded=False):
                    render_file_tree(entry_path)
            else:
                icon, lang = get_file_info(entry)
                with st.expander(f"{icon} {entry}", expanded=False):
                    try:
                        with open(entry_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        st.code(content, language=lang, wrap_lines=True, line_numbers=True)
                    except Exception as e:
                        st.error(f"Erreur en lisant {entry}: {e}")

    # ---- HEADER ----

    cols = st.columns([6,1.2,1], vertical_alignment='center')
    # with cols[0]:
    #     st.title(":material/folder: File Explorer (IDE style)")

    with cols[1]:
        # create zip file in temp dir
        zip_path = shutil.make_archive("project_source", "zip", FOLDER_PATH)
        with open(zip_path, "rb") as fp:
            st.download_button(
                label=":material/download: Source Code",
                data=fp,
                file_name="project_source.zip",
                mime="application/zip"
            )

    with cols[2]:
        if st.button(":material/commit: Github"):
            st.toast('You must add your github acces token first ')
            

    # ---- BODY ----
    if os.path.exists(FOLDER_PATH):
        if not os.listdir(FOLDER_PATH):
            st.warning(f" :material/warning: Dossier '{FOLDER_PATH}' est vide. Veuillez exécuter une commande d'agent pour générer des fichiers.")
        render_file_tree(FOLDER_PATH)
    else:
        st.error(f"Dossier '{FOLDER_PATH}' n'existe pas.")
        


def docs_page():
    def ide_():
        st.write("IDE")
    def docs_page4():
        st.write("Agent Trace")

pages = [
    st.Page(ide, title="IDE", icon=":material/code:"),
    st.Page(docs_page, title="Agent Trace", icon=":material/footprint:"),
]
nav = st.navigation(pages, position="top")

nav.run()