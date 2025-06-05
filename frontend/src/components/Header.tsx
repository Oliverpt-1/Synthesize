import React from 'react';
import { Headphones } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="flex flex-col items-center text-center py-12 animate-fadeIn">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-3 bg-primary-50 rounded-2xl rotate-3 transform hover:rotate-6 transition-transform duration-300">
          <Headphones className="w-12 h-12 text-primary-600" />
        </div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-600 via-primary-500 to-primary-400 text-transparent bg-clip-text transform hover:scale-105 transition-transform duration-300">
          Synthesize
        </h1>
      </div>
      <p className="text-xl text-gray-600 mt-2 font-medium tracking-wide animate-fadeIn delay-200">
        Learn on the Move
      </p>
      <div className="w-32 h-1 bg-gradient-to-r from-primary-400 to-primary-600 rounded-full mt-6 animate-fadeIn delay-300" />
    </header>
  );
};

export default Header;