import React from 'react';
import { Play, Download, RefreshCw } from 'lucide-react';

interface AudioPlayerProps {
  audioUrl: string | null;
  onReset: () => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl, onReset }) => {
  if (!audioUrl) return null;

  return (
    <div className="w-full max-w-xl mt-8 bg-white rounded-lg shadow-md p-6 border border-gray-100">
      <h3 className="text-lg font-medium text-gray-800 mb-4">Your Audiobook</h3>

      <div className="flex flex-col space-y-4">
        <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center">
            <button
              className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white hover:bg-primary-600 transition-colors"
              title="Play audiobook"
            >
              <Play className="w-5 h-5" />
            </button>
            <div className="ml-4">
              <div className="h-2 rounded-full bg-gradient-to-r from-primary-200 to-primary-400 w-40" />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0:00</span>
                <span>~15:30</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex space-x-4">
          <a
            href={audioUrl}
            download
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </a>
          <button
            onClick={onReset}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 border border-primary-500 text-primary-600 hover:bg-primary-50 rounded-lg font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>New Topic</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;