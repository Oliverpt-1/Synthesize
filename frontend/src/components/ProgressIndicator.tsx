import React from 'react';
import { GenerationProgress } from '../types';

interface ProgressIndicatorProps {
  progress: GenerationProgress;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ progress }) => {
  if (progress.status === 'idle') return null;

  return (
    <div className="w-full max-w-xl mt-8 px-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-medium text-gray-800">
          {progress.status === 'generating'
            ? 'Synthesizing your audiobook...'
            : progress.status === 'completed'
            ? 'Your audiobook is ready!'
            : 'Something went wrong'}
        </h3>
        <span className="text-sm font-medium text-primary-600">
          {Math.round(progress.percentage)}%
        </span>
      </div>

      <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${
            progress.status === 'error'
              ? 'bg-red-500'
              : 'bg-gradient-to-r from-primary-400 to-primary-600'
          }`}
          style={{ width: `${progress.percentage}%` }}
        />
      </div>

      {progress.status === 'generating' && (
        <div className="mt-4 flex justify-center">
          <div className="flex space-x-1">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className={`w-2 h-8 bg-primary-${400 - i * 50} rounded-full animate-wave`}
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
            {[...Array(5)].map((_, i) => (
              <div
                key={i + 5}
                className={`w-2 h-8 bg-primary-${200 + i * 50} rounded-full animate-wave-reverse`}
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
            {[...Array(5)].map((_, i) => (
              <div
                key={i + 10}
                className={`w-2 h-8 bg-primary-${400 - i * 50} rounded-full animate-wave`}
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        </div>
      )}

      {progress.status === 'error' && (
        <p className="mt-4 text-red-600 text-sm">{progress.error}</p>
      )}
    </div>
  );
};

export default ProgressIndicator;