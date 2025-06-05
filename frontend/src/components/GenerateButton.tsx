import React from 'react';
import { Disc } from 'lucide-react';

interface GenerateButtonProps {
  onClick: () => void;
  disabled?: boolean;
  isGenerating?: boolean;
}

const GenerateButton: React.FC<GenerateButtonProps> = ({
  onClick,
  disabled = false,
  isGenerating = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        flex items-center justify-center gap-2 
        px-6 py-3 mt-4 rounded-lg font-medium
        transition-all duration-200
        ${
          isGenerating
            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-primary-600 to-primary-500 text-white hover:shadow-lg hover:from-primary-500 hover:to-primary-400 active:scale-95'
        }
      `}
    >
      {isGenerating ? (
        <>
          <Disc className="w-5 h-5 animate-spin" />
          <span>Generating...</span>
        </>
      ) : (
        <>
          <Disc className="w-5 h-5" />
          <span>Generate Audiobook</span>
        </>
      )}
    </button>
  );
};

export default GenerateButton;