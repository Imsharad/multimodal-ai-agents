import React from 'react';
import { motion } from 'framer-motion';

interface CompanyLogoProps {
  className?: string;
}

/**
 * Placeholder company logo component
 * TODO: Replace with actual company logo when received from the team
 */
export function CompanyLogo({ className = '' }: CompanyLogoProps) {
  return (
    <motion.div 
      className={`flex items-center justify-center ${className}`}
      initial={{ scale: 0.9, opacity: 0.8 }}
      animate={{ 
        scale: [0.9, 1, 0.9],
        opacity: [0.8, 1, 0.8]
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {/* Placeholder logo - replace with actual logo when available */}
      <div className="relative w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 flex items-center justify-center shadow-lg">
        {/* Animated gradient background */}
        <motion.div 
          className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 opacity-70"
          animate={{
            background: [
              'linear-gradient(to right, #3b82f6, #8b5cf6, #4f46e5)',
              'linear-gradient(to right, #4f46e5, #3b82f6, #8b5cf6)',
              'linear-gradient(to right, #8b5cf6, #4f46e5, #3b82f6)',
              'linear-gradient(to right, #3b82f6, #8b5cf6, #4f46e5)'
            ]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        
        {/* Glow effect */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 opacity-50 blur-md"></div>
        
        {/* Inner highlight */}
        <div className="absolute inset-1 rounded-full bg-gradient-to-br from-white/20 to-transparent"></div>
        
        {/* Logo text with subtle animation */}
        <motion.div 
          className="relative z-10 flex items-center justify-center"
          animate={{
            textShadow: [
              '0 0 5px rgba(255,255,255,0.5)',
              '0 0 10px rgba(255,255,255,0.7)',
              '0 0 5px rgba(255,255,255,0.5)'
            ]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <span className="text-white font-bold text-2xl">AI</span>
        </motion.div>
        
        {/* Subtle rotating outer ring */}
        <motion.div 
          className="absolute -inset-1 rounded-full border border-white/20"
          animate={{
            rotate: 360
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>
    </motion.div>
  );
} 