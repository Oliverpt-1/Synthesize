export interface AudioBook {
  id: string;
  topic: string;
  audioUrl: string;
  duration: number;
  createdAt: Date;
}

export type GenerationStatus = 'idle' | 'generating' | 'completed' | 'error';

export interface GenerationProgress {
  percentage: number;
  status: GenerationStatus;
  audioId?: string;
  error?: string;
  message?: string;
}