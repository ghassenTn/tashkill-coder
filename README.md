# Tashkil Coder

Tashkil Coder is a Streamlit web application that allows you to create and enhance web applications using a full-stack web developer agent powered by Gemini.

## Features

*   **AI-Powered Web Development**: Leverage the power of a Gemini-based agent to generate and modify web application code.
*   **Interactive Chat Interface**: Communicate with the agent through a user-friendly chat interface.
*   **File Explorer**: View and manage the generated project files directly in the browser.
*   **Download Source Code**: Download the complete source code of your project as a zip file.
*   **Extensible**: The agent's capabilities can be extended by adding more tools.

## Getting Started

### Prerequisites

*   Python 3.7+
*   Node.js and npm
*   A Gemini API key

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/tashkil-coder.git
    cd tashkil-coder
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv env
    source env/bin/activate
    ```

3.  **Install the Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the Node.js dependencies for the MCP server:**

    ```bash
    npm install -g @modelcontextprotocol/server-filesystem
    ```

5.  **Set up your environment variables:**

    Create a `.env` file in the root of the project and add the following:

    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    TARGET_FOLDER_PATH="path/to/your/target/folder"
    ```

## Usage

1.  **Run the Streamlit application:**

    ```bash
    streamlit run app.py
    ```

2.  Open your web browser and navigate to the provided URL (usually `http://localhost:8501`).

3.  Start a conversation with the Tashkil Coder agent by typing a prompt in the chat input box. For example:

    > "Create a simple flask application with a single route that displays 'Hello, World!'"

4.  The agent will generate the code and you can see the file structure in the file explorer.

## Project Structure

```
.
├── app.py                  # The main Streamlit application file.
├── tashkill_agent.py       # The core logic for the Gemini agent.
├── requirements.txt        # Python dependencies.
├── .env                    # Environment variable configuration.
├── assets/                 # Static assets like logos and images.
└── README.md               # This file.
```

## Built With

*   [Streamlit](https://streamlit.io/) - The web framework used to build the user interface.
*   [Gemini](https://deepmind.google/technologies/gemini/) - The large language model powering the agent.
*   [Model-Context-Protocol (MCP)](https://github.com/modelcontextprotocol/servers) - For communication between the agent and the local filesystem.
