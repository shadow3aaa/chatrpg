# ChatRPG

[中文说明](README.md)

This project is a proof-of-concept for a conversational AI with a body. The AI's dialogue and responses are influenced by its internal, autonomously running physiological state, and the physiological state is not directly or indirectly controlled by the will of the dialogue AI.
The application features a real-time Textual User Interface (TUI) that displays the status of various organ systems and the AI's internal "sensations."

## Setup & Installation

First, clone this repository:

```bash
git clone https://github.com/shadow3aaa/chatrpg
cd chatrpg
```

1.  **Install `uv`**
    If you don't have `uv` installed, follow the official installation instructions:
    [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

2.  **Install Dependencies**
    In the project root directory, run the following command to install all required packages listed in `pyproject.toml`:
    ```bash
    uv sync
    ```

3.  **Configure Environment**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Open the newly created `.env` file and add your OpenAI-compatible API key:
    ```dotenv
    OPENAI_API_KEY="YOUR_API_KEY_HERE"

    # (Optional) If you are using a proxy or local model, uncomment and set the base URL.
    # OPENAI_API_BASE="https://api.example.com/v1"

    # (Optional) The model names to use for the different tasks. Currently, there are no specific requirements for the models.
    # REFLEX_MODEL_NAME="gpt-5"
    # PERSONA_MODEL_NAME="gpt-5"
    ```

## Running the Application

To start the TUI application, run:

```bash
uv run python main.py
```

You can interact with the AI by typing in the input box at the bottom of the screen and pressing Enter.

## License

This project is licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

