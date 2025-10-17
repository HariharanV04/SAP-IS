import React, { useState, useRef, useEffect } from "react"
import { toast } from "react-hot-toast"
import FileUploadForm from "@pages/common/FileUploadForm"
import ProgressTracker from "@pages/common/ProgressTracker"
import JobResult from "@pages/common/JobResult"
import LLMProviderSelector from "@components/LLMProviderSelector"
import { generateDocs, getJobStatus, uploadDocumentation, generateIflowFromDocs } from "@services/api"
import { useLLMProvider } from "@/contexts/LLMProviderContext"
import { LLM_PROVIDER_LABELS } from "@utils/constants"
import { Button, Card, CardBody, Divider, Tabs, Tab, Select, SelectItem } from "@heroui/react"
import { Upload, FileText, Code, Zap, ChevronDown, Clock, CheckCircle, XCircle, AlertCircle, MoreVertical, Calendar, User, Activity } from "lucide-react"

// Get environment variables for polling configuration
const DISABLE_AUTO_POLLING = import.meta.env.VITE_DISABLE_AUTO_POLLING === 'true'
const MAX_POLL_COUNT = parseInt(import.meta.env.VITE_MAX_POLL_COUNT || '30')
const POLL_INTERVAL_MS = parseInt(import.meta.env.VITE_POLL_INTERVAL_MS || '5000')
const INITIAL_POLL_INTERVAL_MS = 2000 // Start with a faster polling interval

// No more mock data - we'll fetch real jobs from Supabase

