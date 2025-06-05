# Synthesize

## The Vision: On-the-Go Learning

Synthesize is a tool for busy people who want to learn deeply but don't have time to sit down and read. Whether you're at the gym, walking the dog, or commuting, Synthesize transforms any topic into a custom-tailored audiobook, allowing you to learn on the go.

The goal is to provide fast, deep learning by generating polished, chapter-based audio content that respects your time and your level of expertise.

## Features

- **Custom Topic Generation:** Create an audiobook on virtually any subject you can imagine.
- **Expertise-Level Tailoring:** Choose your desired level of depth, from **Beginner** to **PhD**, to get content that's right for you.
- **Variable Length:** Specify the length of your audiobook, from a quick 15-minute overview to a 60-minute deep dive.
- **Agent-Powered Workflow:** Utilizes a sophisticated, multi-agent system powered by the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/quickstart/) to plan, outline, and script content.
- **High-Quality Audio:** Employs OpenAI's Text-to-Speech models to generate clear, listenable audio.

## Technology Stack

- **Backend:** Python, FastAPI, OpenAI Agents SDK, Pydub
- **Frontend:** React, TypeScript, Vite, Tailwind CSS

---

## Getting Started

Follow these instructions to set up and run the Synthesize application on your local machine.

### Prerequisites

- Python 3.9+
- Node.js and npm
- **FFmpeg:** A crucial dependency for audio processing.
  - on macOS: `brew install ffmpeg`
  - on Windows: `choco install ffmpeg`
  - on Linux: `sudo apt-get install ffmpeg`

### 1. Backend Setup

First, navigate to the backend directory and set up the Python environment.

```bash
# Move to the backend directory
cd backend

# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .\\.venv\\Scripts\\activate
```

Next, set your OpenAI API Key. This is a critical step.

```bash
# Replace sk-... with your actual OpenAI API key
export OPENAI_API_KEY=sk-...
```
> This key is required to use the OpenAI models that power the application. For more information, see the [OpenAI Agents SDK Quickstart](https://openai.github.io/openai-agents-python/quickstart/).

Finally, install the required Python packages.
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

In a separate terminal, navigate to the frontend directory and install the Node.js dependencies.

```bash
# Move to the frontend directory
cd frontend

# Install dependencies
npm install
```

### 3. Running the Application

You will need two separate terminals running simultaneously.

- **In your first terminal (backend):**
  ```bash
  # Ensure you are in the 'backend' directory with the venv active
  uvicorn agent:app --reload
  ```
  The backend server will start, typically on `http://127.0.0.1:8000`.

- **In your second terminal (frontend):**
  ```bash
  # Ensure you are in the 'frontend' directory
  npm run dev
  ```
  The frontend development server will start, typically on `http://localhost:5173`.

You can now open your browser and navigate to `http://localhost:5173` to use the Synthesize application!
