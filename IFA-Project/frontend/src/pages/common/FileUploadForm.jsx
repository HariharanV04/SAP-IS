import React, { useState, useRef } from "react"
import { Upload, File, X } from "lucide-react"
import CustomCard from "@components/Card"

const FileUploadForm = ({ onSubmit, isLoading, selectedPlatform = 'mulesoft', hidePlatformSelector = false }) => {
  const [files, setFiles] = useState([])
  const [enhance, setEnhance] = useState(false)
  const [platform, setPlatform] = useState(selectedPlatform)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = e => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleDrag = e => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = e => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files))
    }
  }

  const handleSubmit = e => {
    e.preventDefault()

    if (files.length === 0) {
      return
    }

    // Use selectedPlatform if hidePlatformSelector is true, otherwise use local platform state
    const targetPlatform = hidePlatformSelector ? selectedPlatform : platform
    onSubmit(files, enhance, targetPlatform)
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const handleClearFiles = () => {
    setFiles([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <CustomCard
        footer={
          <div className="w-full flex justify-end">
            <button
              type="submit"
              disabled={files.length === 0 || isLoading}
              className={`
            px-6 py-3 rounded-md font-medium text-white 
            transition-colors duration-200
            flex items-center space-x-2
            ${files.length === 0 || isLoading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-company-orange-600 hover:bg-company-orange-700"
                }
          `}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <File className="h-5 w-5" />
                  <span>Generate Documentation</span>
                </>
              )}
            </button>
          </div>
        }
      >
        {/* Platform Selection - Only show if not hidden */}
        {!hidePlatformSelector && (
          <div className="mb-6">
            <label htmlFor="platform-select" className="block text-sm font-medium text-gray-700 mb-3">
              Select Integration Platform
            </label>
            <div className="relative">
              <select
                id="platform-select"
                name="platform"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="block w-full px-3 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-company-orange-500 focus:border-company-orange-500 bg-white text-gray-900 text-sm"
              >
                <option value="mulesoft">
                  MuleSoft - Anypoint Platform integration flows
                </option>
                <option value="boomi">
                  Dell Boomi - AtomSphere integration processes
                </option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Choose the source integration platform for your files
            </p>
          </div>
        )}

        <div
          className={`
          border-2 border-dashed rounded-lg p-8
          transition-all duration-200 ease-in-out
          ${dragActive
              ? "border-company-orange-500 bg-company-orange-50"
              : "border-gray-300 hover:border-company-orange-400"
            }
          ${files.length > 0
              ? "bg-company-orange-50 border-company-orange-200"
              : ""
            }
        `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <input
              ref={fileInputRef}
              type="file"
              id="files"
              name="files[]"
              multiple
              accept=".xml,.zip"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="p-4 bg-company-orange-100 rounded-full">
              <Upload className="h-10 w-10 text-company-orange-500" />
            </div>

            <div className="text-center">
              <p className="text-lg font-medium text-gray-700">
                {files.length > 0
                  ? `${files.length} file${files.length > 1 ? "s" : ""} selected`
                  : `Drag & drop ${(hidePlatformSelector ? selectedPlatform : platform) === 'mulesoft' ? 'MuleSoft' : 'Dell Boomi'} XML files or ZIP archive here`}
              </p>
              <p className="text-gray-500 mt-1">
                {files.length > 0 ? files.map(f => f.name).join(", ") : "or"}
              </p>

              {files.length === 0 ? (
                <button
                  type="button"
                  onClick={handleBrowseClick}
                  className="mt-2 px-4 py-2 bg-company-orange-500 text-white rounded-md hover:bg-company-orange-600 transition-colors duration-200"
                >
                  Browse Files
                </button>
              ) : (
                <div className="mt-2 flex space-x-2">
                  <button
                    type="button"
                    onClick={handleBrowseClick}
                    className="px-4 py-2 bg-company-orange-500 text-white rounded-md hover:bg-company-orange-600 transition-colors duration-200"
                  >
                    Add More Files
                  </button>
                  <button
                    type="button"
                    onClick={handleClearFiles}
                    className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors duration-200 flex items-center space-x-1"
                  >
                    <X className="h-4 w-4" />
                    <span>Clear Files</span>
                  </button>
                </div>
              )}
            </div>

            <p className="text-xs text-gray-500">
              Supported formats: .xml files or .zip archives containing {(hidePlatformSelector ? selectedPlatform : platform) === 'mulesoft' ? 'MuleSoft' : 'Boomi'} XML files
            </p>
          </div>
        </div>

        {/* AI Enhancement checkbox - Hidden for now */}
        {false && (
          <div className="flex items-center space-x-2 mt-8">
            <input
              type="checkbox"
              id="enhance"
              name="enhance"
              checked={enhance}
              onChange={e => setEnhance(e.target.checked)}
              className="h-4 w-4 text-company-orange-600 focus:ring-company-orange-500 border-gray-300 rounded"
            />
            <div>
              <label htmlFor="enhance" className="font-medium text-gray-700">
                Enhance documentation with AI
              </label>
              <p className="text-xs text-gray-500">
                Note: AI enhancement may take 1-2 minutes for complex APIs
              </p>
            </div>
          </div>
        )}


      </CustomCard>
    </form>
  )
}

export default FileUploadForm
