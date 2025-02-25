import React from 'react';
import { motion } from 'framer-motion';

interface CompanyLogoProps {
  className?: string;
}

/**
 * Enhanced company logo component with improved animations
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
        duration: 3.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {/* Enhanced placeholder logo - replace with actual logo when available */}
      <div className="relative w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 flex items-center justify-center shadow-lg">
        {/* Improved animated gradient background with smoother transitions */}
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
            duration: 10,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        
        {/* Enhanced glow effect with better blur */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 opacity-60 blur-md"></div>
        
        {/* Improved inner highlight with subtle gradient */}
        <div className="absolute inset-1 rounded-full bg-gradient-to-br from-white/30 to-transparent"></div>
        
        {/* Logo text with enhanced animation */}
        <motion.div 
          className="relative z-10 flex items-center justify-center"
          animate={{
            textShadow: [
              '0 0 5px rgba(255,255,255,0.5)',
              '0 0 10px rgba(255,255,255,0.8)',
              '0 0 5px rgba(255,255,255,0.5)'
            ]
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <span className="text-white font-bold text-2xl">AI</span>
        </motion.div>
        
        {/* Enhanced rotating outer ring with subtle glow */}
        <motion.div 
          className="absolute -inset-1 rounded-full border border-white/30"
          animate={{
            rotate: 360,
            boxShadow: [
              '0 0 5px rgba(255,255,255,0.2)',
              '0 0 8px rgba(255,255,255,0.3)',
              '0 0 5px rgba(255,255,255,0.2)'
            ]
          }}
          transition={{
            rotate: {
              duration: 25,
              repeat: Infinity,
              ease: "linear"
            },
            boxShadow: {
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }
          }}
        />
        
        {/* Additional subtle pulsing ring */}
        <motion.div 
          className="absolute -inset-2 rounded-full border-2 border-white/10"
          animate={{
            scale: [1, 1.05, 1],
            opacity: [0.1, 0.2, 0.1]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>
    </motion.div>
  );
} 