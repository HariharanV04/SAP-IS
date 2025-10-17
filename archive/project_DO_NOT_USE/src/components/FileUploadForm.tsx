import React, { useState, useRef } from 'react';
import { Upload, File, AlertCircle } from 'lucide-react';

interface FileUploadFormProps {
  onSubmit: (files: File[], enhance: boolean) => void;
  isLoading: boolean;
}

const FileUploadForm: React.FC<FileUploadFormProps> = ({ onSubmit, isLoading }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [enhance, setEnhance] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      return;
    }
    
    onSubmit(files, enhance);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div 
        className={`
          border-2 border-dashed rounded-lg p-8 
          transition-all duration-200 ease-in-out
          ${dragActive ? 'border-company-orange-500 bg-company-orange-50' : 'border-gray-300 hover:border-company-orange-400'} 
          ${files.length > 0 ? 'bg-company-orange-50 border-company-orange-200' : ''}
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
                ? `${files.length} file${files.length > 1 ? 's' : ''} selected` 
                : 'Drag & drop MuleSoft XML files or ZIP archive here'}
            </p>
            <p className="text-gray-500 mt-1">
              {files.length > 0 
                ? files.map(f => f.name).join(', ')
                : 'or'}
            </p>
            
            {files.length === 0 && (
              <button 
                type="button" 
                onClick={handleBrowseClick}
                className="mt-2 px-4 py-2 bg-company-orange-500 text-white rounded-md hover:bg-company-orange-600 transition-colors duration-200"
              >
                Browse Files
              </button>
            )}
          </div>
          
          <p className="text-xs text-gray-500">
            Supported formats: .xml files or .zip archives containing MuleSoft XML files
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="enhance"
          name="enhance"
          checked={enhance}
          onChange={(e) => setEnhance(e.target.checked)}
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

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={files.length === 0 || isLoading}
          className={`
            px-6 py-3 rounded-md font-medium text-white 
            transition-colors duration-200
            flex items-center space-x-2
            ${files.length === 0 || isLoading 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-company-orange-600 hover:bg-company-orange-700'}
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
    </form>
  );
};

export default FileUploadForm;