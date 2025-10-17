import React from 'react';
import { Card, CardBody, Button, Chip, Progress } from '@heroui/react';
import { LLM_PROVIDERS, LLM_PROVIDER_LABELS, LLM_PROVIDER_DESCRIPTIONS, LLM_PROVIDER_FEATURES } from '@utils/constants';

const LLMProviderSelector = ({ selectedProvider, onProviderChange, className = "" }) => {
  const providers = [
    {
      id: LLM_PROVIDERS.ANTHROPIC,
      label: LLM_PROVIDER_LABELS[LLM_PROVIDERS.ANTHROPIC],
      description: LLM_PROVIDER_DESCRIPTIONS[LLM_PROVIDERS.ANTHROPIC],
      features: LLM_PROVIDER_FEATURES[LLM_PROVIDERS.ANTHROPIC],
      color: 'primary',
      icon: '🧠',
      badge: 'Premium'
    },
    {
      id: LLM_PROVIDERS.GEMMA3,
      label: LLM_PROVIDER_LABELS[LLM_PROVIDERS.GEMMA3],
      description: LLM_PROVIDER_DESCRIPTIONS[LLM_PROVIDERS.GEMMA3],
      features: LLM_PROVIDER_FEATURES[LLM_PROVIDERS.GEMMA3],
      color: 'secondary',
      icon: '🔓',
      badge: 'Open Source'
    }
  ];

  const handleProviderSelect = (providerId) => {
    localStorage.setItem('selectedLLMProvider', providerId);
    if (onProviderChange) {
      onProviderChange(providerId);
    }
  };

  const getQualityColor = (quality) => {
    switch (quality.toLowerCase()) {
      case 'excellent': return 'success';
      case 'good': return 'warning';
      default: return 'default';
    }
  };

  const getSpeedValue = (speed) => {
    switch (speed.toLowerCase()) {
      case 'fast': return 90;
      case 'moderate': return 60;
      case 'slow': return 30;
      default: return 50;
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          Select AI Model Provider
        </h3>
        <p className="text-gray-600 text-sm">
          Choose the AI model for integration flow generation
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {providers.map((provider) => (
          <Card
            key={provider.id}
            className={`cursor-pointer transition-all duration-200 hover:scale-105 ${
              selectedProvider === provider.id
                ? 'ring-2 ring-blue-500 shadow-lg'
                : 'hover:shadow-md'
            }`}
            isPressable
            onPress={() => handleProviderSelect(provider.id)}
          >
            <CardBody className="p-4">
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{provider.icon}</span>
                    <div>
                      <h4 className="font-semibold text-gray-800 text-sm">
                        {provider.label}
                      </h4>
                      <Chip 
                        size="sm" 
                        variant="flat" 
                        color={provider.color}
                        className="text-xs"
                      >
                        {provider.badge}
                      </Chip>
                    </div>
                  </div>
                  {selectedProvider === provider.id && (
                    <Chip color="success" size="sm" variant="flat">
                      Selected
                    </Chip>
                  )}
                </div>

                {/* Description */}
                <p className="text-gray-600 text-xs leading-relaxed">
                  {provider.description}
                </p>

                {/* Features */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Max Tokens:</span>
                    <span className="text-xs font-medium">{provider.features.maxTokens}</span>
                  </div>
                  
                  <div className="space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">Speed:</span>
                      <span className="text-xs font-medium">{provider.features.speed}</span>
                    </div>
                    <Progress 
                      value={getSpeedValue(provider.features.speed)} 
                      size="sm" 
                      color="primary"
                      className="max-w-full"
                    />
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Quality:</span>
                    <Chip 
                      size="sm" 
                      variant="flat" 
                      color={getQualityColor(provider.features.quality)}
                      className="text-xs"
                    >
                      {provider.features.quality}
                    </Chip>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Cost:</span>
                    <span className="text-xs font-medium">{provider.features.cost}</span>
                  </div>
                </div>

                {/* Selection Button */}
                <Button
                  color={provider.color}
                  variant={selectedProvider === provider.id ? "solid" : "bordered"}
                  size="sm"
                  className="w-full"
                >
                  {selectedProvider === provider.id ? 'Selected' : 'Select'}
                </Button>

                {/* Special notes */}
                {provider.id === LLM_PROVIDERS.GEMMA3 && (
                  <div className="bg-orange-50 p-2 rounded text-xs text-orange-700">
                    <strong>Note:</strong> May require chunking for large documents due to token limits
                  </div>
                )}
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {selectedProvider && (
        <div className="text-center">
          <Chip color="primary" variant="flat" size="lg">
            Using {LLM_PROVIDER_LABELS[selectedProvider]} for integration flow generation
          </Chip>
        </div>
      )}
    </div>
  );
};

export default LLMProviderSelector;
