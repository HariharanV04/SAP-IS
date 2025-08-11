import React, { useState, useEffect } from "react"
import {
  ExternalLink,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Code,
  Play,
  Download,
  Search,
  FileCode,
  Trash2,
  Plus,
  RotateCcw
} from "lucide-react"

import {
  getDocumentation,
  generateIflowMatch,
  getIflowMatchStatus,
  getIflowMatchFile,
  generateIflow,
  generateIflowFromDocs,
  getJobStatus,
  getIflowGenerationStatus,
  downloadGeneratedIflow,
  deployIflowToSap,
  directDeployIflowToSap,
  unifiedDeployIflowToSap,
  updateDeploymentStatus,
  deleteJob
} from "@services/api"

import { toast } from "react-hot-toast"

// Get environment variables for polling configuration
const DISABLE_AUTO_POLLING = import.meta.env.VITE_DISABLE_AUTO_POLLING === 'true'
const MAX_POLL_COUNT = parseInt(import.meta.env.VITE_MAX_POLL_COUNT || '30')
const POLL_INTERVAL_MS = parseInt(import.meta.env.VITE_POLL_INTERVAL_MS || '5000')
const MAX_FAILED_ATTEMPTS = parseInt(import.meta.env.VITE_MAX_FAILED_ATTEMPTS || '3')

