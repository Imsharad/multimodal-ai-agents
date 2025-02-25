import React, { useEffect } from 'react';
import { AgentState, BarVisualizer, useVoiceAssistant } from '@livekit/components-react';
import { motion, AnimatePresence } from 'framer-motion';
import { CompanyLogo } from './CompanyLogo';

interface EnhancedVoiceAssistantProps {
  onStateChange: (state: AgentState) => void;
}

/**
 * Enhanced voice assistant component with improved animations for different states
 * - Visual indicator for processing user's voice (listening state - blue color)
 * - Visual indicator for server connected and responding (thinking/speaking states - purple/green colors)
 * - Idle state animation (subtle pulsing animation)
 * - Accessible design with aria-live regions for screen readers
 */
export function EnhancedVoiceAssistant({ onStateChange }: EnhancedVoiceAssistantProps) {
  const { state, audioTrack } = useVoiceAssistant();
  
  useEffect(() => {
    onStateChange(state);
  }, [onStateChange, state]);

  // Define animation variants for different states
  const containerVariants = {
    idle: {
      scale: [1, 1.02, 1],
      opacity: [0.85, 0.95, 0.85],
      transition: { 
        duration: 4, 
        repeat: Infinity, 
        repeatType: 'reverse' as const,
        ease: "easeInOut"
      }
    },
    listening: {
      scale: 1.05,
      opacity: 1,
      transition: { duration: 0.5 }
    },
    thinking: {
      scale: [1, 1.03, 1],
      opacity: 1,
      transition: { 
        duration: 1.8, 
        repeat: Infinity, 
        repeatType: 'reverse' as const,
        ease: "easeInOut"
      }
    },
    speaking: {
      scale: 1,
      opacity: 1,
      transition: { duration: 0.3 }
    },
    connecting: {
      scale: [1, 1.05, 1],
      opacity: [0.7, 0.9, 0.7],
      transition: { 
        duration: 1.5, 
        repeat: Infinity, 
        repeatType: 'reverse' as const,
        ease: "easeInOut"
      }
    },
    disconnected: {
      scale: 0.95,
      opacity: 0.5,
      transition: { duration: 0.5 }
    }
  };

  // Get the current animation variant based on state
  const currentVariant = state in containerVariants ? state : 'idle';

  // Define colors for different states - updated with more vibrant colors
  const stateColors = {
    idle: 'bg-gray-200',
    listening: 'bg-blue-500',
    thinking: 'bg-purple-600',
    speaking: 'bg-emerald-500',
    connecting: 'bg-amber-500',
    disconnected: 'bg-gray-400'
  };

  // Define ring colors for different states
  const ringColors = {
    idle: 'ring-gray-200',
    listening: 'ring-blue-500',
    thinking: 'ring-purple-600',
    speaking: 'ring-emerald-500',
    connecting: 'ring-amber-500',
    disconnected: 'ring-gray-400'
  };

  // Define shadow effects for different states - enhanced for better visual feedback
  const shadowEffects = {
    idle: 'shadow-md',
    listening: 'shadow-lg shadow-blue-500/40',
    thinking: 'shadow-lg shadow-purple-600/40',
    speaking: 'shadow-lg shadow-emerald-500/40',
    connecting: 'shadow-lg shadow-amber-500/40',
    disconnected: 'shadow-none'
  };

  // Get status text based on state
  const getStatusText = () => {
    switch (state) {
      case 'listening': return 'Listening...';
      case 'thinking': return 'Processing...';
      case 'speaking': return 'Responding...';
      case 'connecting': return 'Connecting...';
      case 'disconnected': return 'Disconnected';
      default: return 'Ready';
    }
  };

  // Get aria label for screen readers
  const getAriaLabel = () => {
    switch (state) {
      case 'listening': return 'AI assistant is listening to your voice';
      case 'thinking': return 'AI assistant is processing your request';
      case 'speaking': return 'AI assistant is responding to your query';
      case 'connecting': return 'AI assistant is connecting';
      case 'disconnected': return 'AI assistant is disconnected';
      default: return 'AI assistant is ready to help';
    }
  };

  return (
    <div className="h-[300px] max-w-[90vw] mx-auto relative flex flex-col items-center justify-center">
      {/* Status indicator with improved animation */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`status-${state}`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="absolute top-0 text-sm font-medium mb-2 backdrop-blur-sm bg-white/40 px-3 py-1 rounded-full"
          style={{ 
            color: state === 'listening' ? '#2563eb' : 
                   state === 'thinking' ? '#9333ea' : 
                   state === 'speaking' ? '#10b981' : 
                   state === 'connecting' ? '#f59e0b' : 
                   state === 'disconnected' ? '#6b7280' : '#6b7280'
          }}
        >
          {getStatusText()}
        </motion.div>
      </AnimatePresence>

      {/* Main animation container with improved visual effects */}
      <motion.div
        className={`relative flex items-center justify-center p-8 rounded-full ring-4 ${ringColors[state as keyof typeof ringColors]} ${shadowEffects[state as keyof typeof shadowEffects]}`}
        variants={containerVariants}
        animate={currentVariant}
      >
        {/* Outer ring animations - enhanced for better visual feedback */}
        {(state === 'listening' || state === 'speaking' || state === 'thinking') && (
          <>
            <motion.div
              className={`absolute w-full h-full rounded-full ${stateColors[state as keyof typeof stateColors]} opacity-10`}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.1, 0.05, 0.1]
              }}
              transition={{
                duration: state === 'listening' ? 1.5 : state === 'thinking' ? 2.2 : 1.8,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            <motion.div
              className={`absolute w-full h-full rounded-full ${stateColors[state as keyof typeof stateColors]} opacity-5`}
              animate={{
                scale: [1.05, 1.3, 1.05],
                opacity: [0.05, 0.02, 0.05]
              }}
              transition={{
                duration: state === 'listening' ? 2 : state === 'thinking' ? 2.8 : 2.3,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 0.2
              }}
            />
          </>
        )}

        {/* Background pulse animation for active states - improved timing and effects */}
        {(state === 'listening' || state === 'speaking' || state === 'thinking') && (
          <motion.div
            className={`absolute rounded-full ${stateColors[state as keyof typeof stateColors]} opacity-20`}
            initial={{ width: '100%', height: '100%' }}
            animate={{ 
              width: ['100%', '125%', '100%'], 
              height: ['100%', '125%', '100%'],
              opacity: [0.2, 0.3, 0.2]
            }}
            transition={{ 
              duration: state === 'listening' ? 1.5 : state === 'thinking' ? 2.5 : 2, 
              repeat: Infinity, 
              ease: "easeInOut" 
            }}
          />
        )}

        {/* Enhanced glass effect background with subtle gradient */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm"></div>

        {/* Company logo with improved positioning */}
        <CompanyLogo className="absolute z-10" />

        {/* Voice visualizer with enhanced styling for each state */}
        <div className={`relative z-0 ${state === 'disconnected' ? 'opacity-50' : 'opacity-100'}`}>
          <BarVisualizer
            state={state}
            barCount={32}
            trackRef={audioTrack}
            className={`agent-visualizer ${
              state === 'listening' ? 'listening-visualizer' : 
              state === 'thinking' ? 'thinking-visualizer' : 
              state === 'speaking' ? 'speaking-visualizer' : 'idle-visualizer'
            }`}
            options={{ 
              minHeight: 24,
              maxHeight: state === 'speaking' ? 80 : state === 'listening' ? 65 : 40
            }}
          />
        </div>

        {/* Enhanced state indicator dot with pulse effect */}
        <motion.div 
          className={`absolute bottom-0 w-4 h-4 rounded-full ${stateColors[state as keyof typeof stateColors]}`}
          initial={{ scale: 0.8, opacity: 0.7 }}
          animate={{ 
            scale: [0.8, 1, 0.8], 
            opacity: [0.7, 1, 0.7]
          }}
          transition={{ 
            duration: 2, 
            repeat: Infinity,
            ease: "easeInOut" 
          }}
        />
      </motion.div>

      {/* State description with animated background and improved styling */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`description-${state}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.3 }}
          className={`mt-4 text-sm font-medium px-4 py-1.5 rounded-full backdrop-blur-sm ${
            state === 'listening' ? 'bg-blue-50/70 text-blue-700' : 
            state === 'thinking' ? 'bg-purple-50/70 text-purple-700' : 
            state === 'speaking' ? 'bg-emerald-50/70 text-emerald-700' : 
            state === 'connecting' ? 'bg-amber-50/70 text-amber-700' : 
            state === 'disconnected' ? 'bg-gray-50/70 text-gray-700' : 
            'bg-gray-50/70 text-gray-700'
          }`}
        >
          {state === 'listening' && "I'm listening to you..."}
          {state === 'thinking' && "I'm processing your request..."}
          {state === 'speaking' && "I'm responding to your query..."}
          {state === 'connecting' && "Establishing connection..."}
          {state === 'disconnected' && "Click 'Start a conversation' to begin"}
          {(state as string) === 'idle' && "I'm ready to assist you"}
        </motion.div>
      </AnimatePresence>

      {/* Accessibility: Enhanced aria-live region for screen readers */}
      <div className="sr-only" aria-live="polite" role="status">
        {getAriaLabel()}
      </div>
    </div>
  );
} 