// Jobs History Panel Component
const JobsHistoryPanel = () => {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch jobs from API
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/jobs?limit=20')
        const data = await response.json()

        if (data.success) {
          setJobs(data.jobs || [])
          setError(null)
        } else {
          setError('Failed to load jobs')
        }
      } catch (err) {
        console.error('Error fetching jobs:', err)
        setError('Unable to connect to server')
      } finally {
        setLoading(false)
      }
    }

    fetchJobs()

    // Refresh jobs every 30 seconds
    const interval = setInterval(fetchJobs, 30000)

    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'processing':
      case 'analyzing':
      case 'generating':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'documentation_ready':
        return <FileText className="w-4 h-4 text-purple-500" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
      case 'analyzing':
      case 'generating':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'documentation_ready':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))

    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    return date.toLocaleDateString()
  }

  const formatDuration = (durationSeconds) => {
    if (!durationSeconds) return 'N/A'
    const minutes = Math.floor(durationSeconds / 60)
    const seconds = durationSeconds % 60
    return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`
  }

  return (
    <Card className="h-fit">
      <CardBody className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Recent Jobs</h3>
          </div>
          <span className="text-sm text-gray-500">
            {loading ? '...' : `${jobs.length} jobs`}
          </span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="ml-3 text-sm text-gray-600">Loading jobs...</span>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-8 text-red-600">
            <XCircle className="w-5 h-5 mr-2" />
            <span className="text-sm">{error}</span>
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-gray-500">
            <AlertCircle className="w-8 h-8 mb-2" />
            <span className="text-sm">No jobs yet</span>
            <span className="text-xs mt-1">Upload documentation to get started</span>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div
                key={job.job_id}
                className="group p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all duration-200 cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(job.status)}
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {job.iflow_name || job.source_file_name || 'Untitled Job'}
                      </h4>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(job.created_at)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDuration(job.duration_seconds)}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                      <span className="px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-700">
                        {job.platform || 'unknown'}
                      </span>
                      {job.total_components > 0 && (
                        <span className="text-xs text-gray-500">
                          {job.total_components} component{job.total_components !== 1 ? 's' : ''}
                        </span>
                      )}
                      {job.progress !== undefined && job.status !== 'completed' && job.status !== 'failed' && (
                        <span className="text-xs text-blue-600 font-medium">
                          {job.progress}%
                        </span>
                      )}
                    </div>
                  </div>

                  <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition-opacity">
                    <MoreVertical className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 pt-4 border-t border-gray-200">
          <button className="w-full text-sm text-blue-600 hover:text-blue-700 font-medium">
            View all jobs
          </button>
        </div>
      </CardBody>
    </Card>
  )
}

// Unified Documentation Upload Component
const UnifiedDocumentationUpload = ({ onSubmit, isLoading, selectedPlatform, uploadProgress = 0, uploadStatus = "" }) => {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (file) {
      onSubmit(file)
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const removeFile = () => {
    setFile(null)
  }

  return (
    <Card>
      <CardBody className="p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Upload Documentation
              </h2>
              <p className="text-gray-600">
                Upload business documentation to automatically generate {selectedPlatform === 'mulesoft' ? 'MuleSoft' : 'Boomi'} iFlows
              </p>
            </div>
          </div>

          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
              dragActive
                ? "border-blue-400 bg-blue-50 scale-[1.02]"
                : "border-gray-300 hover:border-blue-300 hover:bg-gray-50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.doc,.txt,.md,.json"
              className="hidden"
            />

            {file ? (
              <div className="space-y-4">
                <div className="flex items-center gap-4 p-4 bg-green-50 border border-green-200 rounded-xl">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <FileText className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-green-900 truncate">{file.name}</p>
                    <div className="flex items-center gap-4 text-sm text-green-600">
                      <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                      <span className="flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        Ready to upload
                      </span>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="light"
                    size="sm"
                    onClick={removeFile}
                    className="text-red-600 hover:text-red-700"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                <div>
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Drop your documentation here
                  </p>
                  <p className="text-gray-600 mb-4">
                    Supported formats: PDF, Word (.docx), Text (.txt), Markdown (.md), JSON
                  </p>
                  <Button
                    type="button"
                    variant="bordered"
                    onClick={handleBrowseClick}
                    startContent={<Upload className="w-4 h-4" />}
                  >
                    Browse Files
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Progress Bar Section */}
          {isLoading && (
            <div className="space-y-4 p-6 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-blue-900">Processing Documentation</h3>
                <span className="text-sm text-blue-600">{uploadProgress}%</span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-blue-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>

              {/* Status Message */}
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm text-blue-700">
                  {uploadStatus || "Processing your documentation..."}
                </span>
              </div>

              {/* Progress Steps */}
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className={`text-center p-2 rounded ${uploadProgress >= 30 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  <div className={`w-6 h-6 mx-auto mb-1 rounded-full flex items-center justify-center text-xs font-bold ${uploadProgress >= 30 ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'}`}>
                    {uploadProgress >= 30 ? '✓' : '1'}
                  </div>
                  <span className="text-xs">Upload</span>
                </div>
                <div className={`text-center p-2 rounded ${uploadProgress >= 60 ? 'bg-green-100 text-green-700' : uploadProgress >= 30 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>
                  <div className={`w-6 h-6 mx-auto mb-1 rounded-full flex items-center justify-center text-xs font-bold ${uploadProgress >= 60 ? 'bg-green-500 text-white' : uploadProgress >= 30 ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-600'}`}>
                    {uploadProgress >= 60 ? '✓' : uploadProgress >= 30 ? '⚡' : '2'}
                  </div>
                  <span className="text-xs">Process</span>
                </div>
                <div className={`text-center p-2 rounded ${uploadProgress >= 100 ? 'bg-green-100 text-green-700' : uploadProgress >= 60 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>
                  <div className={`w-6 h-6 mx-auto mb-1 rounded-full flex items-center justify-center text-xs font-bold ${uploadProgress >= 100 ? 'bg-green-500 text-white' : uploadProgress >= 60 ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-600'}`}>
                    {uploadProgress >= 100 ? '✓' : uploadProgress >= 60 ? '⚡' : '3'}
                  </div>
                  <span className="text-xs">Ready</span>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-center">
            <Button
              type="submit"
              color="primary"
              size="lg"
              isLoading={isLoading}
              isDisabled={!file || isLoading}
              startContent={!isLoading && <Zap className="w-5 h-5" />}
              className="px-8"
            >
              {isLoading ? "Processing..." : "Upload & Generate iFlow"}
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  )
}

const View = () => {
  const { selectedLLMProvider, setSelectedLLMProvider } = useLLMProvider();
  const [jobInfo, setJobInfo] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [startTime, setStartTime] = useState(null)
  const [pollInterval, setPollInterval] = useState(null)
  const [pollCount, setPollCount] = useState(0)
  const [consecutiveErrors, setConsecutiveErrors] = useState(0)
  const [showLLMSelector, setShowLLMSelector] = useState(false)

  const [uploadType, setUploadType] = useState('source_code') // 'source_code' or 'documentation'
  const [selectedPlatform, setSelectedPlatform] = useState('mulesoft') // 'mulesoft' or 'boomi'

  // Debug logging for state changes
  useEffect(() => {
    console.log('Upload Type changed to:', uploadType);
  }, [uploadType]);

  useEffect(() => {
    console.log('Selected Platform changed to:', selectedPlatform);
  }, [selectedPlatform]);
  const [isGeneratingIflow, setIsGeneratingIflow] = useState(false)
  const [currentStep, setCurrentStep] = useState('upload') // 'upload', 'uploaded', 'generating', 'complete'
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState("")

  const abortControllerRef = useRef(null)

  // No longer checking backend connectivity on mount for production

  const startJob = async (files, enhance, platform = null) => {
    // Use selected platform if not provided
    const targetPlatform = platform || selectedPlatform

    setIsLoading(true)
    setCurrentStep('upload')

    try {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      abortControllerRef.current = new AbortController()

      const formData = new FormData()
      files.forEach(file => formData.append("files[]", file))
      formData.append("enhance", enhance.toString())
      formData.append("platform", targetPlatform)

      const result = await generateDocs(
        formData,
        abortControllerRef.current.signal
      )

      if (result) {
        // Initialize notification state for the new job
        setHasNotifiedCompletion({
          [result.job_id]: { status: false, iflow: false }
        })

        setJobInfo({
          id: result.job_id,
          status: "queued",
          created: new Date().toISOString(),
          last_updated: new Date().toISOString(),
          enhance: enhance,
          files: null,
          processing_step: null,
          processing_message: "Job started successfully. Processing files...",
          file_info: null,
          parsed_details: null,
          error: null
        })

        // Set the start time
        setStartTime(new Date())

        // Start polling
        startPolling(result.job_id, enhance)

        toast.success("Documentation generation started!")
      }
    } catch (error) {
      toast.error("Failed to start documentation generation")
      console.error("Error starting job:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const startDocumentationJob = async (file) => {
    setIsLoading(true)
    setCurrentStep('upload')
    setUploadProgress(0)
    setUploadStatus("Preparing upload...")

    try {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      abortControllerRef.current = new AbortController()

      // Progress: Starting upload
      setUploadProgress(10)
      setUploadStatus("Uploading documentation...")

      const result = await uploadDocumentation(
        file,
        selectedPlatform,
        abortControllerRef.current.signal
      )

      // Progress: Upload completed
      setUploadProgress(30)
      setUploadStatus("Processing document content...")

      if (result) {
        // Progress: Documentation processed
        setUploadProgress(60)
        setUploadStatus("Converting to structured markdown...")

        // Initialize notification state for the new job
        setHasNotifiedCompletion({
          [result.job_id]: { status: false, iflow: false }
        })

        setJobInfo({
          id: result.job_id,
          status: "documentation_ready",
          created: new Date().toISOString(),
          last_updated: new Date().toISOString(),
          enhance: false,
          files: null,
          processing_step: null,
          processing_message: "Documentation processed successfully. Ready for iFlow generation.",
          file_info: null,
          parsed_details: null,
          error: null
        })

        // Set the start time
        setStartTime(new Date())
        setCurrentStep('uploaded')

        // Progress: Documentation processing complete
        setUploadProgress(100)
        setUploadStatus("Documentation processed successfully! Ready for iFlow generation.")

        // Start polling to monitor job status changes (including iFlow generation)
        startPolling(result.job_id, false)

        toast.success("Documentation uploaded successfully!")
      }
    } catch (error) {
      setUploadProgress(0)
      setUploadStatus("Upload failed")
      toast.error("Failed to upload documentation")
      console.error("Error uploading documentation:", error)
    } finally {
      setIsLoading(false)
      // Reset progress after a delay if not successful
      setTimeout(() => {
        if (uploadProgress < 100) {
          setUploadProgress(0)
          setUploadStatus("")
        }
      }, 3000)
    }
  }

  const handleGenerateIflow = async (jobId) => {
    setIsGeneratingIflow(true)
    setCurrentStep('generating')

    try {
      const result = await generateIflowFromDocs(jobId)

      if (result) {
        // Update job info to show iFlow generation started
        setJobInfo(prev => ({
          ...prev,
          status: "generating_iflow",
          processing_message: "iFlow generation started..."
        }))

        // Start polling for iFlow generation completion
        startPolling(jobId, false)

        toast.success("iFlow generation started!")
      }
    } catch (error) {
      toast.error("Failed to start iFlow generation")
      console.error("Error generating iFlow:", error)
      setCurrentStep('uploaded')
    } finally {
      setIsGeneratingIflow(false)
    }
  }

  const startPolling = (jobId, isEnhancement) => {
    // Clear any existing polling
    if (pollInterval) {
      clearInterval(pollInterval)
    }

    // Reset poll count and error count
    setPollCount(0)
    setConsecutiveErrors(0)

    // Check if auto-polling is disabled in production
    if (DISABLE_AUTO_POLLING) {
      console.log("Auto-polling is disabled by environment configuration")
      // Make a single request to get initial status
      checkJobStatus(jobId)

      // Schedule a single follow-up check after a short delay
      // This helps ensure we catch quick job completions
      setTimeout(() => {
        console.log("Performing one follow-up status check...")
        checkJobStatus(jobId)
      }, 5000)

      return
    }

    // Log if this is an enhanced job
    if (isEnhancement) {
      console.log("Enhanced documentation job detected - may take longer to complete")
    }

    // Function to perform a single poll
    const performPoll = async () => {
      // Increment poll count
      setPollCount(prev => {
        const newCount = prev + 1
        console.log(`Poll #${newCount} for job ${jobId}`)
        return newCount
      })

      // Check job status first
      await checkJobStatus(jobId)

      // After checking status, see if we've reached the maximum number of polls
      // This needs to be checked after setPollCount has been processed
      const currentPollCount = pollCount + 1 // Add 1 because setPollCount is asynchronous
      if (currentPollCount >= MAX_POLL_COUNT) {
        console.log(`Reached maximum poll count (${MAX_POLL_COUNT}). Stopping polling.`)
        if (pollInterval) {
          clearInterval(pollInterval)
          setPollInterval(null)
        }
      }
    }

    // Start with initial polling interval
    const interval = setInterval(performPoll, INITIAL_POLL_INTERVAL_MS)
    setPollInterval(interval)

    // After 15 polls, switch to the configured polling interval for slower polling
    setTimeout(() => {
      if (pollInterval === interval) { // Only if this interval is still active
        clearInterval(interval)
        const newInterval = setInterval(performPoll, POLL_INTERVAL_MS)
        setPollInterval(newInterval)
        console.log(`Switched to slower polling interval: ${POLL_INTERVAL_MS}ms`)
      }
    }, INITIAL_POLL_INTERVAL_MS * 15)
  }

  // Keep track of job completion notification state
  const [hasNotifiedCompletion, setHasNotifiedCompletion] = useState({})

  const checkJobStatus = async jobId => {
    try {
      console.log(`Checking status for job ${jobId}...`)
      const data = await getJobStatus(jobId, jobInfo)

      if (data) {
        // Reset consecutive errors counter on successful API call
        setConsecutiveErrors(0)

        // Check if the job ID has changed
        if (data.id && data.id !== jobId) {
          console.warn(`Job ID changed from ${jobId} to ${data.id}. This could cause polling issues.`)
        }

        // Log the job status for debugging
        console.log(`🔍 FRONTEND POLLING - Job status: ${data.status}, Processing step: ${data.processing_step}`)
        console.log(`🔍 FRONTEND POLLING - Deployment status: ${data.deployment_status}, Deployment message: ${data.deployment_message}`)
        console.log(`🔍 FRONTEND POLLING - Full job data:`, data)

        // Update job info state
        setJobInfo(data)

        // If job is failed, stop polling
        // But if job is completed, only stop polling if deployment is also completed or failed
        if (data.status === "failed" ||
            (data.status === "completed" &&
             (data.deployment_status === "completed" || data.deployment_status === "failed"))) {
          console.log(`Job ${jobId} ${data.status} with deployment status ${data.deployment_status}. Stopping polling.`)

          if (pollInterval) {
            clearInterval(pollInterval)
            setPollInterval(null)
          }
        } else if (data.status === "completed" && !data.deployment_status) {
          console.log(`Job ${jobId} completed but no deployment status yet. Continuing polling for deployment updates.`)
        }

          // Initialize job notification state if needed
          if (!hasNotifiedCompletion[jobId]) {
            setHasNotifiedCompletion(prev => ({
              ...prev,
              [jobId]: { status: false, iflow: false }
            }))
          }

          // Only show toast notification if we haven't shown it before for this job's status
          if (
            hasNotifiedCompletion[jobId] &&
            !hasNotifiedCompletion[jobId].status
          ) {
            if (data.status === "completed") {
              toast.success("Documentation generation completed!")
            } else {
              toast.error(`Job failed: ${data.error || "Unknown error"}`)
            }

            // Mark this job's status as having been notified
            setHasNotifiedCompletion(prev => ({
              ...prev,
              [jobId]: { ...prev[jobId], status: true }
            }))
          }

          // Check for iFlow match completion
          if (
            data.iflow_match_status === "completed" &&
            hasNotifiedCompletion[jobId] &&
            !hasNotifiedCompletion[jobId].iflow
          ) {
            // Mark iFlow notification as completed to prevent future notifications
            setHasNotifiedCompletion(prev => ({
              ...prev,
              [jobId]: { ...prev[jobId], iflow: true }
            }))

            // Show iFlow completion notification
            toast.success("SAP Integration Suite equivalent search completed!")
          }
      } else {
        console.log(`Job ${jobId} status: ${data.status}`)
      }
    } catch (error) {
      console.error("Error checking job status:", error)

      // Increment error count for consecutive failures
      setConsecutiveErrors(prev => prev + 1)

      // If we've had too many consecutive errors, stop polling
      if (consecutiveErrors > 3 && pollInterval) {
        console.error("Too many consecutive errors. Stopping polling.")
        clearInterval(pollInterval)
        setPollInterval(null)
        toast.error("Lost connection to the server. Please refresh the page.")
      }
    }
  }

  // Effect to handle job status changes
  useEffect(() => {
    if (jobInfo && (jobInfo.status === "failed" ||
        (jobInfo.status === "completed" &&
         (jobInfo.deployment_status === "completed" || jobInfo.deployment_status === "failed")))) {
      console.log(`Job status changed to ${jobInfo.status} with deployment status ${jobInfo.deployment_status}. Ensuring polling is stopped.`)
      if (pollInterval) {
        console.log("Cleaning up polling interval due to job completion")
        clearInterval(pollInterval)
        setPollInterval(null)
      }
    }
  }, [jobInfo, pollInterval])

  // Cleanup polling on unmount
  useEffect(() => {
    // Log the current polling configuration
    console.log(`Polling configuration: ${DISABLE_AUTO_POLLING ? 'Disabled' : 'Enabled'}, Max polls: ${MAX_POLL_COUNT}, Interval: ${POLL_INTERVAL_MS}ms`)

    return () => {
      // Clean up any active polling
      if (pollInterval) {
        console.log("Cleaning up polling interval on component unmount")
        clearInterval(pollInterval)
      }

      // Abort any in-flight requests
      if (abortControllerRef.current) {
        console.log("Aborting any in-flight requests on component unmount")
        abortControllerRef.current.abort()
      }
    }
  }, [])

  // This old documentation upload mode is no longer needed since we have unified interface
  // Removed the separate documentation upload mode

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-1">IS-Migration</h1>
              <p className="text-gray-600 text-sm">
                Convert integration flows to SAP Integration Suite using AI
              </p>
            </div>
            <div className="flex items-center gap-4">

              <button
                onClick={() => setShowLLMSelector(!showLLMSelector)}
                className="px-4 py-2 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors flex items-center gap-2"
              >
                <Zap className="w-4 h-4" />
                AI Model: {LLM_PROVIDER_LABELS[selectedLLMProvider]}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {showLLMSelector && (
              <Card>
                <CardBody className="p-6">
                  <LLMProviderSelector
                    selectedProvider={selectedLLMProvider}
                    onProviderChange={(provider) => {
                      setSelectedLLMProvider(provider);
                      setShowLLMSelector(false);
                      // Reset job info when provider changes
                      setJobInfo(null);
                      setHasNotifiedCompletion({});
                      if (pollInterval) {
                        clearInterval(pollInterval);
                        setPollInterval(null);
                      }
                    }}
                  />
                </CardBody>
              </Card>
            )}

            {/* Essential Configuration */}
            <Card>
              <CardBody className="p-4">

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Upload Type Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Upload Type
                    </label>
                    <Select
                      placeholder="Select upload type"
                      selectedKeys={new Set([uploadType])}
                      onSelectionChange={(keys) => {
                        const selectedKey = Array.from(keys)[0];
                        if (selectedKey) {
                          setUploadType(selectedKey);
                        }
                      }}
                      className="w-full"
                      variant="bordered"
                    >
                      <SelectItem key="source_code" textValue="Source Code (XML/ZIP)">
                        <div className="flex items-center gap-2">
                          <Code className="w-4 h-4" />
                          Source Code (XML/ZIP)
                        </div>
                      </SelectItem>
                      <SelectItem key="documentation" textValue="Documentation (PDF/Word/Text)">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Documentation (PDF/Word/Text)
                        </div>
                      </SelectItem>
                    </Select>
                    <p className="text-xs text-gray-500 mt-2">
                      {uploadType === 'source_code'
                        ? 'Upload XML files or ZIP archives containing integration code'
                        : 'Upload business documentation to generate iFlows automatically'
                      }
                    </p>
                  </div>

                  {/* Platform Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Source Platform
                    </label>
                    <Select
                      placeholder="Select platform"
                      selectedKeys={new Set([selectedPlatform])}
                      onSelectionChange={(keys) => {
                        const selectedKey = Array.from(keys)[0];
                        if (selectedKey) {
                          setSelectedPlatform(selectedKey);
                        }
                      }}
                      className="w-full"
                      variant="bordered"
                    >
                      <SelectItem key="mulesoft" textValue="MuleSoft">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                          MuleSoft
                        </div>
                      </SelectItem>
                      <SelectItem key="boomi" textValue="Boomi">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          Boomi
                        </div>
                      </SelectItem>
                    </Select>
                    <p className="text-xs text-gray-500 mt-2">
                      Choose the source platform for your integration flows
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Upload/Results Section */}
            {!jobInfo || (jobInfo.status === "failed" && !isLoading) ? (
              uploadType === 'source_code' ? (
                <FileUploadForm
                  onSubmit={startJob}
                  isLoading={isLoading}
                  selectedPlatform={selectedPlatform}
                  hidePlatformSelector={true}
                />
              ) : (
                <UnifiedDocumentationUpload
                  onSubmit={startDocumentationJob}
                  isLoading={isLoading}
                  selectedPlatform={selectedPlatform}
                  uploadProgress={uploadProgress}
                  uploadStatus={uploadStatus}
                />
              )
            ) : (
              <div className="space-y-6 animate-fadeIn">
                <ProgressTracker
                  status={jobInfo.status}
                  processingStep={jobInfo.processing_step}
                  isEnhancement={jobInfo.enhance}
                  startTime={startTime}
                  pollCount={pollCount}
                  statusMessage={jobInfo.processing_message}
                  deploymentStatus={jobInfo.deployment_status}
                  deployedIflowName={jobInfo.deployed_iflow_name}
                  deploymentDetails={jobInfo.deployment_details}
                />

                <JobResult
                  jobInfo={jobInfo}
                  onJobUpdate={(updatedJobInfo) => {
                    console.log("JobResult triggered job update:", updatedJobInfo);
                    setJobInfo(updatedJobInfo);
                  }}
                  onNewJob={() => {
                    // Reset job info
                    setJobInfo(null)
                    // Reset notification state (initialize with empty object)
                    setHasNotifiedCompletion({})
                    // Reset upload progress
                    setUploadProgress(0)
                    setUploadStatus("")
                    // Clear any existing polling
                    if (pollInterval) {
                      clearInterval(pollInterval)
                      setPollInterval(null)
                    }
                  }}
                />
              </div>
            )}
          </div>

          {/* Right Column - Jobs History */}
          <div className="lg:col-span-1">
            <JobsHistoryPanel />
          </div>
        </div>
      </div>
    </div>
  )
}

export default View
