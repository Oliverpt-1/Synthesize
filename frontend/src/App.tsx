import { useState } from 'react';
import './index.css';

// Define the structure for the API request
interface GenerateParams {
  topic: string;
  expertise: string;
  length: number;
}

function App() {
  // State variables for user inputs
  const [topic, setTopic] = useState('The Dutch Tulip Mania');
  const [expertise, setExpertise] = useState('PhD');
  const [length, setLength] = useState(15);
  
  // State for managing the app's status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const expertiseLevels = ['Beginner', 'Intermediate', 'Advanced', 'PhD'];

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setAudioUrl(null);

    const params: GenerateParams = { topic, expertise, length };

    try {
      const response = await fetch('http://127.0.0.1:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.audio_id) {
        // Construct the URL for the audio file
        setAudioUrl(`http://127.0.0.1:8000/download/${result.audio_id}`);
      } else {
        throw new Error(result.status || 'Failed to get audio ID.');
      }
    } catch (e: any) {
      setError(e.message);
      console.error("Generation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-white text-gray-800 flex flex-col items-center justify-center p-4 overflow-hidden">
      {/* Animated side elements */}
      <div className="absolute top-0 left-0 -translate-x-1/3 -translate-y-1/3">
          <div className="w-96 h-96 bg-green-200 rounded-full filter blur-3xl opacity-50 animate-blob"></div>
      </div>
      <div className="absolute bottom-0 right-0 translate-x-1/3 translate-y-1/3">
          <div className="w-96 h-96 bg-green-200 rounded-full filter blur-3xl opacity-50 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl bg-white/70 backdrop-blur-xl rounded-lg shadow-xl p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900">Synthesize</h1>
          <p className="mt-2 text-lg text-gray-600">Learn on the go.</p>
        </div>

        {/* Topic Input */}
        <div className="space-y-2">
          <label htmlFor="topic" className="text-lg font-semibold text-gray-700">Topic</label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full p-3 bg-gray-100 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g., The History of Space Exploration"
          />
        </div>

        {/* Expertise Level */}
        <div className="space-y-2">
          <label className="text-lg font-semibold text-gray-700">Expertise Level</label>
          <div className="flex flex-wrap gap-3">
            {expertiseLevels.map((level) => (
              <button
                key={level}
                onClick={() => setExpertise(level)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  expertise === level ? 'bg-green-600 text-white' : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Audiobook Length */}
        <div className="space-y-2">
          <label htmlFor="length" className="text-lg font-semibold text-gray-700">
            Length: <span className="text-green-600 font-bold">{length} minutes</span>
          </label>
          <input
            id="length"
            type="range"
            min="15"
            max="60"
            step="1"
            value={length}
            onChange={(e) => setLength(parseInt(e.target.value, 10))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer range-thumb-green"
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full p-4 bg-green-600 hover:bg-green-700 rounded-lg text-lg text-white font-bold disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300"
        >
          {loading ? 'Synthesizing... Please Wait...' : 'Generate Audiobook'}
        </button>

        {/* Results Section */}
        {error && <div className="mt-4 text-center text-red-600 bg-red-100 p-3 rounded-lg">{`Error: ${error}`}</div>}
        
        {audioUrl && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg">
            <h2 className="text-2xl font-semibold mb-3 text-center">Your Audiobook is Ready!</h2>
            <audio controls src={audioUrl} className="w-full">
              Your browser does not support the audio element.
            </audio>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;