import React, { useState, useRef, useEffect } from 'react';
import { Upload, Check, AlertCircle, Clock } from 'lucide-react';
import { toast } from 'react-hot-toast';
import FileUploadForm from '../components/FileUploadForm';
import ProgressTracker from '../components/ProgressTracker';
import JobResult from '../components/JobResult';
import { generateDocs, getJobStatus } from '../services/api';
import { JobStatus, JobInfo } from '../types';

const Home: React.FC = () => {
  const [jobInfo, setJobInfo] = useState<JobInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [pollInterval, setPollInterval] = useState<number | null>(null);
  const [pollCount, setPollCount] = useState(0);

  const abortControllerRef = useRef<AbortController | null>(null);

  // No longer checking backend connectivity on mount for production

  const startJob = async (files: File[], enhance: boolean) => {
    setIsLoading(true);

    try {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      const formData = new FormData();
      files.forEach(file => formData.append('files[]', file));
      formData.append('enhance', enhance.toString());

      const result = await generateDocs(formData, abortControllerRef.current.signal);

      if (result) {
        // Initialize notification state for the new job
        setHasNotifiedCompletion({
          [result.job_id]: { status: false, iflow: false }
        });

        setJobInfo({
          id: result.job_id,
          status: 'queued',
          created: new Date().toISOString(),
          last_updated: new Date().toISOString(),
          enhance: enhance,
          files: null,
          processing_step: null,
          processing_message: 'Job started successfully. Processing files...',
          file_info: null,
          parsed_details: null,
          error: null
        });

        // Set the start time
        setStartTime(new Date());

        // Start polling
        startPolling(result.job_id, enhance);

        toast.success('Documentation generation started!');
      }
    } catch (error) {
      toast.error('Failed to start documentation generation');
      console.error('Error starting job:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startPolling = (jobId: string, isEnhancement: boolean) => {
    // Clear any existing polling
    if (pollInterval) {
      clearInterval(pollInterval);
    }

    setPollCount(0);

    // Start polling at 2-second intervals
    const interval = setInterval(() => {
      setPollCount(prev => prev + 1);
      checkJobStatus(jobId);

      // Gradually increase the polling interval if LLM enhancement is happening
      if (isEnhancement && pollCount > 15) {
        clearInterval(interval);
        const newInterval = setInterval(() => {
          checkJobStatus(jobId);
        }, 5000);
        setPollInterval(newInterval);
      }
    }, 2000);

    setPollInterval(interval);
  };

  // Keep track of job completion notification state
  const [hasNotifiedCompletion, setHasNotifiedCompletion] = useState<Record<string, Record<string, boolean>>>({});

  const checkJobStatus = async (jobId: string) => {
    try {
      const data = await getJobStatus(jobId);

      if (data) {
        // Update job info state
        setJobInfo(data);

        // If job is complete or failed, stop polling
        if (data.status === 'completed' || data.status === 'failed') {
          if (pollInterval) {
            clearInterval(pollInterval);
            setPollInterval(null);
          }

          // Initialize job notification state if needed
          if (!hasNotifiedCompletion[jobId]) {
            setHasNotifiedCompletion(prev => ({
              ...prev,
              [jobId]: { status: false, iflow: false }
            }));
          }

          // Only show toast notification if we haven't shown it before for this job's status
          if (hasNotifiedCompletion[jobId] && !hasNotifiedCompletion[jobId].status) {
            if (data.status === 'completed') {
              toast.success('Documentation generation completed!');
            } else {
              toast.error(`Job failed: ${data.error || 'Unknown error'}`);
            }

            // Mark this job's status as having been notified
            setHasNotifiedCompletion(prev => ({
              ...prev,
              [jobId]: { ...prev[jobId], status: true }
            }));
          }

          // Check for iFlow match completion
          if (data.iflow_match_status === 'completed' &&
              hasNotifiedCompletion[jobId] &&
              !hasNotifiedCompletion[jobId].iflow) {
            // Mark iFlow notification as completed to prevent future notifications
            setHasNotifiedCompletion(prev => ({
              ...prev,
              [jobId]: { ...prev[jobId], iflow: true }
            }));

            // Show iFlow completion notification
            toast.success('SAP Integration Suite equivalent search completed!');
          }
        }
      }
    } catch (error) {
      console.error('Error checking job status:', error);
      // Don't stop polling on error to allow for temporary network issues
    }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [pollInterval]);

  return (
    <div className="space-y-8">
      {/* Title removed as requested */}

      {/* Connection status is hidden in production */}

      {!jobInfo || (jobInfo.status === 'failed' && !isLoading) ? (
        <FileUploadForm onSubmit={startJob} isLoading={isLoading} />
      ) : (
        <div className="space-y-6 animate-fadeIn">
          <ProgressTracker
            status={jobInfo.status}
            processingStep={jobInfo.processing_step}
            isEnhancement={jobInfo.enhance}
            startTime={startTime}
            pollCount={pollCount}
            statusMessage={jobInfo.processing_message}
          />

          <JobResult
            jobInfo={jobInfo}
            onNewJob={() => {
              // Reset job info
              setJobInfo(null);
              // Reset notification state (initialize with empty object)
              setHasNotifiedCompletion({});
              // Clear any existing polling
              if (pollInterval) {
                clearInterval(pollInterval);
                setPollInterval(null);
              }
            }}
          />
        </div>
      )}
    </div>
  );
};

export default Home;