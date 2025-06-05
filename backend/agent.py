from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import asyncio
import random
from typing import Any, List
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel

from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool

app = FastAPI()
client = OpenAI()

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models for API ---
class GenerateRequest(BaseModel):
    topic: str
    expertise: str
    length: int

class GenerateResponse(BaseModel):
    audio_id: str
    status: str

# --- Pydantic Models for Agent Outputs ---
class FetchedContent(BaseModel):
    combined_text: str
    original_request: str

class DraftScript(BaseModel):
    script_text: str
    original_request: str

class RefinedScript(BaseModel):
    refined_script_text: str
    original_request: str

class FinalAudiobookScript(BaseModel):
    script_in_chapters: str

# --- Add a constant for character limit per file ---
MAX_CHARS_PER_FILE = 8000  # Approx. 2000 tokens, aiming for < 6000 tokens total for 3 files (leaves room for prompt)

# --- Tools ---
@function_tool
def fetch_data(filename: str) -> str:
    """
    Fetch Data from a specified file expected at './documents/{filename}' relative to the script's CWD.
    Content will be truncated if it exceeds MAX_CHARS_PER_FILE to prevent API token limits.
    Valid filenames are 'investopedia.txt', 'kremp.txt', 'wikipedia.txt'.
    """
    allowed_files = ['investopedia.txt', 'kremp.txt', 'wikipedia.txt']
    if filename not in allowed_files:
        return f"Error: File '{filename}' is not an allowed source. Please use one of {allowed_files}."
    
    # Path is relative to the current working directory when the script is run.
    # If script is in 'backend/' and run from 'backend/', './documents/' resolves to 'backend/documents/'.
    filepath_relative_to_cwd = f"./documents/{filename}"
    
    try:
        # Assuming documents are in a 'documents' subdirectory relative to the Current Working Directory (CWD)
        with open(filepath_relative_to_cwd, "r", encoding="utf-8") as f: # Added encoding
            content = f.read()
            if len(content) > MAX_CHARS_PER_FILE:
                # Truncate and add a marker
                truncated_content = content[:MAX_CHARS_PER_FILE]
                return truncated_content + f"\\n[...content truncated, original size {len(content)} chars...]"
            return content
    except FileNotFoundError:
        # Updated error message to be more precise about the path searched
        return f"Error: File '{filename}' not found at '{filepath_relative_to_cwd}' (path is relative to the current working directory)."
    except Exception as e:
        return f"An error occurred while fetching {filename}: {e}"

# --- Agent Definitions ---

# Forward declaration for handoffs
script_generator_agent: Agent
script_refiner_agent: Agent
chapterizer_agent: Agent

content_fetcher_agent = Agent(
    name="Content Fetcher Agent",
    instructions=(
        "Your primary goal is to gather textual information for an audiobook script. "
        "You must fetch content from three specific files: 'investopedia.txt', then 'kremp.txt', and finally 'wikipedia.txt', using the 'fetch_data' tool for each. "
        "Combine the content from these three files into a single text block. "
        "Preserve the original user request alongside the combined text for context in subsequent steps. "
        "After combining the content, you must pass the result to the next agent for script generation."
    ),
    tools=[fetch_data],
    output_type=FetchedContent,
    handoffs=[], # To be defined after all agents are declared
)

script_generator_agent = Agent(
    name="Script Generator Agent",
    instructions=(
        "You are an expert scriptwriter. Based on the original user request and the provided combined text, "
        "generate a draft script for the audiobook. The user's request contains details about expertise level, "
        "target audience, desired length, and topic."
        "Focus on conveying the information accurately and engagingly according to the user's original request. "
        "After generating the draft script, you must pass it to the next agent for refinement."
    ),
    output_type=DraftScript,
    handoffs=[],
)

script_refiner_agent = Agent(
    name="Script Refiner Agent",
    instructions=(
        "Your task is to refine the draft audiobook script. Review it for clarity, accuracy, flow, and engagement. "
        "Ensure it aligns with the original user request regarding tone, style, and target audience. "
        "Make improvements to create a polished version of the script. "
        "After refining the script, you must pass it to the next agent for chapterization."
    ),
    output_type=RefinedScript,
    handoffs=[],
)

