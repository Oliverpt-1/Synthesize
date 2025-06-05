import { useState, useEffect, useCallback } from 'react';
import { GenerationProgress } from '../types';
import { generateAudiobook, checkGenerationProgress, downloadAudiobook } from '../api/audioApi';

export function useAudioGeneration() {
  const [topic, setTopic] = useState('');
  const [progress, setProgress] = useState<GenerationProgress>({
    percentage: 0,
    status: 'idle',
  });
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  
  // Reset everything when starting a new generation
  const startGeneration = useCallback(async (audiobookLength: number) => {
    if (!topic.trim()) return;
    
    setProgress({
      percentage: 0,
      status: 'generating',
    });
    setAudioUrl(null);
    
    try {
      const audioId = await generateAudiobook({ topic, allotted_time_minutes: audiobookLength });
      setProgress(prev => ({
        ...prev,
        audioId,
      }));
    } catch (error) {
      setProgress({
        percentage: 0,
        status: 'error',
        error: 'Failed to start generation. Please try again.',
      });
    }
  }, [topic]);
  
  // Poll for progress updates when in generating status
  useEffect(() => {
    let intervalId: number | undefined;
    
    if (progress.status === 'generating' && progress.audioId) {
      intervalId = setInterval(async () => {
        try {
          const updatedProgress = await checkGenerationProgress(
            progress.audioId!,
            progress.percentage
          );
          
          setProgress(updatedProgress);
          
          // If generation is complete, get the download URL
          if (updatedProgress.status === 'completed') {
            const url = await downloadAudiobook(progress.audioId!);
            setAudioUrl(url);
            clearInterval(intervalId);
          }
        } catch (error) {
          setProgress(prev => ({
            ...prev,
            status: 'error',
            error: 'Failed to check progress. Please try again.',
          }));
          clearInterval(intervalId);
        }
      }, 1000) as unknown as number;
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [progress.status, progress.audioId, progress.percentage]);
  
  const resetGeneration = useCallback(() => {
    setProgress({
      percentage: 0,
      status: 'idle',
    });
    setAudioUrl(null);
  }, []);
  
  return {
    topic,
    setTopic,
    progress,
    audioUrl,
    startGeneration,
    resetGeneration,
  };
}