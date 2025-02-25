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
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 opacity-50 blur-sm"></div>
        <div className="relative z-10 flex items-center justify-center">
          <span className="text-white font-bold text-2xl">AI</span>
        </div>
      </div>
    </motion.div>
  );
} 