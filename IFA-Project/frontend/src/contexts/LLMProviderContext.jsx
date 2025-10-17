import React, { createContext, useContext, useState, useEffect } from 'react';
import { LLM_PROVIDERS } from '@utils/constants';

const LLMProviderContext = createContext();

export const useLLMProvider = () => {
  const context = useContext(LLMProviderContext);
  if (!context) {
    throw new Error('useLLMProvider must be used within a LLMProviderProvider');
  }
  return context;
};

export const LLMProviderProvider = ({ children }) => {
  // Default to Anthropic for backward compatibility
  const [selectedLLMProvider, setSelectedLLMProvider] = useState(() => {
    // Try to get from localStorage first
    const saved = localStorage.getItem('selectedLLMProvider');
    return saved || LLM_PROVIDERS.ANTHROPIC;
  });

  // Save to localStorage whenever provider changes
  useEffect(() => {
    localStorage.setItem('selectedLLMProvider', selectedLLMProvider);
  }, [selectedLLMProvider]);

  const value = {
    selectedLLMProvider,
    setSelectedLLMProvider,
    isAnthropic: selectedLLMProvider === LLM_PROVIDERS.ANTHROPIC,
    isGemma3: selectedLLMProvider === LLM_PROVIDERS.GEMMA3
  };

  return (
    <LLMProviderContext.Provider value={value}>
      {children}
    </LLMProviderContext.Provider>
  );
};
