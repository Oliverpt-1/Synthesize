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
import traceback
from pydub import AudioSegment
import os

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

class FinalAudiobookScript(BaseModel):
    script_in_chapters: str

# --- Tools ---
@function_tool
def fetch_data(filename: str) -> str:
    """
    Fetch the full content from a specified file expected at './documents/{filename}' relative to the script's CWD.
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
        with open(filepath_relative_to_cwd, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Updated error message to be more precise about the path searched
        return f"Error: File '{filename}' not found at '{filepath_relative_to_cwd}' (path is relative to the current working directory)."
    except Exception as e:
        return f"An error occurred while fetching {filename}: {e}"

# --- Agent Definitions ---
content_fetcher_agent = Agent(
    name="Content Fetcher Agent",
    instructions=(
        "Your primary goal is to gather textual information for an audiobook script. "
        "You must fetch content from three specific files: 'investopedia.txt', then 'kremp.txt', and finally 'wikipedia.txt', using the 'fetch_data' tool for each. "
        "Combine the content from these three files into a single text block. "
        "Preserve the original user request alongside the combined text for context in subsequent steps."
    ),
    tools=[fetch_data],
    output_type=FetchedContent,
)

script_producer_agent = Agent(
    name="Script Producer Agent",
    instructions=(
        "You are an expert scriptwriter. Your primary and most critical task is to generate a script that meets a specific word count. "
        "The user's request will contain a target word count. It is a strict requirement that you produce a script with at least that many words. "
        "Do not write a script shorter than the requested word count, as this is considered a failure. "
        "Based on the original user request and the provided combined text, generate a final, polished audiobook script structured into logical chapters, ensuring it meets the length requirement."
    ),
    output_type=FinalAudiobookScript,
)

AUDIO_DIR = Path(__file__).parent / "audio_files"
AUDIO_DIR.mkdir(exist_ok=True)

@app.post("/generate", response_model=GenerateResponse)
async def generate_audio(request: GenerateRequest):
    """
    Triggers the audiobook generation process based on user input.
    """
    audio_id = str(uuid.uuid4())
    
    # Calculate target word count for the prompt
    words_per_minute = 150  # Standard speaking pace
    target_word_count = request.length * words_per_minute

    # Dynamically create a more forceful prompt
    original_user_input = (
        f"Your main goal is to generate a script for a {request.length}-minute long audiobook on the topic of '{request.topic}'. "
        f"To achieve this, the script's length is critical. It MUST contain at least {target_word_count} words. This is a strict requirement. "
        f"The script must be tailored for a {request.expertise} level audience, covering the topic, its principles, and outcomes."
    )
    
    print(f"Received request: {request}. Starting agent run with a strict target of at least {target_word_count} words.")

    try:
        # --- Run Agents Sequentially ---

        # 1. Fetch Content
        print("Step 1: Running Content Fetcher Agent...")
        fetched_content_result = await Runner.run(content_fetcher_agent, input=original_user_input)
        if not isinstance(fetched_content_result.final_output, FetchedContent):
            raise Exception(f"Content Fetcher failed. Final output: {fetched_content_result.final_output}")

        # Prepare input for the next agent
        producer_input_text = (
            f"--- ORIGINAL USER REQUEST ---\\n{fetched_content_result.final_output.original_request}\\n\\n"
            f"--- COMBINED SOURCE TEXT ---\\n{fetched_content_result.final_output.combined_text}"
        )

        # 2. Generate Final Script (Combined Step)
        print("Step 2: Running Script Producer Agent...")
        final_script_result = await Runner.run(
            script_producer_agent, 
            input=producer_input_text # The runner can handle a single string input
        )
        if not isinstance(final_script_result.final_output, FinalAudiobookScript):
            raise Exception(f"Script Producer failed. Final output: {final_script_result.final_output}")

        # --- Generate Audio ---
        print("\n--- Final Audiobook Script Generation ---")
        speech_file_path = AUDIO_DIR / f"{audio_id}.mp3"
        final_script_text = final_script_result.final_output.script_in_chapters

        # --- New: Chunking logic to handle API limit ---
        def chunk_text(text, max_length=2500): # Use a more conservative limit
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = ""
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) + 2 < max_length:
                    current_chunk += paragraph + '\n\n'
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = paragraph + '\n\n'
            if current_chunk:
                chunks.append(current_chunk)
            return chunks

        script_chunks = chunk_text(final_script_text)
        audio_segments = []
        temp_chunk_dir = AUDIO_DIR / f"temp_{audio_id}"
        temp_chunk_dir.mkdir(exist_ok=True)

        try:
            for i, chunk in enumerate(script_chunks):
                chunk_file_path = temp_chunk_dir / f"chunk_{i}.mp3"
                print(f"Generating audio for chunk {i+1}/{len(script_chunks)}...")
                with client.audio.speech.with_streaming_response.create(
                    model="tts-1",
                    voice="coral",
                    input=chunk,
                ) as response:
                    response.stream_to_file(chunk_file_path)
                
                audio_segments.append(AudioSegment.from_mp3(chunk_file_path))
            
            # --- New: Concatenate audio segments ---
            print("Combining audio chunks...")
            final_audio = sum(audio_segments) if audio_segments else AudioSegment.empty()
            
            # Export the final combined audio file
            final_audio.export(speech_file_path, format="mp3")

        finally:
            # --- New: Clean up temporary chunk files and directory ---
            for file in temp_chunk_dir.glob("*.mp3"):
                os.remove(file)
            os.rmdir(temp_chunk_dir)

        print(f"Audio file successfully saved to {speech_file_path}")
        return GenerateResponse(audio_id=audio_id, status="Audio generation complete")

    except Exception as e:
        print(f"\n--- An error occurred during the agent pipeline ---")
        traceback.print_exc()
        error_message = f"An error occurred: {repr(e)}"
        return GenerateResponse(audio_id=audio_id, status=error_message)

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
