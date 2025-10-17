import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';
import { JobStatus } from '../types';

interface ProgressTrackerProps {
  status: JobStatus;
  processingStep: string | null;
  isEnhancement: boolean;
  startTime: Date | null;
  pollCount: number;
  statusMessage: string | null;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  status,
  processingStep,
  isEnhancement,
  startTime,
  pollCount,
  statusMessage
}) => {
  const [elapsedTime, setElapsedTime] = useState<string>('0s');
  
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    
    if (startTime) {
      interval = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now.getTime() - startTime.getTime()) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        setElapsedTime(`${minutes}m ${seconds}s`);
      }, 1000);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [startTime]);
  
  // Calculate progress percentage based on status and processing step
  const getProgressPercentage = (): number => {
    let percentage = 5; // Default starting percentage
    
    if (status === 'queued') {
      percentage = 5;
    } else if (status === 'processing') {
      // Calculate percentage based on processing step
      if (processingStep === 'file_analysis') {
        percentage = 15;
      } else if (processingStep === 'mule_parsing') {
        percentage = 30;
      } else if (processingStep === 'visualization') {
        percentage = 45;
      } else if (processingStep === 'llm_enhancing') {
        percentage = 60;
      } else if (processingStep === 'llm_complete') {
        percentage = 85;
      } else if (processingStep === 'llm_failed') {
        percentage = 85;
      } else {
        // Fallback to calculation based on poll count
        if (isEnhancement) {
          percentage = Math.min(80, 10 + (pollCount * 2));
        } else {
          percentage = Math.min(90, 10 + (pollCount * 5));
        }
      }
    } else if (status === 'completed') {
      percentage = 100;
    } else if (status === 'failed') {
      percentage = 100;
    }
    
    return percentage;
  };
  
  // Get the progress text based on status and processing step
  const getProgressText = (): string => {
    if (status === 'queued') {
      return 'Queued...';
    } else if (status === 'processing') {
      if (processingStep === 'file_analysis') {
        return 'Analyzing files...';
      } else if (processingStep === 'mule_parsing') {
        return 'Parsing MuleSoft files...';
      } else if (processingStep === 'visualization') {
        return 'Generating visualization...';
      } else if (processingStep === 'llm_enhancing') {
        return 'AI Enhancement...';
      } else if (processingStep === 'llm_complete') {
        return 'Finalizing...';
      } else if (processingStep === 'llm_failed') {
        return 'LLM failed, finishing...';
      } else {
        return 'Processing...';
      }
    } else if (status === 'completed') {
      return 'Completed!';
    } else if (status === 'failed') {
      return 'Failed';
    } else {
      return 'Unknown status';
    }
  };
  
  // Get progress bar color based on status
  const getProgressBarColor = (): string => {
    if (status === 'failed') {
      return 'bg-red-500';
    } else if (processingStep === 'llm_failed') {
      return 'bg-company-orange-500';
    } else {
      return 'bg-company-orange-600';
    }
  };

  const percentage = getProgressPercentage();
  const progressText = getProgressText();
  const progressBarColor = getProgressBarColor();

  // Should we show the LLM enhancement message?
  const showLLMMessage = isEnhancement && status === 'processing' && 
    (processingStep === 'llm_enhancing' || (!processingStep && pollCount > 15));

  return (
    <div className="bg-white shadow-sm rounded-lg p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Job Progress</h3>
        <div className="flex items-center text-gray-600 text-sm">
          <Clock className="h-4 w-4 mr-1" />
          <span>Elapsed time: {elapsedTime}</span>
        </div>
      </div>
      
      <div className="relative h-6 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${progressBarColor} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
        <div className="absolute inset-0 flex items-center justify-center text-sm font-medium">
          {progressText}
        </div>
      </div>
      
      <div className={`p-3 rounded-md ${status === 'failed' ? 'bg-red-50 text-red-800' : 'bg-company-orange-50 text-company-orange-800'}`}>
        {statusMessage || `Status: ${status}`}
      </div>
      
      {showLLMMessage && (
        <div className="p-3 rounded-md bg-company-orange-50 text-company-orange-800 animate-pulse">
          The AI enhancement process is running and may take 1-2 minutes to complete.
          Documentation generation will continue automatically.
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;