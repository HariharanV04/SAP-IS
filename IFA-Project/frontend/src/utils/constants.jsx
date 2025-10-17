export const APP_NAME = 'IS-Migration'
export const CREDIT_NAME = 'IT Resonance, Inc.'
export const DATE_FORMAT = 'DD-MM-YYYY'
export const TIME_FORMAT = 'hh:mm a'
export const DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT
export const JOB_ID_FORMAT = "ITRES_"
export const DATA_USER = 5;
export const RECRUITR = 4;
export const RECRUITR_MANAGER = 3;
export const MANAGER = 2;

// LLM Provider constants
export const LLM_PROVIDERS = {
  ANTHROPIC: 'anthropic',
  GEMMA3: 'gemma3'
};

export const LLM_PROVIDER_LABELS = {
  [LLM_PROVIDERS.ANTHROPIC]: 'Premium AI Model',
  [LLM_PROVIDERS.GEMMA3]: 'Gemma3 (Open Source)'
};

export const LLM_PROVIDER_DESCRIPTIONS = {
  [LLM_PROVIDERS.ANTHROPIC]: 'High-quality commercial AI model with excellent reasoning capabilities',
  [LLM_PROVIDERS.GEMMA3]: 'Open source model running on RunPod with cost-effective processing'
};

export const LLM_PROVIDER_FEATURES = {
  [LLM_PROVIDERS.ANTHROPIC]: {
    maxTokens: '200K',
    speed: 'Fast',
    quality: 'Excellent',
    cost: 'Premium'
  },
  [LLM_PROVIDERS.GEMMA3]: {
    maxTokens: '8K',
    speed: 'Moderate',
    quality: 'Good',
    cost: 'Low'
  }
};