from fastapi import FastAPI
from fastapi.responses import FileResponse
import uuid
import asyncio
import random
from typing import Any, List

from pydantic import BaseModel

from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool

app = FastAPI()


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

# --- Tools ---
@function_tool
def fetch_data(filename: str) -> str:
    """
    Fetch Data from a specified file in the documents directory.
    Valid filenames are 'investopedia.txt', 'kremp.txt', 'wikipedia.txt'.
    """
    allowed_files = ['investopedia.txt', 'kremp.txt', 'wikipedia.txt']
    if filename not in allowed_files:
        return f"Error: File '{filename}' is not an allowed source. Please use one of {allowed_files}."
    try:
        # Assuming documents are in a 'documents' subdirectory relative to this script
        with open(f"backend/documents/{filename}", "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found in backend/documents/."
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
        "Preserve the original user request alongside the combined text for context in subsequent steps."
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
        "Focus on conveying the information accurately and engagingly according to the user's original request."
    ),
    output_type=DraftScript,
    handoffs=[],
)

script_refiner_agent = Agent(
    name="Script Refiner Agent",
    instructions=(
        "Your task is to refine the draft audiobook script. Review it for clarity, accuracy, flow, and engagement. "
        "Ensure it aligns with the original user request regarding tone, style, and target audience. "
        "Make improvements to create a polished version of the script."
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


async def main() -> None:
    original_user_input = (
        "You are an expert in Nuclear Physics. Generate a script for a 15-minute long audiobook "
        "designed for a PhD level economicist to understand the Tulip trading mania, "
        "economics principles associated, and outcome."
    )
    
    # The initial input to the ContentFetcherAgent should be the original_user_input,
    # as it needs to pass it along. Its instructions guide it to fetch files.
    run_result = await Runner.run(
        content_fetcher_agent,
        input=original_user_input, # The agent will use this for context and pass it on
    )

    if isinstance(run_result.final_output, FinalAudiobookScript):
        print("\n--- Final Audiobook Script ---")
        print(run_result.final_output.script_in_chapters)
    else:
        print("\n--- Agent Run Ended ---")
        print(f"Final output type: {type(run_result.final_output)}")
        print(f"Final output: {run_result.final_output}")
    
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())

'''
@app.post("/generate")
async def generate_audio(topic: str = ""):
    # In a real app, this would trigger the audiobook generation process
    audio_id = str(uuid.uuid4())
    return {"audio_id": audio_id, "status": "Audio generation started"}

@app.get("/download/{audio_id}")
async def download_audio(audio_id: str):
    # In a real app, this would check the status and return the file
    # For now, it just returns a placeholder message
    # You could also return a FileResponse if you have a dummy MP3
    # e.g., return FileResponse("path/to/dummy.mp3", media_type="audio/mpeg", filename=f"{audio_id}.mp3")
    return {"message": "Download ready", "audio_id": audio_id}

'''
# To run this app:
# 1. Install uvicorn and fastapi: pip install fastapi uvicorn
# 2. Run from the terminal in the backend directory: uvicorn agent:app --reload