chapterizer_agent = Agent(
    name="Chapterizer Agent",
    instructions=(
        "Take the refined audiobook script and structure it into logical chapters. "
        "Each chapter should have a clear title. "
        "The final output should be the complete script, well-formatted with these chapters, "
        "suitable for an audiobook narration."
    ),
    output_type=FinalAudiobookScript,
    handoffs=[], # This is the final agent in this sequence
)

# Define handoffs now that all agents are declared
content_fetcher_agent.handoffs = [script_generator_agent]
script_generator_agent.handoffs = [script_refiner_agent]
script_refiner_agent.handoffs = [chapterizer_agent]

AUDIO_DIR = Path(__file__).parent / "audio_files"
AUDIO_DIR.mkdir(exist_ok=True)

@app.post("/generate", response_model=GenerateResponse)
async def generate_audio(request: GenerateRequest):
    """
    Triggers the audiobook generation process based on user input.
    """
    audio_id = str(uuid.uuid4())
    
    # Dynamically create the prompt
    original_user_input = (
        f"You are an expert in the user-specified field. Generate a script for a {request.length}-minute long audiobook "
        f"designed for a {request.expertise} level audience to understand the topic of '{request.topic}', "
        "including associated principles and outcomes."
    )
    
    print(f"Received request: {request}. Starting agent run...")

    try:
        # --- Run Agents Sequentially ---

        # 1. Fetch Content
        print("Step 1: Running Content Fetcher Agent...")
        fetched_content_result = await Runner.run(content_fetcher_agent, input=original_user_input)
        if not isinstance(fetched_content_result.final_output, FetchedContent):
            raise Exception(f"Content Fetcher failed. Final output: {fetched_content_result.final_output}")

        # 2. Generate Draft Script
        print("Step 2: Running Script Generator Agent...")
        draft_script_result = await Runner.run(script_generator_agent, input=fetched_content_result.final_output)
        if not isinstance(draft_script_result.final_output, DraftScript):
            raise Exception(f"Script Generator failed. Final output: {draft_script_result.final_output}")

        # 3. Refine Script
        print("Step 3: Running Script Refiner Agent...")
        refined_script_result = await Runner.run(script_refiner_agent, input=draft_script_result.final_output)
        if not isinstance(refined_script_result.final_output, RefinedScript):
            raise Exception(f"Script Refiner failed. Final output: {refined_script_result.final_output}")
            
        # 4. Chapterize Script
        print("Step 4: Running Chapterizer Agent...")
        final_script_result = await Runner.run(chapterizer_agent, input=refined_script_result.final_output)
        if not isinstance(final_script_result.final_output, FinalAudiobookScript):
            raise Exception(f"Chapterizer failed. Final output: {final_script_result.final_output}")

        # --- Generate Audio ---
        print("\n--- Final Audiobook Script Generation ---")
        speech_file_path = AUDIO_DIR / f"{audio_id}.mp3"
        
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="coral",
            input=final_script_result.final_output.script_in_chapters,
        ) as response:
            response.stream_to_file(speech_file_path)
            
        print(f"Audio file successfully saved to {speech_file_path}")
        return GenerateResponse(audio_id=audio_id, status="Audio generation complete")

    except Exception as e:
        print("\n--- An error occurred during the agent pipeline: {e} ---")
        return GenerateResponse(audio_id=audio_id, status=f"An error occurred: {e}")

@app.get("/download/{audio_id}")
async def download_audio(audio_id: str):
    """
    Serves the generated audio file for download/playback.
    """
    file_path = AUDIO_DIR / f"{audio_id}.mp3"
    if not file_path.is_file():
        return {"error": "Audio file not found or generation not complete."}
    return FileResponse(file_path, media_type="audio/mpeg", filename=f"{audio_id}.mp3")

# To run this app:
# 1. Install necessary packages: pip install fastapi uvicorn python-multipart
# 2. Run from the terminal in the backend directory: uvicorn agent:app --reload
