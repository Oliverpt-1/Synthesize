import React from 'react';

const AnimatedBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
      {/* Left side waves */}
      <div className="absolute -left-16 top-1/4">
        {[...Array(3)].map((_, i) => (
          <div
            key={`left-${i}`}
            className={`absolute h-64 w-4 rounded-full bg-gradient-to-b from-primary-${200 + i * 100} to-primary-${300 + i * 100} opacity-${30 - i * 5} animate-wave-slow`}
            style={{
              left: `${i * 8}px`,
              animationDelay: `${i * 0.5}s`,
              height: `${200 + i * 30}px`,
              filter: 'blur(8px)',
            }}
          />
        ))}
      </div>

      {/* Right side waves */}
      <div className="absolute -right-16 top-2/3">
        {[...Array(3)].map((_, i) => (
          <div
            key={`right-${i}`}
            className={`absolute h-64 w-4 rounded-full bg-gradient-to-b from-primary-${300 - i * 50} to-primary-${400 - i * 50} opacity-${25 - i * 5} animate-wave-reverse`}
            style={{
              right: `${i * 8}px`,
              animationDelay: `${i * 0.7}s`,
              height: `${180 + i * 25}px`,
              filter: 'blur(8px)',
            }}
          />
        ))}
      </div>

      {/* Bottom waves */}
      <div className="absolute bottom-0 left-1/4">
        {[...Array(5)].map((_, i) => (
          <div
            key={`bottom-${i}`}
            className={`absolute bottom-0 h-32 w-3 rounded-full bg-gradient-to-t from-primary-${200 + i * 50} to-primary-${300 + i * 50} opacity-${20 - i * 3} animate-wave`}
            style={{
              left: `${i * 40 + Math.sin(i) * 20}px`,
              animationDelay: `${i * 0.3}s`,
              height: `${100 + i * 15}px`,
              filter: 'blur(5px)',
            }}
          />
        ))}
      </div>

      {/* Floating orbs */}
      <div className="absolute inset-0">
        {[...Array(3)].map((_, i) => (
          <div
            key={`orb-${i}`}
            className="absolute w-32 h-32 rounded-full animate-float"
            style={{
              background: `radial-gradient(circle, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0) 70%)`,
              left: `${30 + i * 25}%`,
              top: `${20 + i * 20}%`,
              animationDelay: `${i * 1.5}s`,
              filter: 'blur(10px)',
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default AnimatedBackground;