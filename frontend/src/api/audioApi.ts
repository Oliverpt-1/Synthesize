import { GenerationProgress } from '../types';

// Type for the /generate endpoint payload
interface GenerateAudioPayload {
  topic: string;
  allotted_time_minutes: number;
}

// Type for the /generate endpoint response
interface GenerateAudioResponse {
  task_id: string;
  status: string;
  message: string;
  download_url?: string;
}

// Type for the /status endpoint response
interface TaskStatusResponse {
  task_id: string;
  status: string; // e.g., "queued", "processing_context", "generating_script", "converting_to_audio", "completed", "failed"
  message: string;
  download_url?: string;
}

const API_BASE_URL = 'http://localhost:8000'; // Assuming your backend runs here

/**
 * Simulate generating an audiobook based on a topic
 */
export const generateAudiobook = async (payload: GenerateAudioPayload): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Failed to start generation. Server returned an error.' }));
    throw new Error(errorData.message || 'Failed to start generation');
  }

  const data: GenerateAudioResponse = await response.json();
  return data.task_id; // Return the task_id (which is the audioId in this context)
};

/**
 * Simulate checking the generation progress
 */
export const checkGenerationProgress = async (
  audioId: string,
  // currentProgress: number // This was for simulation, backend now manages actual progress message
): Promise<GenerationProgress> => {
  const response = await fetch(`${API_BASE_URL}/status/${audioId}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Failed to check progress. Server returned an error.' }));
    throw new Error(errorData.message || 'Failed to check progress');
  }
  const data: TaskStatusResponse = await response.json();

  // Map backend status to frontend progress
  // This is a simple mapping, could be more sophisticated
  let percentage = 0;
  if (data.status === 'queued') percentage = 10;
  else if (data.status === 'processing_context') percentage = 25;
  else if (data.status === 'generating_script') percentage = 50;
  else if (data.status === 'converting_to_audio') percentage = 75;
  else if (data.status === 'completed') percentage = 100;
  else if (data.status === 'failed') percentage = 0; // Or handle differently

  return {
    percentage,
    status: data.status === 'completed' ? 'completed' : data.status === 'failed' ? 'error' : 'generating',
    audioId,
    error: data.status === 'failed' ? data.message : undefined,
    message: data.message, // Pass through the backend message
  };
};

/**
 * Simulate downloading the generated audiobook
 */
export const downloadAudiobook = async (audioId: string): Promise<string> => {
  // The backend /download/{audio_id} endpoint directly serves the file.
  // The AudioPlayer component can use this URL directly as its src.
  // No need to fetch and create a blob URL if the browser can stream from the endpoint.
  return `${API_BASE_URL}/download/${audioId}`;
};