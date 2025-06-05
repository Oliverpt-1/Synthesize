import React, { useState } from 'react';
import { useAudioGeneration } from './hooks/useAudioGeneration';
import Navigation from './components/Navigation';
import Header from './components/Header';
import TopicInput from './components/TopicInput';
import GenerateButton from './components/GenerateButton';
import ProgressIndicator from './components/ProgressIndicator';
import AudioPlayer from './components/AudioPlayer';
import AnimatedBackground from './components/AnimatedBackground';

function App() {
  const {
    topic,
    setTopic,
    progress,
    audioUrl,
    startGeneration,
    resetGeneration,
  } = useAudioGeneration();

  const [expertiseLevel, setExpertiseLevel] = useState('Intermediate');
  const [audiobookLength, setAudiobookLength] = useState(45);

  const isGenerating = progress.status === 'generating';
  const isCompleted = progress.status === 'completed';

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-primary-50 flex flex-col items-center px-4 pb-20">
      <AnimatedBackground />
      <Navigation />
      
      <main className="w-full max-w-3xl mx-auto flex flex-col items-center mt-20">
        <Header />
        
        <div className="mt-8 w-full flex flex-col items-center">
          <TopicInput 
            topic={topic} 
            setTopic={setTopic} 
            disabled={isGenerating || isCompleted}
          />
          
          <div className="mt-6 w-full max-w-md flex flex-col items-center space-y-4">
            <div>
              <label htmlFor="expertise" className="block text-sm font-medium text-gray-700 mb-1">
                Expertise Level
              </label>
              <select
                id="expertise"
                name="expertise"
                value={expertiseLevel}
                onChange={(e) => setExpertiseLevel(e.target.value)}
                disabled={isGenerating || isCompleted}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md shadow-sm"
              >
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
                <option>PhD</option>
              </select>
            </div>

            <div>
              <label htmlFor="length" className="block text-sm font-medium text-gray-700 mb-1">
                Audiobook Length: {audiobookLength} minutes
              </label>
              <input
                type="range"
                id="length"
                name="length"
                min="15"
                max="120"
                step="5"
                value={audiobookLength}
                onChange={(e) => setAudiobookLength(parseInt(e.target.value, 10))}
                disabled={isGenerating || isCompleted}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600 disabled:opacity-50"
              />
            </div>
          </div>
          
          <GenerateButton
            onClick={() => startGeneration(audiobookLength)}
            disabled={!topic.trim() || isGenerating || isCompleted}
            isGenerating={isGenerating}
          />
          
          <ProgressIndicator progress={progress} />
          
          <AudioPlayer 
            audioUrl={audioUrl} 
            onReset={resetGeneration}
          />
        </div>
      </main>
    </div>
  );
}

export default App;