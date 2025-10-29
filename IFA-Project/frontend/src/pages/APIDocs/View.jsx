import React from "react"

const View = () => {
    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    API Documentation
                </h1>
                <p className="text-gray-600">
                    Integration with the MuleSoft Documentation Generator API.
                </p>
            </div>

            <div className="bg-white shadow-sm rounded-lg p-6 space-y-6">
                <div>
                    <h2 className="text-xl font-semibold text-gray-800">API Endpoints</h2>
                    <p className="text-gray-600 mt-1">
                        The following endpoints are available for integration with the
                        documentation generator.
                    </p>
                </div>

                <div className="space-y-4">
                    <div className="border-l-4 border-company-orange-500 pl-4">
                        <h3 className="font-medium text-gray-800">POST /api/generate</h3>
                        <p className="text-gray-600 mt-1">
                            Generate documentation from MuleSoft XML files.
                        </p>
                        <pre className="bg-gray-100 p-3 mt-2 rounded text-sm overflow-x-auto">
                            {`
# Request (multipart/form-data)
files[]: File (MuleSoft XML or ZIP archive)
enhance: boolean (optional, default: false)

# Response
{
  "job_id": "string",
  "status": "queued",
  "message": "Job created successfully"
}
              `}
                        </pre>
                    </div>

                    <div className="border-l-4 border-company-orange-500 pl-4">
                        <h3 className="font-medium text-gray-800">
                            GET /api/job/{"{job_id}"}
                        </h3>
                        <p className="text-gray-600 mt-1">
                            Check the status of a documentation generation job.
                        </p>
                        <pre className="bg-gray-100 p-3 mt-2 rounded text-sm overflow-x-auto">
                            {`
# Response
{
  "id": "string",
  "status": "queued|processing|completed|failed",
  "created": "ISO date string",
  "last_updated": "ISO date string",
  "processing_step": "string|null",
  "processing_message": "string|null",
  "enhance": boolean,
  "files": [
    "string"
  ],
  "file_info": {
    "xml_files": number,
    "yaml_files": number,
    "raml_files": number,
    "dwl_files": number,
    "properties_files": number,
    "json_files": number,
    "other_files": number
  },
  "parsed_details": {
    "mule_flows": [
      {
        "name": "string",
        "type": "string",
        "filename": "string"
        // Additional flow details
      }
    ],
    "documentation_links": {
      "flow_diagram": "string",
      "flow_documentation": "string",
      "full_documentation": "string",
      "visualization": "string"
    }
  },
  "error": "string|null"
}
              `}
                        </pre>
                    </div>

                    <div className="border-l-4 border-company-orange-500 pl-4">
                        <h3 className="font-medium text-gray-800">
                            GET /api/download/{"{job_id}"}/{"{filename}"}
                        </h3>
                        <p className="text-gray-600 mt-1">
                            Download generated documentation files.
                        </p>
                        <pre className="bg-gray-100 p-3 mt-2 rounded text-sm overflow-x-auto">
                            {`
# Response
File content (HTML, Markdown, or JSON)
              `}
                        </pre>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow-sm rounded-lg p-6 space-y-6">
                <div>
                    <h2 className="text-xl font-semibold text-gray-800">
                        Supported File Types
                    </h2>
                    <p className="text-gray-600 mt-1">
                        The documentation generator processes various file types from
                        MuleSoft applications.
                    </p>
                </div>

                <div className="space-y-5">
                    <div>
                        <h3 className="font-medium text-gray-800">MuleSoft XML Files</h3>
                        <p className="text-gray-600 mt-1">
                            Core MuleSoft configuration files parsed for flow visualization
                            and documentation.
                        </p>
                        <ul className="list-disc pl-5 mt-2 text-gray-600">
                            <li>Flow configurations</li>
                            <li>Subflows</li>
                            <li>Error handlers</li>
                            <li>API configurations</li>
                            <li>Connection configurations</li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-medium text-company-orange-600">
                            DataWeave (DWL) Files
                        </h3>
                        <p className="text-gray-600 mt-1">
                            DataWeave transformation scripts are parsed to extract valuable
                            metadata.
                        </p>
                        <ul className="list-disc pl-5 mt-2 text-gray-600">
                            <li>DataWeave version detection</li>
                            <li>Function definitions and signatures</li>
                            <li>Variable declarations</li>
                            <li>Type hints (Transformation, Function Library, etc.)</li>
                            <li>Documentation comments</li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-medium text-company-orange-600">RAML Files</h3>
                        <p className="text-gray-600 mt-1">
                            RAML API definition files are analyzed to extract API
                            specifications.
                        </p>
                        <ul className="list-disc pl-5 mt-2 text-gray-600">
                            <li>RAML version detection</li>
                            <li>API title, version, and base URI</li>
                            <li>Endpoints (resources) and HTTP methods</li>
                            <li>Response codes and content types</li>
                            <li>
                                RAML file type (API Definition, Library, Resource Type, etc.)
                            </li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-medium text-company-orange-600">
                            YAML Configuration Files
                        </h3>
                        <p className="text-gray-600 mt-1">
                            YAML files are parsed to identify configuration patterns and
                            extract key information.
                        </p>
                        <ul className="list-disc pl-5 mt-2 text-gray-600">
                            <li>Configuration type detection (API, Server, General)</li>
                            <li>Top-level key identification</li>
                            <li>Structure analysis (object vs. array)</li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-medium text-gray-600">Other Supported Files</h3>
                        <p className="text-gray-600 mt-1">
                            Additional file types that are processed for comprehensive
                            documentation.
                        </p>
                        <ul className="list-disc pl-5 mt-2 text-gray-600">
                            <li>Properties files (configuration properties)</li>
                            <li>JSON files (data structures and configurations)</li>
                            <li>ZIP archives containing multiple file types</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow-sm rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800">
                    Documentation Output
                </h2>
                <p className="text-gray-600 mt-1">
                    The documentation generator produces several output formats:
                </p>
                <ul className="list-disc pl-5 mt-2 text-gray-600">
                    <li>
                        <strong>Flow Diagram (Mermaid)</strong>: Visual representation of
                        MuleSoft flows
                    </li>
                    <li>
                        <strong>Flow Documentation (Markdown)</strong>: Detailed
                        documentation of each flow
                    </li>
                    <li>
                        <strong>Full Documentation (HTML)</strong>: Comprehensive
                        documentation with navigation
                    </li>
                    <li>
                        <strong>Flow Visualization (Interactive)</strong>: Interactive
                        visualization of flows
                    </li>
                </ul>
            </div>
        </div>
    )
}

export default View
