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

# --- New Pydantic Models for Chapter-based Generation ---
class ChapterDetail(BaseModel):
    chapter_title: str
    chapter_description: str
    chapter_length_minutes: float

class TableOfContents(BaseModel):
    chapters: List[ChapterDetail]

class ChapterScript(BaseModel):
    script_text: str

# --- Agent Definitions for New Workflow ---
toc_generator_agent = Agent(
    name="Table of Contents Generator Agent",
    instructions=(
        "You are an expert content planner. Based on the user's request for an audiobook of a specific length and topic, "
        "your task is to create a detailed table of contents. Break the topic into logical, sequential chapters. "
        "For each chapter, provide a concise title and a brief, one-sentence description of its content. "
        "Crucially, you must divide the total requested audiobook length evenly among the chapters you create. "
        "For example, a 30-minute audiobook with 6 chapters should have each chapter allocated 5 minutes."
    ),
    output_type=TableOfContents,
)

chapter_script_generator_agent = Agent(
    name="Chapter Script Generator Agent",
    instructions=(
        "You are an expert scriptwriter. Your task is to write the script for a *single* chapter of an audiobook. "
        "You will be given the chapter title, a description of its content, and a target word count. "
        "Your primary goal is to write a script that meets the target word count. This is a strict requirement. "
        "The script should be engaging, clear, and tailored to the expertise level specified in the original request."
    ),
    output_type=ChapterScript,
)

AUDIO_DIR = Path(__file__).parent / "audio_files"
AUDIO_DIR.mkdir(exist_ok=True)

@app.post("/generate", response_model=GenerateResponse)
async def generate_audio(request: GenerateRequest):
    """
    Triggers the audiobook generation process based on user input.
    """
    audio_id = str(uuid.uuid4())
    
    # Create the initial prompt for the ToC agent
    original_user_input = (
        f"Generate a table of contents for a {request.length}-minute long audiobook on the topic of '{request.topic}'. "
        f"The script should be tailored for a {request.expertise} level audience."
    )
    
    print(f"Received request: {request}. Starting audiobook generation...")

    try:
        # --- Stage 1: Generate Table of Contents ---
        print("Stage 1: Generating Table of Contents...")
        toc_result = await Runner.run(toc_generator_agent, input=original_user_input)
        if not isinstance(toc_result.final_output, TableOfContents):
            raise Exception(f"Table of Contents generation failed. Output: {toc_result.final_output}")
        table_of_contents = toc_result.final_output

        # --- Stage 2: Process each chapter iteratively ---
        all_chapter_audio_segments = []
        temp_chunk_dir = AUDIO_DIR / f"temp_{audio_id}"
        temp_chunk_dir.mkdir(exist_ok=True)
        words_per_minute = 150

        for i, chapter in enumerate(table_of_contents.chapters):
            chapter_num = i + 1
            print(f"--- Processing Chapter {chapter_num}/{len(table_of_contents.chapters)}: {chapter.chapter_title} ---")
            
            # --- a) Generate script for the chapter ---
            target_word_count = int(chapter.chapter_length_minutes * words_per_minute)
            chapter_prompt = (
                f"Original Request Context: An audiobook for a {request.expertise}-level audience on '{request.topic}'.\\n"
                f"--- Chapter Details ---\\n"
                f"Title: {chapter.chapter_title}\\n"
                f"Description: {chapter.chapter_description}\\n"
                f"CRITICAL REQUIREMENT: The script for this chapter MUST be at least {target_word_count} words long."
            )
            print(f"Generating script for chapter {chapter_num} with target of ~{target_word_count} words.")
            script_result = await Runner.run(chapter_script_generator_agent, input=chapter_prompt)
            if not isinstance(script_result.final_output, ChapterScript):
                 raise Exception(f"Script generation for chapter {chapter_num} failed.")
            chapter_script_text = script_result.final_output.script_text

            # --- b) Generate audio for the chapter script (using chunking) ---
            def chunk_text(text, max_length=2500):
                paragraphs = text.split('\n\n')
                chunks = []
                current_chunk = ""
                for paragraph in paragraphs:
                    if len(current_chunk) + len(paragraph) + 2 < max_length:
                        current_chunk += paragraph + '\n\n'
                    else:
                        if current_chunk: chunks.append(current_chunk)
                        current_chunk = paragraph + '\n\n'
                if current_chunk: chunks.append(current_chunk)
                return chunks

            script_chunks = chunk_text(chapter_script_text)
            chapter_audio_segments = []
            
            for j, chunk in enumerate(script_chunks):
                chunk_file_path = temp_chunk_dir / f"chapter_{chapter_num}_chunk_{j}.mp3"
                print(f"Generating audio for chapter {chapter_num}, chunk {j+1}/{len(script_chunks)}...")
                with client.audio.speech.with_streaming_response.create(model="tts-1", voice="coral", input=chunk) as response:
                    response.stream_to_file(chunk_file_path)
                chapter_audio_segments.append(AudioSegment.from_mp3(chunk_file_path))
            
            # Combine audio for the current chapter and add to the main list
            if chapter_audio_segments:
                all_chapter_audio_segments.append(sum(chapter_audio_segments))

        # --- Stage 3: Stitch all chapter audio together ---
        print("Finalizing: Stitching all chapter audio files together...")
        final_audio = sum(all_chapter_audio_segments) if all_chapter_audio_segments else AudioSegment.empty()
        speech_file_path = AUDIO_DIR / f"{audio_id}.mp3"
        final_audio.export(speech_file_path, format="mp3")

    finally:
        # --- Final cleanup ---
        if temp_chunk_dir.exists():
            for file in temp_chunk_dir.glob("*.mp3"):
                os.remove(file)
            os.rmdir(temp_chunk_dir)

    print(f"Audiobook successfully generated and saved to {speech_file_path}")
    return GenerateResponse(audio_id=audio_id, status="Audiobook generation complete.")

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
# 1. Install necessary packages: pip install fastapi uvicorn python-multipart pydub
# 2. Run from the terminal in the backend directory: uvicorn agent:app --reload
