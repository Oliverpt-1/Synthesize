import React from 'react';

interface TopicInputProps {
  topic: string;
  setTopic: (topic: string) => void;
  disabled?: boolean;
}

const TopicInput: React.FC<TopicInputProps> = ({ topic, setTopic, disabled = false }) => {
  return (
    <div className="w-full max-w-xl">
      <label htmlFor="topic\" className="block text-sm font-medium text-gray-700 mb-2">
        What would you like to learn about?
      </label>
      <input
        type="text"
        id="topic"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        disabled={disabled}
        placeholder="e.g., Quantum Mechanics, Startup Strategy, Deep Learning..."
        className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-400 focus:border-primary-400 transition-all duration-200 disabled:bg-gray-100 disabled:text-gray-500"
      />
    </div>
  );
};

export default TopicInput;