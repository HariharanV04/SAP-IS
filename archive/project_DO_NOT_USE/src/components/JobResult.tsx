import React, { useState, useEffect } from 'react';
import {
  ExternalLink,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Code,
  Play,
  Download,
  AlertTriangle,
  Search,
  FileCode,
  Upload
} from 'lucide-react';
import { JobInfo } from '../types';
import { getDocumentation, generateIflowMatch, getIflowMatchStatus, getIflowMatchFile } from '../services/api';
import { toast } from 'react-hot-toast';

interface JobResultProps {
  jobInfo: JobInfo;
  onNewJob: () => void;
}

const JobResult: React.FC<JobResultProps> = ({ jobInfo, onNewJob }) => {
  const [isGeneratingIflowMatch, setIsGeneratingIflowMatch] = useState(false);
  const [iflowMatchStatus, setIflowMatchStatus] = useState<string | null>(null);
  const [iflowMatchMessage, setIflowMatchMessage] = useState<string | null>(null);
  const [iflowMatchFiles, setIflowMatchFiles] = useState<Record<string, string> | null>(null);
  const [isGeneratingIflow, setIsGeneratingIflow] = useState(false);
  const [isIflowGenerated, setIsIflowGenerated] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [isDeployed, setIsDeployed] = useState(false);
  const [downloading, setDownloading] = useState<Record<string, boolean>>({
    html: false,
    markdown: false,
    visualization: false,
    iflowReport: false,
    iflowSummary: false,
    generatedIflow: false
  });

  // Check if iFlow match has been processed
  useEffect(() => {
    if (jobInfo.status === 'completed' && jobInfo.id) {
      checkIflowMatchStatus();
    }
  }, [jobInfo]);

  // Function to check iFlow match status
  const checkIflowMatchStatus = async () => {
    try {
      const result = await getIflowMatchStatus(jobInfo.id);
      if (result.status !== 'not_started') {
        setIflowMatchStatus(result.status);
        setIflowMatchMessage(result.message);
        setIflowMatchFiles(result.files || null);
      }
    } catch (error) {
      console.error('Error checking iFlow match status:', error);
      // Don't show an error toast here as this is just a status check
    }
  };

  // Function to generate iFlow match
  const handleGenerateIflowMatch = async () => {
    try {
      setIsGeneratingIflowMatch(true);
      setIflowMatchStatus('processing');
      setIflowMatchMessage('Starting SAP Integration Suite equivalent search...');

      const result = await generateIflowMatch(jobInfo.id);
      toast.success('SAP Integration Suite equivalent search started');

      // Start polling for status
      const intervalId = setInterval(async () => {
        try {
          const statusResult = await getIflowMatchStatus(jobInfo.id);
          setIflowMatchStatus(statusResult.status);
          setIflowMatchMessage(statusResult.message);

          if (statusResult.status === 'completed') {
            setIflowMatchFiles(statusResult.files || null);
            clearInterval(intervalId);
            setIsGeneratingIflowMatch(false);
            toast.success('SAP Integration Suite equivalent search completed!');
          } else if (statusResult.status === 'failed') {
            clearInterval(intervalId);
            setIsGeneratingIflowMatch(false);
            toast.error(`SAP Integration Suite equivalent search failed: ${statusResult.message}`);
          }
        } catch (error) {
          console.error('Error polling iFlow match status:', error);
        }
      }, 2000); // Poll every 2 seconds

      // Clean up interval after 5 minutes (safety)
      setTimeout(() => {
        clearInterval(intervalId);
        if (iflowMatchStatus === 'processing') {
          setIflowMatchStatus('unknown');
          setIflowMatchMessage('Status check timed out. Please refresh the page.');
          setIsGeneratingIflowMatch(false);
        }
      }, 300000); // 5 minutes

    } catch (error) {
      console.error('Error generating iFlow match:', error);
      toast.error('Failed to start SAP Integration Suite equivalent search');
      setIsGeneratingIflowMatch(false);
      setIflowMatchStatus('failed');
      setIflowMatchMessage('Failed to start SAP Integration Suite equivalent search');
    }
  };

  const handleGenerateIflow = () => {
    setIsGeneratingIflow(true);

    // Simulate iFlow generation (would be an API call in a real app)
    toast.success('Starting SAP API/iFlow generation...');

    // Simulate a delay for the generation process
    setTimeout(() => {
      setIsGeneratingIflow(false);
      setIsIflowGenerated(true);
      toast.success('SAP API/iFlow generated successfully!');
    }, 3000);
  };

  const handleDeployToSap = () => {
    setIsDeploying(true);

    // Simulate deployment (would be an API call in a real app)
    setTimeout(() => {
      setIsDeploying(false);
      setIsDeployed(true);
      toast.success('Deployed to SAP Integration Suite successfully!');
    }, 2000);
  };

  const getStatusIcon = () => {
    if (jobInfo.status === 'completed') {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    } else if (jobInfo.status === 'failed') {
      return <XCircle className="h-5 w-5 text-red-500" />;
    } else {
      return <Clock className="h-5 w-5 text-blue-500" />;
    }
  };

  const downloadFile = async (fileType: 'html' | 'markdown' | 'visualization', filename: string) => {
    try {
      setDownloading(prev => ({ ...prev, [fileType]: true }));

      console.log(`Attempting to download ${fileType} file for job ${jobInfo.id}...`);

      // Get the file using our API service
      const blob = await getDocumentation(jobInfo.id, fileType);

      console.log(`File download response received, type: ${blob.type}, size: ${blob.size} bytes`);

      if (blob.size === 0) {
        toast.error(`Empty file received. No content available for ${fileType}.`);
        console.error(`Empty blob received for ${fileType}`);
        setDownloading(prev => ({ ...prev, [fileType]: false }));
        return;
      }

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(`${fileType} file downloaded successfully!`);
    } catch (error) {
      console.error(`Error downloading ${fileType} file:`, error);
      toast.error(`Failed to download ${fileType} file. Please try again.`);
    } finally {
      setDownloading(prev => ({ ...prev, [fileType]: false }));
    }
  };

  const downloadIflowMatchFile = async (fileType: 'report' | 'summary', filename: string) => {
    try {
      const downloadKey = fileType === 'report' ? 'iflowReport' : 'iflowSummary';
      setDownloading(prev => ({ ...prev, [downloadKey]: true }));

      console.log(`Attempting to download iFlow match ${fileType} file for job ${jobInfo.id}...`);

      // Get the file using our API service
      const blob = await getIflowMatchFile(jobInfo.id, fileType);

      console.log(`iFlow match file download response received, type: ${blob.type}, size: ${blob.size} bytes`);

      if (blob.size === 0) {
        toast.error(`Empty file received. No content available for iFlow match ${fileType}.`);
        console.error(`Empty blob received for iFlow match ${fileType}`);
        setDownloading(prev => ({ ...prev, [downloadKey]: false }));
        return;
      }

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(`iFlow match ${fileType} file downloaded successfully!`);
    } catch (error) {
      console.error(`Error downloading iFlow match ${fileType} file:`, error);
      toast.error(`Failed to download iFlow match ${fileType} file. Please try again.`);
    } finally {
      const downloadKey = fileType === 'report' ? 'iflowReport' : 'iflowSummary';
      setDownloading(prev => ({ ...prev, [downloadKey]: false }));
    }
  };

  const downloadGeneratedIflow = () => {
    try {
      setDownloading(prev => ({ ...prev, generatedIflow: true }));

      // Create a sample iFlow file (in a real app, this would be fetched from the server)
      const iflowContent = `<?xml version="1.0" encoding="UTF-8"?>
<iflow:process xmlns:iflow="http://www.sap.com/xi/XI/iflow/rt" id="Process_1">
  <bpmn2:startEvent id="StartEvent_1" name="Start">
    <bpmn2:outgoing>SequenceFlow_1</bpmn2:outgoing>
  </bpmn2:startEvent>
  <bpmn2:endEvent id="EndEvent_1" name="End">
    <bpmn2:incoming>SequenceFlow_2</bpmn2:incoming>
  </bpmn2:endEvent>
  <bpmn2:task id="Task_1" name="Process Data">
    <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
  </bpmn2:task>
  <bpmn2:sequenceFlow id="SequenceFlow_1" sourceRef="StartEvent_1" targetRef="Task_1" />
  <bpmn2:sequenceFlow id="SequenceFlow_2" sourceRef="Task_1" targetRef="EndEvent_1" />
</iflow:process>`;

      // Create a blob from the content
      const blob = new Blob([iflowContent], { type: 'application/xml' });

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sap_generated_iflow_${jobInfo.id}.xml`;
      document.body.appendChild(a);
      a.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('Generated SAP iFlow downloaded successfully!');
    } catch (error) {
      console.error('Error downloading generated iFlow:', error);
      toast.error('Failed to download generated iFlow. Please try again.');
    } finally {
      setDownloading(prev => ({ ...prev, generatedIflow: false }));
    }
  };

  return (
    <div className="bg-white shadow-sm rounded-lg p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <h3 className="text-lg font-semibold text-gray-800">
            Job Status: <span className="capitalize">{jobInfo.status}</span>
          </h3>
        </div>

        <button
          onClick={onNewJob}
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
        >
          <RefreshCw className="h-4 w-4" />
          <span>New Job</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Job ID: <span className="font-medium text-gray-800">{jobInfo.id}</span></p>
          <p className="text-gray-600">Created: <span className="font-medium text-gray-800">{new Date(jobInfo.created).toLocaleString()}</span></p>
        </div>
        <div>
          <p className="text-gray-600">Last Updated: <span className="font-medium text-gray-800">{new Date(jobInfo.last_updated).toLocaleString()}</span></p>
          <p className="text-gray-600">AI Enhancement: <span className="font-medium text-gray-800">{jobInfo.enhance ? 'Enabled' : 'Disabled'}</span></p>
        </div>
      </div>

      {jobInfo.status === 'completed' && (
        <>
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Documentation Files:</h4>
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-md">
                <FileText className="h-5 w-5 text-blue-500" />
                <span className="font-medium text-gray-800">HTML Documentation with Mermaid</span>

                <div className="flex gap-2 ml-auto">
                  <a
                    href={`https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/docs/${jobInfo.id}/html`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                    title="View in browser"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>

                  <button
                    onClick={() => downloadFile('html', `mulesoft_documentation_${jobInfo.id}.html`)}
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

              <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-md">
                <Code className="h-5 w-5 text-blue-500" />
                <span className="font-medium text-gray-800">Markdown Documentation</span>

                <div className="flex gap-2 ml-auto">
                  <a
                    href={`https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/docs/${jobInfo.id}/markdown`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                    title="View in browser"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>

                  <button
                    onClick={() => downloadFile('markdown', `mulesoft_documentation_${jobInfo.id}.md`)}
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

              <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-md">
                <Play className="h-5 w-5 text-blue-500" />
                <span className="font-medium text-gray-800">Flow Visualization</span>

                <div className="flex gap-2 ml-auto">
                  <a
                    href={`https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/docs/${jobInfo.id}/visualization`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                    title="View in browser"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>

                  <button
                    onClick={() => downloadFile('visualization', `mulesoft_visualization_${jobInfo.id}.html`)}
                    disabled={downloading.visualization}
                    className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Download file"
                  >
                    {downloading.visualization ? (
                      <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className="p-3 bg-yellow-50 rounded-md flex items-start space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-yellow-700">
                    If you're having trouble with the links, you can try these direct links:
                  </p>
                  <ul className="mt-1 text-xs text-yellow-700 space-y-1">
                    <li>
                      <a
                        href={`https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/docs/${jobInfo.id}/html`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Direct HTML Documentation Link
                      </a>
                    </li>
                    <li>
                      <a
                        href={`https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/docs/${jobInfo.id}/markdown`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Direct Markdown Documentation Link
                      </a>
                    </li>
                    <li>
                      <a
                        href={`https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/docs/${jobInfo.id}/visualization`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Direct Flow Visualization Link
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-800 mb-3">SAP Integration Suite Options:</h4>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleGenerateIflowMatch}
                disabled={isGeneratingIflowMatch || iflowMatchStatus === 'completed'}
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center space-x-2
                  ${isGeneratingIflowMatch || iflowMatchStatus === 'completed'
                    ? 'bg-green-100 text-green-800 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'}
                  transition-colors duration-200
                `}
              >
                {isGeneratingIflowMatch ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
                    <span>Finding SAP Equivalents...</span>
                  </>
                ) : iflowMatchStatus === 'completed' ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>SAP Equivalents Found</span>
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    <span>Find SAP Integration Suite Equivalents</span>
                  </>
                )}
              </button>

              <button
                onClick={handleGenerateIflow}
                disabled={iflowMatchStatus !== 'completed' || isGeneratingIflow || isIflowGenerated}
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center space-x-2
                  ${iflowMatchStatus !== 'completed' || isGeneratingIflow || isIflowGenerated
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'}
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
                    <Code className="h-4 w-4" />
                    <span>Generate SAP API/iFlow</span>
                  </>
                )}
              </button>

              <button
                onClick={handleDeployToSap}
                disabled={!isIflowGenerated || isDeploying || isDeployed}
                className={`
                  px-4 py-2 rounded-md font-medium flex items-center space-x-2
                  ${!isIflowGenerated || isDeploying || isDeployed
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'}
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
                    <Play className="h-4 w-4" />
                    <span>Deploy to SAP Integration Suite</span>
                  </>
                )}
              </button>
            </div>

            {/* Show iFlow match status and results */}
            {iflowMatchStatus && (
              <div className="mt-4">
                <div className={`p-4 rounded-md ${
                  iflowMatchStatus === 'completed' ? 'bg-green-50' :
                  iflowMatchStatus === 'failed' ? 'bg-red-50' :
                  'bg-blue-50'
                }`}>
                  <p className={`text-sm font-medium ${
                    iflowMatchStatus === 'completed' ? 'text-green-800' :
                    iflowMatchStatus === 'failed' ? 'text-red-800' :
                    'text-blue-800'
                  }`}>
                    {iflowMatchMessage || 'Processing SAP Integration Suite equivalent search...'}
                  </p>

                  {iflowMatchStatus === 'completed' && iflowMatchFiles && (
                    <div className="mt-3 space-y-2">
                      <h5 className="text-sm font-semibold text-gray-700">Available Files:</h5>

                      <div className="flex flex-wrap items-center gap-2 p-3 bg-white rounded-md">
                        <FileText className="h-5 w-5 text-blue-500" />
                        <span className="font-medium text-gray-800">Integration Match Report</span>

                        <div className="flex gap-2 ml-auto">
                          <a
                            href={`${import.meta.env.VITE_API_URL}/iflow-match/${jobInfo.id}/report`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                            title="View in browser"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>

                          <button
                            onClick={() => downloadIflowMatchFile('report', `sap_integration_match_${jobInfo.id}.html`)}
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

                      <div className="flex flex-wrap items-center gap-2 p-3 bg-white rounded-md">
                        <Code className="h-5 w-5 text-blue-500" />
                        <span className="font-medium text-gray-800">Integration Match Summary</span>

                        <div className="flex gap-2 ml-auto">
                          <a
                            href={`${import.meta.env.VITE_API_URL}/iflow-match/${jobInfo.id}/summary`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200"
                            title="View in browser"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>

                          <button
                            onClick={() => downloadIflowMatchFile('summary', `sap_integration_match_summary_${jobInfo.id}.json`)}
                            disabled={downloading.iflowSummary}
                            className="p-1.5 text-blue-600 hover:bg-blue-100 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Download file"
                          >
                            {downloading.iflowSummary ? (
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
                <div className="p-4 rounded-md bg-blue-50">
                  <p className="text-sm font-medium text-blue-800">
                    SAP API/iFlow has been generated successfully!
                  </p>

                  <div className="mt-3 space-y-2">
                    <h5 className="text-sm font-semibold text-gray-700">Generated File:</h5>

                    <div className="flex flex-wrap items-center gap-2 p-3 bg-white rounded-md">
                      <FileCode className="h-5 w-5 text-blue-500" />
                      <span className="font-medium text-gray-800">SAP API/iFlow Definition</span>

                      <div className="flex gap-2 ml-auto">
                        <button
                          onClick={downloadGeneratedIflow}
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
        </>
      )}

      {jobInfo.file_info && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">File Analysis:</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Count</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">XML Files</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.xml_files}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">Properties Files</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.properties_files}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">JSON Files</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.json_files}</td>
                </tr>
                {jobInfo.file_info.yaml_files !== undefined && (
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">YAML Files</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.yaml_files}</td>
                  </tr>
                )}
                {jobInfo.file_info.raml_files !== undefined && (
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">RAML Files</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.raml_files}</td>
                  </tr>
                )}
                {jobInfo.file_info.dwl_files !== undefined && (
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">DWL Files</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.dwl_files}</td>
                  </tr>
                )}
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">Other Files</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">{jobInfo.file_info.other_files}</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-800">Total Files</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-800">{jobInfo.file_info.total_files}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {jobInfo.parsed_details && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Parsed MuleSoft Components:</h4>
          {/* Changed to flex layout for better responsiveness */}
          <div className="flex flex-wrap gap-4">
            <div className="bg-blue-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-blue-600 uppercase font-semibold">Flows</p>
              <p className="text-2xl font-bold text-blue-800">{jobInfo.parsed_details.flows}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-green-600 uppercase font-semibold">Subflows</p>
              <p className="text-2xl font-bold text-green-800">{jobInfo.parsed_details.subflows}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-purple-600 uppercase font-semibold">Configurations</p>
              <p className="text-2xl font-bold text-purple-800">{jobInfo.parsed_details.configs}</p>
            </div>
            <div className="bg-orange-50 p-4 rounded-md flex-1 min-w-[150px]">
              <p className="text-xs text-orange-600 uppercase font-semibold">Error Handlers</p>
              <p className="text-2xl font-bold text-orange-800">{jobInfo.parsed_details.error_handlers}</p>
            </div>
          </div>

          {/* Add a table view for better visibility on smaller screens */}
          <div className="mt-4 overflow-x-auto md:hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Count</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-blue-600">Flows</td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">{jobInfo.parsed_details.flows}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-green-600">Subflows</td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">{jobInfo.parsed_details.subflows}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-purple-600">Configurations</td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">{jobInfo.parsed_details.configs}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-orange-600">Error Handlers</td>
                  <td className="px-4 py-2 whitespace-nowrap text-sm font-bold text-gray-800">{jobInfo.parsed_details.error_handlers}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {jobInfo.status === 'failed' && jobInfo.error && (
        <div className="bg-red-50 p-4 rounded-md">
          <h4 className="font-semibold text-red-800 mb-1">Error:</h4>
          <p className="text-red-700">{jobInfo.error}</p>
        </div>
      )}

      {/* Add a prominent Upload New File button at the bottom */}
      <div className="mt-8 flex justify-center">
        <button
          onClick={onNewJob}
          className="px-6 py-3 bg-blue-600 text-white rounded-md font-medium flex items-center space-x-2 hover:bg-blue-700 transition-colors duration-200 shadow-md"
        >
          <Upload className="h-5 w-5" />
          <span>Upload New File</span>
        </button>
      </div>
    </div>
  );
};

export default JobResult;