const JobResult = ({ jobInfo, onNewJob, onJobUpdate }) => {
  const [isGeneratingIflowMatch, setIsGeneratingIflowMatch] = useState(false)
  const [iflowMatchStatus, setIflowMatchStatus] = useState(null)
  const [iflowMatchMessage, setIflowMatchMessage] = useState(null)
  const [iflowMatchFiles, setIflowMatchFiles] = useState(null)
  const [isGeneratingIflow, setIsGeneratingIflow] = useState(false)

  // Debouncing to prevent rapid multiple clicks
  const [lastClickTime, setLastClickTime] = useState(0)
  const [isIflowGenerated, setIsIflowGenerated] = useState(false)
  const [isDeploying, setIsDeploying] = useState(false)
  const [isDeployed, setIsDeployed] = useState(false)

  // User input for deployment configuration
  const [showDeploymentConfig, setShowDeploymentConfig] = useState(false)
  const [customPackageName, setCustomPackageName] = useState("ConversionPackages")
  const [customIflowName, setCustomIflowName] = useState("")
  const [downloading, setDownloading] = useState({
    html: false,
    markdown: false,
    iflowReport: false,
    iflowSummary: false,
    generatedIflow: false,
    documentationJson: false,
    uploadedDocumentation: false
  })
  const [showFileAnalysis, setShowFileAnalysis] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  // Check if iFlow match has been processed
  useEffect(() => {
    if (jobInfo.status === "completed" && jobInfo.id) {
      checkIflowMatchStatus()
    }
  }, [jobInfo])

  // Function to check iFlow match status
  const checkIflowMatchStatus = async () => {
    try {
      const result = await getIflowMatchStatus(jobInfo.id)
      if (result.status !== "not_started") {
        setIflowMatchStatus(result.status)
        setIflowMatchMessage(result.message)
        setIflowMatchFiles(result.files || null)
      }
    } catch (error) {
      console.error("Error checking iFlow match status:", error)
      // Don't show an error toast here as this is just a status check
    }
  }

  // Function to generate iFlow match - ISOLATED from main job status
  const handleGenerateIflowMatch = async () => {
    // DEBOUNCING: Prevent rapid multiple clicks
    const now = Date.now();
    if (now - lastClickTime < 1000) { // 1 second debounce
      console.log("🚫 Click ignored - too soon after last click");
      return;
    }
    setLastClickTime(now);

    // IMMEDIATELY disable button to prevent multiple clicks
    if (isGeneratingIflowMatch) {
      console.log("🚫 SAP equivalent search already in progress, ignoring click");
      return;
    }

    setIsGeneratingIflowMatch(true);
    setIflowMatchStatus("processing");
    setIflowMatchMessage("Starting SAP Integration Suite equivalent search...");

    try {
      // Clear any existing iFlow match interval first
      if (iflowMatchInterval) {
        console.log("Clearing existing iFlow match interval");
        clearInterval(iflowMatchInterval);
        setIflowMatchInterval(null);
      }

      console.log("🔍 Starting SAP equivalent search - ISOLATED mode (no main job interference)");
      console.log("🔍 Current main job status:", jobInfo.status);

      const result = await generateIflowMatch(jobInfo.id)
      toast.success("SAP Integration Suite equivalent search started")

      // Check if auto-polling is disabled in production
      if (DISABLE_AUTO_POLLING) {
        console.log("Auto-polling is disabled for SAP equivalent search. Making a single status check.");

        // Make a single status check after a short delay - ISOLATED
        setTimeout(async () => {
          try {
            const statusResult = await getIflowMatchStatus(jobInfo.id);
            console.log("SAP equivalent search status check (no polling):", statusResult);
            setIflowMatchStatus(statusResult.status);
            setIflowMatchMessage(statusResult.message);

            if (statusResult.status === "completed") {
              setIflowMatchFiles(statusResult.files || null);
              setIsGeneratingIflowMatch(false);
              toast.success("SAP Integration Suite equivalent search completed!");
            } else {
              setIsGeneratingIflowMatch(false);
              toast.info("SAP Integration Suite equivalent search is in progress. Check back later for results.");
            }
          } catch (error) {
            console.error("Error checking SAP equivalents status:", error);
            setIsGeneratingIflowMatch(false);
            toast.info("SAP Integration Suite equivalent search is in progress. Check back later for results.");
          }
        }, 5000); // Wait 5 seconds before checking

        return;
      }

      // Start polling for status - ISOLATED from main job status
      const intervalId = setInterval(async () => {
        try {
          // Use ONLY the iFlow match status API, not the main job status
          const statusResult = await getIflowMatchStatus(jobInfo.id)
          console.log("🔍 SAP equivalent search status (isolated, no main job update):", statusResult)

          setIflowMatchStatus(statusResult.status)
          setIflowMatchMessage(statusResult.message)

          if (statusResult.status === "completed") {
            setIflowMatchFiles(statusResult.files || null)
            clearInterval(intervalId)
            setIflowMatchInterval(null)
            setIsGeneratingIflowMatch(false)
            toast.success("SAP Integration Suite equivalent search completed!")
          } else if (statusResult.status === "failed") {
            clearInterval(intervalId)
            setIflowMatchInterval(null)
            setIsGeneratingIflowMatch(false)
            toast.error(
              `SAP Integration Suite equivalent search failed: ${statusResult.message}`
            )
          }
        } catch (error) {
          console.error("Error polling iFlow match status:", error)
          // Don't let SAP search errors affect main progress
        }
      }, POLL_INTERVAL_MS) // Use configured polling interval

      // Store the interval ID for cleanup
      setIflowMatchInterval(intervalId)

      // Clean up interval after 5 minutes (safety)
      setTimeout(() => {
        clearInterval(intervalId)
        setIflowMatchInterval(null)
        if (iflowMatchStatus === "processing") {
          setIflowMatchStatus("unknown")
          setIflowMatchMessage(
            "Status check timed out. Please refresh the page."
          )
          setIsGeneratingIflowMatch(false)
        }
      }, 300000) // 5 minutes
    } catch (error) {
      console.error("Error generating iFlow match:", error)
      toast.error("Failed to start SAP Integration Suite equivalent search")
      setIsGeneratingIflowMatch(false)
      setIflowMatchStatus("failed")
      setIflowMatchMessage(
        "Failed to start SAP Integration Suite equivalent search"
      )
    }
  }

  const [iflowJobId, setIflowJobId] = useState(null)
  const [iflowGenerationStatus, setIflowGenerationStatus] = useState(null)
  const [iflowGenerationMessage, setIflowGenerationMessage] = useState(null)
  const [iflowGenerationFiles, setIflowGenerationFiles] = useState(null)
  const [statusCheckInterval, setStatusCheckInterval] = useState(null)
  const [iflowMatchInterval, setIflowMatchInterval] = useState(null)

  // Set default custom iFlow name when iflowJobId becomes available
  useEffect(() => {
    if (!customIflowName && (iflowJobId || jobInfo.id)) {
      const baseFileName = jobInfo.filename ? jobInfo.filename.replace(/\.[^/.]+$/, "") : "Integration"
      const cleanBaseName = baseFileName.replace(/[^a-zA-Z0-9_]/g, '_').substring(0, 30)
      const jobIdToUse = iflowJobId || jobInfo.id
      const defaultName = `${cleanBaseName}_${jobIdToUse.substring(0, 8)}`
      setCustomIflowName(defaultName)
    }
  }, [iflowJobId, jobInfo.id, jobInfo.filename, customIflowName])

  // Clean up any existing intervals when component unmounts or when starting a new job
  useEffect(() => {
    return () => {
      if (statusCheckInterval) {
        console.log("Cleaning up status check interval on unmount");
        clearInterval(statusCheckInterval);
      }
      if (iflowMatchInterval) {
        console.log("Cleaning up iFlow match interval on unmount");
        clearInterval(iflowMatchInterval);
      }
    };
  }, [statusCheckInterval, iflowMatchInterval]);

  const handleGenerateIflow = async () => {
    // DEBOUNCING: Prevent rapid multiple clicks
    const now = Date.now();
    if (now - lastClickTime < 1000) { // 1 second debounce
      console.log("🚫 Click ignored - too soon after last click");
      return;
    }
    setLastClickTime(now);

    // IMMEDIATELY disable button to prevent multiple clicks
    if (isGeneratingIflow) {
      console.log("🚫 iFlow generation already in progress, ignoring click");
      return;
    }

    setIsGeneratingIflow(true);
    setIflowGenerationStatus("processing");
    setIflowGenerationMessage("Starting SAP API/iFlow generation...");

    try {
      // Clear any existing interval first
      if (statusCheckInterval) {
        console.log("Clearing existing status check interval");
        clearInterval(statusCheckInterval);
        setStatusCheckInterval(null);
      }

      console.log(`Generating iFlow for job ${jobInfo.id}...`)
      console.log(`Platform detected: ${jobInfo.platform || 'mulesoft'}`)

      // Check if this is a documentation upload job
      const isDocumentationUpload = jobInfo.source_type === 'uploaded_documentation' ||
                                   jobInfo.status === 'documentation_ready';

      let result;
      if (isDocumentationUpload) {
        console.log("Using main API endpoint for documentation upload job");
        // Call the main API endpoint for documentation upload jobs
        result = await generateIflowFromDocs(jobInfo.id);
      } else {
        console.log("Using direct BoomiToIS-API endpoint for XML processing job");
        // Call the BoomiToIS-API directly for XML processing jobs
        result = await generateIflow(jobInfo.id, jobInfo.platform || 'mulesoft');
      }

      // Check if the result has an error status
      if (result.status === 'error') {
        console.error("Error from iFlow generation API:", result.message);
        toast.error(`Failed to start SAP API/iFlow generation: ${result.message}`);
        setIsGeneratingIflow(false);
        setIflowGenerationStatus("failed");
        setIflowGenerationMessage(result.message);
        return;
      }

      toast.success("SAP API/iFlow generation started")

      // Store the appropriate job ID based on the API used
      if (isDocumentationUpload) {
        // For main API, the job_id is the main job ID, boomi_job_id is the BoomiToIS-API job ID
        setIflowJobId(result.boomi_job_id || result.job_id);
        console.log("Main API response:", result);
        console.log("Stored BoomiToIS-API job ID:", result.boomi_job_id);
      } else {
        // For direct BoomiToIS-API, the job_id is the BoomiToIS-API job ID
        setIflowJobId(result.job_id);
        console.log("BoomiToIS-API response:", result);
      }

      // Check if auto-polling is disabled in production
      if (DISABLE_AUTO_POLLING) {
        console.log("Auto-polling is disabled by environment configuration. Making a single status check.");

        // Make status checks after delays to catch completion
        const checkStatuses = async (attempt = 1, maxAttempts = 6) => {
          try {
            let statusToCheck;

            if (isDocumentationUpload) {
              // For documentation upload jobs, check the main job status
              // The main API will poll the BoomiToIS-API and update the main job status
              statusToCheck = await getJobStatus(jobInfo.id);
              console.log(`Status check attempt ${attempt} (main job):`, {
                mainJobStatus: statusToCheck.status,
                processingMessage: statusToCheck.processing_message
              });

              // Update main job info if it has changed
              if (statusToCheck.status !== jobInfo.status) {
                console.log(`Main job status updated from ${jobInfo.status} to ${statusToCheck.status}`);
                // Only update parent if this is NOT a SAP equivalent search operation
                // to prevent interference with main progress tracking
                if (typeof onJobUpdate === 'function' && !isGeneratingIflowMatch) {
                  onJobUpdate(statusToCheck);
                }
              }
            } else {
              // For XML processing jobs, check the BoomiToIS-API job status directly
              statusToCheck = await getJobStatus(result.job_id);
              console.log(`Status check attempt ${attempt} (BoomiToIS-API job):`, {
                iflowStatus: statusToCheck.status
              });
            }

            if (statusToCheck.status === "completed") {
              setIflowGenerationStatus("completed");
              setIflowGenerationMessage("iFlow generation completed successfully");
              setIsGeneratingIflow(false);
              setIsIflowGenerated(true);
              toast.success("iFlow generated successfully!");
              return;
            }

            // If not completed yet and we haven't reached max attempts, try again
            if (attempt < maxAttempts) {
              setTimeout(() => checkStatuses(attempt + 1, maxAttempts), 5000);
            } else {
              setIsGeneratingIflow(false);
              toast.info("iFlow generation is in progress. Check back later for results.");
            }
          } catch (error) {
            console.error("Error checking status:", error);
            if (attempt < maxAttempts) {
              setTimeout(() => checkStatuses(attempt + 1, maxAttempts), 5000);
            } else {
              setIsGeneratingIflow(false);
              toast.info("iFlow generation is in progress. Check back later for results.");
            }
          }
        };

        // Start checking after 5 seconds
        setTimeout(() => checkStatuses(), 5000);

        return;
      }

      // Start polling for status
      let failedAttempts = 0;
      let pollCount = 0;

      console.log(`Starting polling for iFlow generation job ${result.job_id}`);
      console.log(`Polling configuration: Max polls: ${MAX_POLL_COUNT}, Interval: ${POLL_INTERVAL_MS}ms, Max failed attempts: ${MAX_FAILED_ATTEMPTS}`);

      const intervalId = setInterval(async () => {
        try {
          pollCount++;
          console.log(`Polling attempt ${pollCount} for job ${result.job_id}`);

          // If we've reached the maximum number of polls, stop polling
          if (pollCount >= MAX_POLL_COUNT) {
            console.log(`Reached maximum number of polls (${MAX_POLL_COUNT}). Stopping.`);
            clearInterval(intervalId);
            setStatusCheckInterval(null);

            // Try one final direct download
            try {
              await downloadGeneratedIflow(result.job_id, jobInfo.platform || 'mulesoft');
              setIflowGenerationStatus("completed");
              setIflowGenerationMessage("iFlow generation completed successfully");
              setIsGeneratingIflow(false);
              setIsIflowGenerated(true);
              toast.success("iFlow generated successfully!");
            } catch (finalDownloadError) {
              setIflowGenerationStatus("unknown");
              setIflowGenerationMessage("Status check timed out. The iFlow may still be generating.");
              setIsGeneratingIflow(false);
              toast("Status check timed out. Try downloading the iFlow manually.", {
                icon: "⚠️",
                duration: 5000
              });
            }
            return;
          }

          // Use main API status which includes BoomiToIS-API sync
          const statusResult = await getJobStatus(result.job_id)

          // If the result has an error status, handle it but don't stop polling yet
          if (statusResult.status === 'failed') {
            console.warn("Job failed:", statusResult.processing_message || statusResult.message);
            failedAttempts++;

            // Only if we've had multiple consecutive failures, try direct download
            if (failedAttempts >= MAX_FAILED_ATTEMPTS) {
              await handleDirectDownloadCheck(result.job_id, intervalId);
            }
            return;
          }

          // Reset failed attempts counter on successful API call
          failedAttempts = 0;

          setIflowGenerationStatus(statusResult.status)
          setIflowGenerationMessage(statusResult.processing_message || statusResult.message || "Processing...")

          if (statusResult.status === "completed") {
            setIflowGenerationFiles(statusResult.files || null)
            clearInterval(intervalId)
            setStatusCheckInterval(null)
            setIsGeneratingIflow(false)
            setIsIflowGenerated(true)
            toast.success("iFlow generated successfully!")
          } else if (statusResult.status === "failed") {
            clearInterval(intervalId)
            setStatusCheckInterval(null)
            setIsGeneratingIflow(false)
            toast.error(`iFlow generation failed: ${statusResult.processing_message || statusResult.message || "Unknown error"}`)
          }
        } catch (error) {
          console.error("Error polling iFlow generation status:", error)
          failedAttempts++;

          // If we've had multiple consecutive failures, try to download the file directly
          if (failedAttempts >= MAX_FAILED_ATTEMPTS) {
            await handleDirectDownloadCheck(result.job_id, intervalId);
          }
        }
      }, POLL_INTERVAL_MS) // Use configured polling interval

      // Store the interval ID for cleanup
      setStatusCheckInterval(intervalId)
    } catch (error) {
      console.error("Error generating iFlow:", error)
      toast.error("Failed to start SAP API/iFlow generation")
      setIsGeneratingIflow(false)
      setIflowGenerationStatus("failed")
      setIflowGenerationMessage("Failed to start SAP API/iFlow generation")
    }
  }

  // Helper function to check if the file exists by trying to download it
  const handleDirectDownloadCheck = async (jobId, intervalId) => {
    console.log(`Multiple consecutive status check failures. Trying direct download for job ${jobId}...`);

    try {
      // Try to download the file directly to see if it exists
      await downloadGeneratedIflow(jobId, jobInfo.platform || 'mulesoft');

      // If download succeeds, the file exists and job is complete
      clearInterval(intervalId);
      setStatusCheckInterval(null);
      setIflowGenerationStatus("completed");
      setIflowGenerationMessage("iFlow generation completed successfully");
      setIsGeneratingIflow(false);
      setIsIflowGenerated(true);
      toast.success("iFlow generated successfully!");
      console.log("Direct download successful - assuming job is complete");
      return true;
    } catch (downloadError) {
      console.error("Direct download failed:", downloadError);
      return false;
    }
  }

  const handleDeployToSap = async () => {
    try {
      setIsDeploying(true)

      // ONLY use the iFlow job ID - don't fall back to the documentation job ID
      if (!iflowJobId) {
        toast.error("iFlow job ID not found. Please generate the iFlow first.")
        setIsDeploying(false)
        return
      }

      const deployJobId = iflowJobId

      console.log(`Deploying iFlow for job ${deployJobId} to SAP Integration Suite...`)

      // Use custom names provided by user or fall back to job data/generated names
      let iflowName
      if (customIflowName && customIflowName.trim()) {
        // Use user-provided custom name
        iflowName = customIflowName.trim()
      } else if (jobInfo.iflow_name) {
        // Use the preserved iflow_name from the job data
        iflowName = jobInfo.iflow_name
      } else {
        // Fallback to generating from filename
        const baseFileName = jobInfo.filename ? jobInfo.filename.replace(/\.[^/.]+$/, "") : "Integration"
        const cleanBaseName = baseFileName.replace(/[^a-zA-Z0-9_]/g, '_').substring(0, 30)
        iflowName = `${cleanBaseName}_${deployJobId.substring(0, 8)}`
      }
      const iflowId = iflowName.replace(/[^a-zA-Z0-9_]/g, '_')
      const packageId = (customPackageName && customPackageName.trim()) ? customPackageName.trim() : "ConversionPackages"

      // Use the direct deployment approach with platform information
      console.log(`🚀 DEPLOYMENT INFO:`)
      console.log(`  - Job ID: ${deployJobId}`)
      console.log(`  - iFlow Name: ${iflowName}`)
      console.log(`  - iFlow ID: ${iflowId}`)
      console.log(`  - Package: ${packageId}`)
      console.log(`  - Platform: ${jobInfo.platform || 'mulesoft'}`)
      console.log(`Using unified deployment with iflowId=${iflowId}, iflowName=${iflowName}, packageId=${packageId}, platform=${jobInfo.platform || 'mulesoft'}`)
      const result = await unifiedDeployIflowToSap(deployJobId, packageId, iflowId, iflowName, jobInfo.platform || 'mulesoft')

      console.log("Unified deployment response:", result)
      console.log(`📦 DEPLOYMENT RESULT STATUS: ${result.status}`)

      if (result.status === 'success') {
        setIsDeployed(true)
        console.log(`✅ DEPLOYMENT SUCCESS:`)
        console.log(`  - Deployed Name: ${result.iflow_name || iflowName}`)
        console.log(`  - Package: ${result.package_id || packageId}`)
        console.log(`  - Response:`, result)
        toast.success(`Deployed to SAP Integration Suite as: ${result.iflow_name || iflowName}`)

        // Update Main API job status with deployment information
        try {
          console.log(`📦 Updating Main API job ${jobInfo.id} with deployment status...`)
          console.log(`📦 Deployment details:`, {
            iflow_name: result.iflow_name || iflowName,
            package_id: result.package_id || packageId,
            iflow_id: result.iflow_id || iflowId
          })

          const updateResult = await updateDeploymentStatus(
            jobInfo.id, // Update the MAIN API job (this is correct!)
            'completed',
            `iFlow deployed successfully as: ${result.iflow_name || iflowName}`,
            {
              iflow_name: result.iflow_name || iflowName,
              package_id: result.package_id || packageId,
              iflow_id: result.iflow_id || iflowId,
              deployment_method: 'direct',
              response_code: result.response_code || 201,
              boomi_job_id: deployJobId // Also include the BoomiToIS job ID for reference
            }
          )
          console.log(`📦 Main API job status updated successfully:`, updateResult)
        } catch (error) {
          console.error("❌ Error updating Main API deployment status:", error)
        }

        // Refresh job data to get updated deployment status and iflow_name
        if (typeof onJobUpdate === 'function') {
          try {
            const updatedJobData = await getJobStatus(jobInfo.id) // Use main job ID
            if (updatedJobData) {
              console.log("Refreshed job data after deployment:", updatedJobData)
              onJobUpdate(updatedJobData)
            }
          } catch (error) {
            console.error("Error refreshing job data after deployment:", error)
          }
        }
      } else {
        console.log(`📦 ENTERING FAILURE BLOCK - Status was: ${result.status}`)
        console.log(`❌ DEPLOYMENT FAILED:`, result)
        toast.error(`Deployment failed: ${result.message}`)

        // Update Main API job status with deployment failure
        try {
          console.log(`📦 Updating Main API job ${jobInfo.id} with deployment failure...`)
          await updateDeploymentStatus(
            jobInfo.id,
            'failed',
            `Deployment failed: ${result.message}`,
            {
              error: result.message,
              deployment_method: 'direct'
            }
          )
          console.log(`📦 Main API job status updated with failure`)
        } catch (error) {
          console.error("Error updating Main API deployment failure status:", error)
        }

        // Also refresh job data on failure to show updated deployment status
        if (typeof onJobUpdate === 'function') {
          try {
            const updatedJobData = await getJobStatus(jobInfo.id) // Use main job ID
            if (updatedJobData) {
              console.log("Refreshed job data after deployment failure:", updatedJobData)
              onJobUpdate(updatedJobData)
            }
          } catch (error) {
            console.error("Error refreshing job data after deployment failure:", error)
          }
        }
      }
    } catch (error) {
      console.error("Error deploying to SAP:", error)
      toast.error("Failed to deploy to SAP Integration Suite. Please try again.")
      
      // Refresh job data even on exception to show any partial updates
      if (typeof onJobUpdate === 'function') {
        try {
          const updatedJobData = await getJobStatus(deployJobId)
          if (updatedJobData) {
            console.log("Refreshed job data after deployment exception:", updatedJobData)
            onJobUpdate(updatedJobData)
          }
        } catch (refreshError) {
          console.error("Error refreshing job data after deployment exception:", refreshError)
        }
      }
    } finally {
      setIsDeploying(false)
    }
  }

  const getStatusIcon = () => {
    if (jobInfo.status === "completed") {
      return <CheckCircle className="h-5 w-5 text-green-500" />
    } else if (jobInfo.status === "failed") {
      return <XCircle className="h-5 w-5 text-red-500" />
    } else {
      return <Clock className="h-5 w-5 text-blue-500" />
    }
  }

  const handleDeleteJob = async () => {
    try {
      setIsDeleting(true)
      await deleteJob(jobInfo.id)
      toast.success("Job and associated files deleted successfully")
      setShowDeleteConfirm(false)
      // Trigger the onNewJob callback to reset the UI
      if (onNewJob) {
        onNewJob()
      }
    } catch (error) {
      console.error("Error deleting job:", error)
      toast.error("Failed to delete job. Please try again.")
    } finally {
      setIsDeleting(false)
    }
  }

  const downloadFile = async (fileType, filename) => {
    try {
      // Map file types to download state keys
      const downloadKey = fileType === "documentation_json" ? "documentationJson" :
                         fileType === "uploaded_documentation" ? "uploadedDocumentation" : fileType
      setDownloading(prev => ({ ...prev, [downloadKey]: true }))

      console.log(
        `Attempting to download ${fileType} file for job ${jobInfo.id}...`
      )

      // Get the file using our API service
      const blob = await getDocumentation(jobInfo.id, fileType)

      console.log(
        `File download response received, type: ${blob.type}, size: ${blob.size} bytes`
      )

      if (blob.size === 0) {
        toast.error(
          `Empty file received. No content available for ${fileType}.`
        )
        console.error(`Empty blob received for ${fileType}`)
        setDownloading(prev => ({ ...prev, [fileType]: false }))
        return
      }

      // Create a download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()

      // Clean up
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success(`${fileType} file downloaded successfully!`)
    } catch (error) {
      console.error(`Error downloading ${fileType} file:`, error)
      toast.error(`Failed to download ${fileType} file. Please try again.`)
    } finally {
      // Use the same mapping for cleanup
      const downloadKey = fileType === "documentation_json" ? "documentationJson" :
                         fileType === "uploaded_documentation" ? "uploadedDocumentation" : fileType
      setDownloading(prev => ({ ...prev, [downloadKey]: false }))
    }
  }

  const downloadIflowMatchFile = async (fileType, filename) => {
    try {
      const downloadKey = fileType === "report" ? "iflowReport" : "iflowSummary"
      setDownloading(prev => ({ ...prev, [downloadKey]: true }))

      console.log(
        `Attempting to download iFlow match ${fileType} file for job ${jobInfo.id}...`
      )

      // Get the file using our API service
      const blob = await getIflowMatchFile(jobInfo.id, fileType)

      console.log(
        `iFlow match file download response received, type: ${blob.type}, size: ${blob.size} bytes`
      )

      if (blob.size === 0) {
        toast.error(
          `Empty file received. No content available for iFlow match ${fileType}.`
        )
        console.error(`Empty blob received for iFlow match ${fileType}`)
        setDownloading(prev => ({ ...prev, [downloadKey]: false }))
        return
      }

      // Create a download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()

      // Clean up
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success(`iFlow match ${fileType} file downloaded successfully!`)
    } catch (error) {
      console.error(`Error downloading iFlow match ${fileType} file:`, error)
      toast.error(
        `Failed to download iFlow match ${fileType} file. Please try again.`
      )
    } finally {
      const downloadKey = fileType === "report" ? "iflowReport" : "iflowSummary"
      setDownloading(prev => ({ ...prev, [downloadKey]: false }))
    }
  }

  const handleDownloadGeneratedIflow = async () => {
    try {
      if (!iflowJobId) {
        toast.error("iFlow job ID not found. Please try generating the iFlow again.")
        return
      }

      setDownloading(prev => ({ ...prev, generatedIflow: true }))

      console.log(`Downloading generated iFlow for job ${iflowJobId}...`)

      // Get the file using our API service
      const blob = await downloadGeneratedIflow(iflowJobId, jobInfo.platform || 'mulesoft')

      console.log(`iFlow download response received, size: ${blob.size} bytes`)

      if (blob.size === 0) {
        toast.error("Empty file received. No content available for iFlow.")
        console.error("Empty blob received for iFlow")
        setDownloading(prev => ({ ...prev, generatedIflow: false }))
        return
      }

      // Create a download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `sap_generated_iflow_${iflowJobId}.zip`
      document.body.appendChild(a)
      a.click()

      // Clean up
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success("Generated SAP iFlow downloaded successfully!")
    } catch (error) {
      console.error("Error downloading generated iFlow:", error)
      toast.error("Failed to download generated iFlow. Please try again.")
    } finally {
      setDownloading(prev => ({ ...prev, generatedIflow: false }))
    }
  }

  return (
    <div className="bg-white shadow-sm rounded-lg p-6 space-y-6">
      {/* New Upload Button - Prominent placement at top */}
      {(jobInfo.status === "completed" || jobInfo.status === "failed" || jobInfo.status === "documentation_ready") && (
        <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">
              {jobInfo.status === "completed" ? "Job Completed Successfully!" :
               jobInfo.status === "failed" ? "Job Failed" :
               "Documentation Ready"}
            </h3>
            <p className="text-sm text-gray-600">
              {jobInfo.status === "completed" ? "Your files have been processed and are ready for download." :
               jobInfo.status === "failed" ? "There was an issue processing your files." :
               "Your documentation has been processed and is ready for iFlow generation."}
            </p>
          </div>
          <button
            onClick={() => {
              if (onNewJob) {
                onNewJob()
              }
            }}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium shadow-sm"
            title="Start a new upload"
          >
            <RotateCcw className="h-5 w-5" />
            <span>Start New Upload</span>
          </button>
        </div>
      )}

      {(jobInfo.status === "completed" || jobInfo.status === "documentation_ready") && (
        <>
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">
              SAP Integration Suite Options (Independent Actions):
            </h4>
            <p className="text-sm text-gray-600 mb-2">
              These actions can be performed independently. You can generate an iFlow directly from the documentation or find SAP equivalents first.
            </p>
            <div className="flex flex-wrap items-center">
              <button
                onClick={handleGenerateIflowMatch}
                disabled={
                  isGeneratingIflowMatch || iflowMatchStatus === "completed"
                }
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center space-x-2
                  ${
                    isGeneratingIflowMatch || iflowMatchStatus === "completed"
                      ? "bg-green-100 text-green-800 cursor-not-allowed"
                      : "bg-green-600 text-white hover:bg-green-700"
                  }
                  transition-colors duration-200
                `}
              >
                {isGeneratingIflowMatch ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
                    <span>Finding SAP Equivalents...</span>
                  </>
                ) : iflowMatchStatus === "completed" ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>SAP Equivalents Found</span>
                  </>
                ) : (
                  <>
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-white text-green-600 rounded-full mr-1 font-bold">1</span>
                    <Search className="h-4 w-4" />
                    <span>Find SAP Integration Suite Equivalents</span>
                  </>
                )}
              </button>

              <div className="mx-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14"></path>
                  <path d="m12 5 7 7-7 7"></path>
                </svg>
              </div>

              <button
                onClick={handleGenerateIflow}
                disabled={
                  isGeneratingIflow ||
                  isIflowGenerated
                }
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center space-x-2
                  ${
                    isGeneratingIflow
                      ? "bg-blue-100 text-blue-800 cursor-not-allowed"
                      : isIflowGenerated
                      ? "bg-green-100 text-green-800 cursor-not-allowed"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  }
                  transition-colors duration-200
                `}
              >
                {isGeneratingIflow ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
                    <span>Generating SAP API/iFlow...</span>
                  </>
                ) : isIflowGenerated ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>SAP API/iFlow Generated</span>
                  </>
                ) : (
                  <>
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-white text-blue-600 rounded-full mr-1 font-bold">2</span>
                    <Code className="h-4 w-4" />
                    <span>Generate SAP API/iFlow</span>
                  </>
                )}
              </button>

              <div className="mx-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14"></path>
                  <path d="m12 5 7 7-7 7"></path>
                </svg>
              </div>

              {/* Deployment Configuration Section */}
              {!isDeployed && isIflowGenerated && (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Deployment Configuration</h4>
                    <button
                      onClick={() => setShowDeploymentConfig(!showDeploymentConfig)}
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      {showDeploymentConfig ? "Hide" : "Customize"}
                      <svg className={`w-4 h-4 transition-transform ${showDeploymentConfig ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>

                  {showDeploymentConfig && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          iFlow Name
                        </label>
                        <input
                          type="text"
                          value={customIflowName}
                          onChange={(e) => setCustomIflowName(e.target.value)}
                          placeholder="Enter custom iFlow name"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Leave empty to use auto-generated name
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Package Name
                        </label>
                        <input
                          type="text"
                          value={customPackageName}
                          onChange={(e) => setCustomPackageName(e.target.value)}
                          placeholder="Enter package name"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Package where the iFlow will be deployed in SAP Integration Suite
                        </p>
                      </div>
                    </div>
                  )}

                  {!showDeploymentConfig && (
                    <div className="text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>iFlow Name:</span>
                        <span className="font-mono text-blue-700">
                          {(() => {
                            if (customIflowName && customIflowName.trim()) {
                              return customIflowName.trim()
                            }
                            const baseFileName = jobInfo.filename ? jobInfo.filename.replace(/\.[^/.]+$/, "") : "Integration"
                            const cleanBaseName = baseFileName.replace(/[^a-zA-Z0-9_]/g, '_').substring(0, 30)
                            const jobIdToUse = iflowJobId || jobInfo.id
                            return `${cleanBaseName}_${jobIdToUse.substring(0, 8)}`
                          })()}
                        </span>
                      </div>
                      <div className="flex justify-between mt-1">
                        <span>Package:</span>
                        <span className="font-mono text-blue-700">{customPackageName}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={handleDeployToSap}
                disabled={!isIflowGenerated || isDeploying || isDeployed}
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center space-x-2
                  ${
                    !isIflowGenerated
                      ? "bg-gray-100 text-gray-500 cursor-not-allowed"
                      : isDeploying
                      ? "bg-green-100 text-green-800 cursor-not-allowed"
                      : isDeployed
                      ? "bg-green-100 text-green-800 cursor-not-allowed"
                      : "bg-green-600 text-white hover:bg-green-700"
                  }
                  transition-colors duration-200
                `}
              >
                {isDeploying ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
                    <span>Deploying...</span>
                  </>
                ) : isDeployed ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>Deployed</span>
                  </>
                ) : (
                  <>
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-white text-green-600 rounded-full mr-1 font-bold">3</span>
                    <Play className="h-4 w-4" />
                    <span>Deploy to SAP Integration Suite</span>
                  </>
                )}
              </button>

              {/* Show deployment preview when not yet deployed or currently deploying */}
              {!isDeployed && (!jobInfo.deployment_status || jobInfo.deployment_status === "deploying") && (
                <div className="mt-2 text-xs text-gray-600">
                  <div className="bg-gray-50 p-2 rounded border">
                    <span className="font-medium">
                      {jobInfo.deployment_status === "deploying" ? "Deploying as:" : "Will deploy as:"}
                    </span>
                    <div className="font-mono text-blue-700 mt-1">
                      {(() => {
                        // Use custom name if provided, otherwise use preserved or generated name
                        if (customIflowName && customIflowName.trim()) {
                          return customIflowName.trim()
                        } else if (jobInfo.iflow_name) {
                          return jobInfo.iflow_name
                        } else {
                          const baseFileName = jobInfo.filename ? jobInfo.filename.replace(/\.[^/.]+$/, "") : "Integration"
                          const cleanBaseName = baseFileName.replace(/[^a-zA-Z0-9_]/g, '_').substring(0, 30)
                          const jobIdToUse = iflowJobId || jobInfo.id
                          return jobIdToUse ? `${cleanBaseName}_${jobIdToUse.substring(0, 8)}` : `${cleanBaseName}_loading`
                        }
                      })()}
                    </div>
                    <div className="text-gray-500 mt-1">
                      Package: <span className="font-mono">{customPackageName}</span>
                    </div>
                    {jobInfo.deployment_status === "deploying" && (
                      <div className="mt-2 flex items-center gap-1 text-blue-600">
                        <div className="animate-spin rounded-full h-3 w-3 border-2 border-blue-500 border-t-transparent" />
                        <span className="text-xs">Deployment in progress...</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Show SAP Integration Suite Deployment Status */}
            {(isDeployed || jobInfo.deployment_status) && (
              <div className="mt-4">
                <div className="p-4 rounded-md bg-green-50 border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <h4 className="font-semibold text-green-800">
                      🚀 Deployed to SAP Integration Suite
                    </h4>
                  </div>

                  {jobInfo.deployment_details && (
                    <div className="space-y-2 text-sm">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <span className="font-medium text-gray-700">iFlow Name:</span>
                          <div className="bg-white px-3 py-1 rounded border text-green-800 font-mono text-sm">
                            {(() => {
                              const displayName = jobInfo.deployed_iflow_name || jobInfo.deployment_details?.iflow_name || jobInfo.iflow_name || jobInfo.deployment_details?.iflow_id || 'N/A'
                              console.log("Displaying iFlow name:", displayName, "from jobInfo:", {
                                deployed_iflow_name: jobInfo.deployed_iflow_name,
                                deployment_details_iflow_name: jobInfo.deployment_details?.iflow_name,
                                iflow_name: jobInfo.iflow_name,
                                deployment_details_iflow_id: jobInfo.deployment_details?.iflow_id
                              })
                              return displayName
                            })()}
                          </div>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Package:</span>
                          <div className="bg-white px-3 py-1 rounded border text-blue-800 font-mono text-sm">
                            {jobInfo.deployed_package_id || jobInfo.deployment_details?.package_id || 'N/A'}
                          </div>
                        </div>
                      </div>

                      <div className="mt-3 p-2 bg-white rounded border">
                        <span className="font-medium text-gray-700">SAP Integration Suite Location:</span>
                        <div className="text-xs text-gray-600 mt-1">
                          Navigate to: <strong>Design</strong> → <strong>Integrations and APIs</strong> → <strong>{jobInfo.deployed_package_id || jobInfo.deployment_details?.package_id || 'ConversionPackages'}</strong> → <strong>{jobInfo.deployed_iflow_name || jobInfo.deployment_details?.iflow_name || jobInfo.iflow_name || jobInfo.deployment_details?.iflow_id || 'Your iFlow'}</strong>
                        </div>
                      </div>

                      {jobInfo.deployment_details.response_code && (
                        <div className="text-xs text-green-600">
                          ✅ Deployment successful (HTTP {jobInfo.deployment_details.response_code})
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Show iFlow match status and results */}
            {iflowMatchStatus && (
              <div className="mt-4">
                <div
                  className={`p-4 rounded-md ${
                    iflowMatchStatus === "completed"
                      ? "bg-green-50"
                      : iflowMatchStatus === "failed"
                      ? "bg-red-50"
                      : "bg-blue-50"
                  }`}
                >
                  <p
                    className={`text-sm font-medium ${
                      iflowMatchStatus === "completed"
                        ? "text-green-800"
                        : iflowMatchStatus === "failed"
                        ? "text-red-800"
                        : "text-blue-800"
                    }`}
                  >
                    {iflowMatchMessage ||
                      "Processing SAP Integration Suite equivalent search..."}
                  </p>

                  {iflowMatchStatus === "completed" && iflowMatchFiles && (
                    <div className="mt-3 space-y-2">
                      <h5 className="text-sm font-semibold text-gray-700">
                        Available Files:
                      </h5>

                      <div className="flex flex-wrap items-center gap-2 p-3 bg-white rounded-md">
                        <FileText className="h-5 w-5 text-blue-500" />
                        <span className="font-medium text-gray-800">
                          Integration Match Report
                        </span>

                        <div className="flex gap-2 ml-auto">
                          <a
                            href={`${
                              import.meta.env.VITE_API_URL
                            }/iflow-match/${jobInfo.id}/report`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                            title="View in browser"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>

                          <button
                            onClick={() =>
                              downloadIflowMatchFile(
                                "report",
                                `sap_integration_match_${jobInfo.id}.html`
                              )
                            }
                            disabled={downloading.iflowReport}
                            className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Download file"
                          >
                            {downloading.iflowReport ? (
                              <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                            ) : (
                              <Download className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Show generated iFlow when available */}
            {isIflowGenerated && (
              <div className="mt-4">
                <div className="p-4 rounded-md bg-green-50">
                  <p className="text-sm font-medium text-green-800">
                    SAP API/iFlow has been generated successfully!
                  </p>

                  <div className="mt-3 space-y-2">
                    <h5 className="text-sm font-semibold text-gray-700">
                      Generated File:
                    </h5>

                    <div className="flex flex-wrap items-center gap-2 p-3 bg-white rounded-md">
                      <FileCode className="h-5 w-5 text-blue-500" />
                      <span className="font-medium text-gray-800">
                        SAP API/iFlow Definition
                      </span>

                      <div className="flex gap-2 ml-auto">
                        <button
                          onClick={handleDownloadGeneratedIflow}
                          disabled={downloading.generatedIflow}
                          className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Download file"
                        >
                          {downloading.generatedIflow ? (
                            <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <Download className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Documentation Files Section - Only show for XML uploads, not documentation uploads */}
          {jobInfo.source_type !== 'uploaded_documentation' && (
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">
                Documentation Files:
              </h4>
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-md">
                <FileText className="h-5 w-5 text-blue-500" />
                <span className="font-medium text-gray-800">
                  HTML Documentation with Mermaid
                </span>

                <div className="flex gap-2 ml-auto">
                  <a
                    href={`${import.meta.env.VITE_API_URL}/docs/${jobInfo.id}/html`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                    title="View in browser"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>

                  <button
                    onClick={() =>
                      downloadFile(
                        "html",
                        `mulesoft_documentation_${jobInfo.id}.html`
                      )
                    }
                    disabled={downloading.html}
                    className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Download file"
                  >
                    {downloading.html ? (
                      <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Markdown Documentation section removed */}
              {/* Flow Visualization section removed */}
              {/* Direct links section removed */}
            </div>
          </div>
          )}

          {/* Intermediate Processing Files Section - Show for documentation uploads */}
          {console.log('JobInfo debug:', { source_type: jobInfo.source_type, status: jobInfo.status, files: jobInfo.files })}
          {(jobInfo.source_type === 'uploaded_documentation' || jobInfo.status === 'documentation_ready') && (
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">
                Processing Files:
              </h4>
              <div className="space-y-2">
                {/* AI-Generated Markdown */}
                <div className="flex flex-wrap items-center gap-2 p-3 bg-blue-50 rounded-md">
                  <FileText className="h-5 w-5 text-blue-500" />
                  <span className="font-medium text-gray-800">
                    AI-Enhanced Markdown
                  </span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    Structured for iFlow Generation
                  </span>

                  <div className="flex gap-2 ml-auto">
                    <a
                      href={`${import.meta.env.VITE_API_URL}/docs/${jobInfo.id}/markdown`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                      title="View in browser"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>

                    <button
                      onClick={() =>
                        downloadFile(
                          "markdown",
                          `ai_enhanced_documentation_${jobInfo.id}.md`
                        )
                      }
                      disabled={downloading.markdown}
                      className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Download file"
                    >
                      {downloading.markdown ? (
                        <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Documentation JSON */}
                <div className="flex flex-wrap items-center gap-2 p-3 bg-green-50 rounded-md">
                  <FileText className="h-5 w-5 text-green-500" />
                  <span className="font-medium text-gray-800">
                    Documentation JSON
                  </span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                    Structured Data + Metadata
                  </span>

                  <div className="flex gap-2 ml-auto">
                    <a
                      href={`${import.meta.env.VITE_API_URL}/docs/${jobInfo.id}/documentation_json`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 text-green-600 hover:bg-green-100 rounded transition-colors duration-200"
                      title="View in browser"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>

                    <button
                      onClick={() =>
                        downloadFile(
                          "documentation_json",
                          `documentation_${jobInfo.id}.json`
                        )
                      }
                      disabled={downloading.documentationJson}
                      className="p-1.5 text-green-600 hover:bg-green-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Download file"
                    >
                      {downloading.documentationJson ? (
                        <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Original Uploaded Documentation */}
                <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-md">
                  <FileText className="h-5 w-5 text-gray-500" />
                  <span className="font-medium text-gray-800">
                    Original Document Content
                  </span>
                  <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    Raw Extracted Text
                  </span>

                  <div className="flex gap-2 ml-auto">
                    <a
                      href={`${import.meta.env.VITE_API_URL}/docs/${jobInfo.id}/uploaded_documentation`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors duration-200"
                      title="View in browser"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>

                    <button
                      onClick={() =>
                        downloadFile(
                          "uploaded_documentation",
                          `original_content_${jobInfo.id}.md`
                        )
                      }
                      disabled={downloading.uploadedDocumentation}
                      className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Download file"
                    >
                      {downloading.uploadedDocumentation ? (
                        <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Image Analysis Results - Show if images were found and analyzed */}
          {jobInfo.source_type === 'uploaded_documentation' && jobInfo.image_count > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold text-gray-800 mb-3">
                📸 Image Analysis Results:
              </h4>
              <div className="bg-purple-50 rounded-md p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-purple-700">
                    <strong>{jobInfo.image_count}</strong> images found,
                    <strong> {jobInfo.images_analyzed || 0}</strong> analyzed with AI
                  </span>
                </div>
                <div className="text-xs text-purple-600">
                  Images containing integration diagrams, flow charts, and architecture details
                  have been analyzed and included in the AI-enhanced documentation above.
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {jobInfo.file_info && (
        <div className="mt-6">
          <button
            onClick={() => setShowFileAnalysis(!showFileAnalysis)}
            className="flex items-center justify-between w-full font-semibold text-gray-800 mb-3 bg-gray-100 p-3 rounded-md hover:bg-gray-200 transition-colors"
          >
            <span>File Analysis</span>
            <span className="text-gray-500">
              {showFileAnalysis ? '▼' : '►'}
            </span>
          </button>

          {showFileAnalysis && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      File Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Count
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      XML Files
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                      {jobInfo.file_info.xml_files}
                    </td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      Properties Files
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                      {jobInfo.file_info.properties_files}
                    </td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      JSON Files
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                      {jobInfo.file_info.json_files}
                    </td>
                  </tr>
                  {jobInfo.file_info.yaml_files !== undefined && (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        YAML Files
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                        {jobInfo.file_info.yaml_files}
                      </td>
                    </tr>
                  )}
                  {jobInfo.file_info.raml_files !== undefined && (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        RAML Files
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                        {jobInfo.file_info.raml_files}
                      </td>
                    </tr>
                  )}
                  {jobInfo.file_info.dwl_files !== undefined && (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        DWL Files
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                        {jobInfo.file_info.dwl_files}
                      </td>
                    </tr>
                  )}
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      Other Files
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                      {jobInfo.file_info.other_files}
                    </td>
                  </tr>
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-800">
                      Total Files
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-800">
                      {jobInfo.file_info.total_files}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {jobInfo.parsed_details && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">
            Parsed MuleSoft Components:
          </h4>
          {/* Changed to flex layout for better responsiveness */}
          <div className="flex flex-wrap gap-4">
            <div className="bg-blue-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-blue-600 uppercase font-semibold">
                Flows
              </p>
              <p className="text-2xl font-bold text-blue-800">
                {jobInfo.parsed_details.flows}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-green-600 uppercase font-semibold">
                Subflows
              </p>
              <p className="text-2xl font-bold text-green-800">
                {jobInfo.parsed_details.subflows}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-purple-600 uppercase font-semibold">
                Configurations
              </p>
              <p className="text-2xl font-bold text-purple-800">
                {jobInfo.parsed_details.configs}
              </p>
            </div>
            <div className="bg-orange-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-orange-600 uppercase font-semibold">
                Error Handlers
              </p>
              <p className="text-2xl font-bold text-orange-800">
                {jobInfo.parsed_details.error_handlers}
              </p>
            </div>
          </div>

          {/* Add a table view for better visibility on smaller screens */}
          <div className="mt-4 overflow-x-auto md:hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Component
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Count
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-blue-600">
                    Flows
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">
                    {jobInfo.parsed_details.flows}
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-green-600">
                    Subflows
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">
                    {jobInfo.parsed_details.subflows}
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-purple-600">
                    Configurations
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">
                    {jobInfo.parsed_details.configs}
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-orange-600">
                    Error Handlers
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">
                    {jobInfo.parsed_details.error_handlers}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Job Status Information */}
      <div className="border-t pt-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <h3 className="text-lg font-semibold text-gray-800">
              Job Status: <span className="capitalize">{jobInfo.status}</span>
            </h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                if (onNewJob) {
                  onNewJob()
                }
              }}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors duration-200"
              title="Start a new upload"
            >
              <Plus className="h-4 w-4" />
              <span>New Upload</span>
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors duration-200"
              title="Delete this job and all associated files"
            >
              <Trash2 className="h-4 w-4" />
              <span>Delete Job</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">
              Job ID:{" "}
              <span className="font-medium text-gray-800">{jobInfo.id}</span>
            </p>
            <p className="text-gray-600">
              Created:{" "}
              <span className="font-medium text-gray-800">
                {new Date(jobInfo.created).toLocaleString()}
              </span>
            </p>
          </div>
          <div>
            <p className="text-gray-600">
              Last Updated:{" "}
              <span className="font-medium text-gray-800">
                {new Date(jobInfo.last_updated).toLocaleString()}
              </span>
            </p>
            <p className="text-gray-600">
              AI Enhancement:{" "}
              <span className="font-medium text-gray-800">
                {jobInfo.enhance ? "Enabled" : "Disabled"}
              </span>
            </p>
          </div>
        </div>
      </div>

      {jobInfo.status === "failed" && jobInfo.error && (
        <div className="bg-red-50 p-4 rounded-md">
          <h4 className="font-semibold text-red-800 mb-1">Error:</h4>
          <p className="text-red-700">{jobInfo.error}</p>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="flex-shrink-0">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">Delete Job</h3>
              </div>
            </div>
            <div className="mb-6">
              <p className="text-sm text-gray-600">
                Are you sure you want to delete this job and all associated files? This action cannot be undone.
              </p>
              <div className="mt-3 p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500">
                  <strong>Job ID:</strong> {jobInfo.id}
                </p>
                <p className="text-xs text-gray-500">
                  <strong>Status:</strong> {jobInfo.status}
                </p>
                {jobInfo.filename && (
                  <p className="text-xs text-gray-500">
                    <strong>Files:</strong> {jobInfo.filename}
                  </p>
                )}
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteJob}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors duration-200 disabled:opacity-50 flex items-center space-x-2"
              >
                {isDeleting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4" />
                    <span>Delete</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Removed the Upload New File button */}
    </div>
  )
}

export default JobResult
