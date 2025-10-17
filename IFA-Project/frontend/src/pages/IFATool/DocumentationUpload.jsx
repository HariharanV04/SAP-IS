import React, { useState, useRef, useEffect } from "react"
import { toast } from "react-hot-toast"
import DocumentationUploadForm from "@pages/common/DocumentationUploadForm"
import ProgressTracker from "@pages/common/ProgressTracker"
import JobResult from "@pages/common/JobResult"
import { uploadDocumentation, generateIflowFromDocs, getJobStatus } from "@services/api"
import { Button, Card, CardBody, Divider } from "@heroui/react"
import { ArrowLeft, FileText, Zap } from "lucide-react"

// Get environment variables for polling configuration
const DISABLE_AUTO_POLLING = import.meta.env.VITE_DISABLE_AUTO_POLLING === 'true'
const DISABLE_AUTO_IFLOW_GENERATION = import.meta.env.VITE_DISABLE_AUTO_IFLOW_GENERATION === 'true'
const MAX_POLL_COUNT = parseInt(import.meta.env.VITE_MAX_POLL_COUNT || '30')
const POLL_INTERVAL_MS = parseInt(import.meta.env.VITE_POLL_INTERVAL_MS || '5000')

const DocumentationUpload = ({ onBack }) => {
  const [jobInfo, setJobInfo] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isGeneratingIflow, setIsGeneratingIflow] = useState(false)
  const [platform, setPlatform] = useState('mulesoft')
  const [startTime, setStartTime] = useState(null)
  const [pollInterval, setPollInterval] = useState(null)
  const [pollCount, setPollCount] = useState(0)
  const [consecutiveErrors, setConsecutiveErrors] = useState(0)
  const [currentStep, setCurrentStep] = useState('upload') // 'upload', 'uploaded', 'generating', 'complete'

  const abortControllerRef = useRef(null)

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [pollInterval])

  const handleDocumentationUpload = async (file, selectedPlatform) => {
    setIsLoading(true)
    setStartTime(Date.now())
    setCurrentStep('upload')

    try {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      abortControllerRef.current = new AbortController()

      const result = await uploadDocumentation(
        file,
        selectedPlatform,
        abortControllerRef.current.signal
      )

      if (result) {
        setJobInfo(result)
        setCurrentStep('uploaded')
        toast.success('Documentation uploaded successfully!')
        
        // Auto-generate iFlow if ready and auto-generation is enabled
        if (result.ready_for_iflow_generation && !DISABLE_AUTO_IFLOW_GENERATION) {
          console.log('Auto-triggering iFlow generation in 1 second...')
          setTimeout(() => {
            handleGenerateIflow(result.job_id)
          }, 1000)
        } else if (result.ready_for_iflow_generation && DISABLE_AUTO_IFLOW_GENERATION) {
          console.log('Auto iFlow generation is disabled. User must manually trigger generation.')
          toast.success('Documentation ready! Click "Generate iFlow" to continue.')
        }
      }
    } catch (error) {
      console.error('Documentation upload failed:', error)
      toast.error(error.message || 'Documentation upload failed')
      setCurrentStep('upload')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateIflow = async (jobId) => {
    setIsGeneratingIflow(true)
    setCurrentStep('generating')

    try {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      abortControllerRef.current = new AbortController()

      const result = await generateIflowFromDocs(
        jobId,
        abortControllerRef.current.signal
      )

      if (result) {
        toast.success('iFlow generation started!')
        
        // Update job info
        setJobInfo(prev => ({
          ...prev,
          ...result,
          status: 'iflow_generation_started'
        }))

        // Start polling for completion
        if (!DISABLE_AUTO_POLLING) {
          startPolling(jobId)
        }
      }
    } catch (error) {
      console.error('iFlow generation failed:', error)
      toast.error(error.message || 'iFlow generation failed')
      setCurrentStep('uploaded')
    } finally {
      setIsGeneratingIflow(false)
    }
  }

  const startPolling = (jobId) => {
    setPollCount(0)
    setConsecutiveErrors(0)

    const interval = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId)
        
        setJobInfo(prev => ({
          ...prev,
          ...status
        }))

        setConsecutiveErrors(0)
        setPollCount(prev => prev + 1)

        // Check if job is complete
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval)
          setPollInterval(null)
          setCurrentStep('complete')
          
          if (status.status === 'completed') {
            toast.success('iFlow generation completed successfully!')
          } else {
            toast.error('iFlow generation failed')
          }
        }

        // Stop polling after max attempts
        if (pollCount >= MAX_POLL_COUNT) {
          clearInterval(interval)
          setPollInterval(null)
          toast.warning('Polling stopped after maximum attempts. Check job status manually.')
        }

      } catch (error) {
        console.error('Polling error:', error)
        setConsecutiveErrors(prev => prev + 1)

        // Stop polling after consecutive errors
        if (consecutiveErrors >= 3) {
          clearInterval(interval)
          setPollInterval(null)
          toast.error('Stopped polling due to consecutive errors')
        }
      }
    }, POLL_INTERVAL_MS)

    setPollInterval(interval)
  }

  const handleReset = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      setPollInterval(null)
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    setJobInfo(null)
    setIsLoading(false)
    setIsGeneratingIflow(false)
    setCurrentStep('upload')
    setPollCount(0)
    setConsecutiveErrors(0)
    setStartTime(null)
  }

  const getStepStatus = (step) => {
    switch (step) {
      case 'upload':
        return currentStep === 'upload' && isLoading ? 'loading' : 
               ['uploaded', 'generating', 'complete'].includes(currentStep) ? 'completed' : 'pending'
      case 'uploaded':
        return currentStep === 'uploaded' ? 'current' :
               ['generating', 'complete'].includes(currentStep) ? 'completed' : 'pending'
      case 'generating':
        return currentStep === 'generating' && isGeneratingIflow ? 'loading' :
               currentStep === 'complete' ? 'completed' :
               currentStep === 'generating' ? 'current' : 'pending'
      case 'complete':
        return currentStep === 'complete' ? 'completed' : 'pending'
      default:
        return 'pending'
    }
  }

  const steps = [
    {
      id: 'upload',
      title: 'Upload Documentation',
      description: 'Upload your integration documentation file',
      icon: FileText,
      status: getStepStatus('upload')
    },
    {
      id: 'uploaded',
      title: 'Documentation Processed',
      description: 'Documentation extracted and prepared for iFlow generation',
      icon: FileText,
      status: getStepStatus('uploaded')
    },
    {
      id: 'generating',
      title: 'Generate iFlow',
      description: 'Creating SAP Integration Suite iFlow from documentation',
      icon: Zap,
      status: getStepStatus('generating')
    },
    {
      id: 'complete',
      title: 'Complete',
      description: 'iFlow generation completed successfully',
      icon: Zap,
      status: getStepStatus('complete')
    }
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Button
            variant="light"
            isIconOnly
            onClick={onBack}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Documentation Upload</h1>
            <p className="text-gray-600">
              Upload documentation directly to generate iFlows without the document generation step
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Upload Form or Progress */}
        <div className="space-y-6">
          {currentStep === 'upload' ? (
            <DocumentationUploadForm
              onUpload={handleDocumentationUpload}
              isLoading={isLoading}
              platform={platform}
              onPlatformChange={setPlatform}
            />
          ) : (
            <Card>
              <CardBody className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Job Progress</h3>
                  <Button
                    variant="light"
                    size="sm"
                    onClick={handleReset}
                  >
                    Start New Upload
                  </Button>
                </div>
                
                <Divider />
                
                {jobInfo && (
                  <div className="space-y-2">
                    <p><strong>Job ID:</strong> {jobInfo.job_id}</p>
                    <p><strong>Platform:</strong> {jobInfo.platform}</p>
                    <p><strong>Status:</strong> {jobInfo.status}</p>
                    {jobInfo.file_info && (
                      <div>
                        <p><strong>File:</strong> {jobInfo.file_info.original_filename}</p>
                        <p><strong>Type:</strong> {jobInfo.file_info.content_type}</p>
                        <p><strong>Size:</strong> {(jobInfo.file_info.file_size / 1024).toFixed(1)} KB</p>
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 'uploaded' && jobInfo?.ready_for_iflow_generation && (
                  <Button
                    color="primary"
                    onClick={() => handleGenerateIflow(jobInfo.job_id)}
                    isLoading={isGeneratingIflow}
                    className="w-full"
                  >
                    {isGeneratingIflow ? 'Starting iFlow Generation...' : 'Generate iFlow'}
                  </Button>
                )}
              </CardBody>
            </Card>
          )}
        </div>

        {/* Right Column - Progress Tracker and Results */}
        <div className="space-y-6">
          <ProgressTracker
            steps={steps}
            currentStep={currentStep}
            startTime={startTime}
            jobInfo={jobInfo}
          />

          {jobInfo && currentStep === 'complete' && (
            <JobResult
              jobInfo={jobInfo}
              platform={platform}
              showIflowGeneration={true}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default DocumentationUpload
