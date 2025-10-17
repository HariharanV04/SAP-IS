import React, { useState, useRef } from "react"
import { toast } from "react-hot-toast"
import { Button, Card, CardBody, CardHeader, Divider, Select, SelectItem, Chip } from "@heroui/react"
import { Upload, FileText, File, FileImage, X } from "lucide-react"

const DocumentationUploadForm = ({ onUpload, isLoading, platform, onPlatformChange }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const supportedFormats = [
    { ext: '.txt', type: 'text/plain', label: 'Text Files', icon: FileText },
    { ext: '.md', type: 'text/markdown', label: 'Markdown Files', icon: FileText },
    { ext: '.pdf', type: 'application/pdf', label: 'PDF Documents', icon: File },
    { ext: '.docx', type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', label: 'Word Documents', icon: FileImage },
    { ext: '.json', type: 'application/json', label: 'JSON Files', icon: FileText },
    { ext: '.chat', type: 'text/plain', label: 'Chat Logs', icon: FileText }
  ]

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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (file) => {
    // Validate file type
    const isSupported = supportedFormats.some(format => 
      file.name.toLowerCase().endsWith(format.ext) || 
      file.type === format.type
    )

    if (!isSupported) {
      toast.error(`Unsupported file format. Please upload: ${supportedFormats.map(f => f.ext).join(', ')}`)
      return
    }

    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024 // 50MB
    if (file.size > maxSize) {
      toast.error('File size must be less than 50MB')
      return
    }

    setSelectedFile(file)
    toast.success(`File selected: ${file.name}`)
  }

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!selectedFile) {
      toast.error('Please select a documentation file')
      return
    }

    if (!platform) {
      toast.error('Please select a platform')
      return
    }

    onUpload(selectedFile, platform)
  }

  const getFileIcon = (file) => {
    const format = supportedFormats.find(f => 
      file.name.toLowerCase().endsWith(f.ext) || 
      file.type === f.type
    )
    const IconComponent = format?.icon || FileText
    return <IconComponent className="w-5 h-5" />
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Upload className="w-6 h-6 text-primary" />
          <h2 className="text-xl font-semibold">Upload Documentation</h2>
        </div>
        <p className="text-sm text-gray-600">
          Upload your integration documentation directly to generate iFlows without the document generation step.
        </p>
      </CardHeader>
      
      <Divider />
      
      <CardBody className="gap-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Platform Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Platform</label>
            <Select
              placeholder="Select platform"
              value={platform}
              onChange={(e) => onPlatformChange(e.target.value)}
              isRequired
              className="w-full"
            >
              <SelectItem key="mulesoft" value="mulesoft">
                MuleSoft
              </SelectItem>
              <SelectItem key="boomi" value="boomi">
                Boomi
              </SelectItem>
            </Select>
          </div>

          {/* File Upload Area */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Documentation File</label>
            
            {!selectedFile ? (
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive 
                    ? 'border-primary bg-primary/5' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium mb-2">
                  Drop your documentation file here
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  or click to browse files
                </p>
                <Button
                  type="button"
                  variant="bordered"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Choose File
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".txt,.md,.pdf,.docx,.json,.chat"
                  onChange={handleFileInputChange}
                />
              </div>
            ) : (
              <div className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getFileIcon(selectedFile)}
                    <div>
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                  </div>
                  <Button
                    isIconOnly
                    variant="light"
                    size="sm"
                    onClick={handleRemoveFile}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Supported Formats */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Supported Formats</label>
            <div className="flex flex-wrap gap-2">
              {supportedFormats.map((format) => (
                <Chip
                  key={format.ext}
                  variant="flat"
                  size="sm"
                  startContent={<format.icon className="w-3 h-3" />}
                >
                  {format.ext}
                </Chip>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            color="primary"
            size="lg"
            className="w-full"
            isLoading={isLoading}
            isDisabled={!selectedFile || !platform}
          >
            {isLoading ? 'Uploading...' : 'Upload & Generate iFlow'}
          </Button>
        </form>
      </CardBody>
    </Card>
  )
}

export default DocumentationUploadForm
