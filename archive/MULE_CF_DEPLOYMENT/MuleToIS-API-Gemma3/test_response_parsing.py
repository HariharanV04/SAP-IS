#!/usr/bin/env python3
"""
Test script for RunPod response parsing
"""

import json
import sys
import os

# Add the current directory to the path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import extract_output

def test_runpod_response():
    """Test the extract_output function with a sample RunPod response"""
    
    # Sample RunPod response based on your example
    sample_response = {
        "delayTime": 597384,
        "executionTime": 42353,
        "id": "14266ee9-027e-40ba-a943-8a2b05485daa-e2",
        "output": [
            {
                "choices": [
                    {
                        "tokens": [
                            "\n\nHere's a sample iFlow project aimed at fetching data from a REST API and mapping it to a simple SAP SuccessFactors API.\n\n**Scenario:**\n\nWe want to fetch employee data from a public REST API (e.g., a mock API for testing) and then post that data to a SuccessFactors API.  For simplicity, we'll assume the REST API returns data in JSON format and SuccessFactors expects a specific JSON format as well.\n\n**REST API (Mock API - Replace with your actual API):**\n\n```json\n{\n  \"employeeId\": \"12345\",\n  \"firstName\": \"John\",\n  \"lastName\": \"Doe\",\n  \"email\": \"john.doe@example.com\"\n}\n```\n\n**SuccessFactors API (Simplified - Replace with your actual API details):**\n\nWe'll assume a simplified SuccessFactors API endpoint for creating employee records.  The expected JSON payload is:\n\n```json\n{\n  \"employeeId\": \"12345\",\n  \"name\": \"John Doe\",\n  \"email\": \"john.doe@example.com\"\n}\n```\n\n**iFlow Design:**\n\n1.  **Request Reply:**  This iFlow type is suitable for synchronous interactions.  We'll use it to fetch data from the REST API and then post to SuccessFactors.\n2.  **HTTP Requestor:** Fetches data from the REST API.\n3.  **Message Mapping:** Maps the data from the REST API response to the SuccessFactors API request payload.\n4.  **HTTP Sender:** Sends the mapped data to the SuccessFactors API.\n5.  **Parameters:** We will use parameters for the REST API URL and the SuccessFactors API URL.\n\n**Code Files:**\n\n**1. `src/main/resources/scenarioflows/integrationflow/employee_sync.iflw` (iFlow XML):**\n\n```xml\n<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<iflow xmlns=\"http://www.sap.com/integration/iflow\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.sap.com/integration/iflow iflow.xsd\">\n    <name>employee_sync</name>\n    <type>requestreply</type>\n    <description>Fetches employee data from REST API and posts to SuccessFactors API</description>\n    <main>\n        <step id=\"1\" type=\"http_requestor\">\n            <name>REST API Request</name>\n            <configuration>\n                <url>${REST_API_URL}</url>\n                <method>GET</method>\n                <contentType>application/json</contentType>\n                <requestHeaders>\n                   <!-- Add any necessary headers here -->\n                </requestHeaders>\n            </configuration>\n        </step>\n        <step id=\"2\" type=\"message_mapping\">\n            <name>Map to SuccessFactors</name>\n            <configuration>\n                <mapping source=\"REST API Request\" target=\"SuccessFactors API Request\">\n                    <mapExpression source=\"$.employeeId\" target=\"employeeId\"/>\n                    <mapExpression source=\"$.firstName\" target=\"name\"/>\n                    <mapExpression source=\"$.lastName\" target=\"name\"/>\n                    <mapExpression source=\"$.email\" target=\"email\"/>\n                </mapping>\n            </configuration>\n        </step>\n        <step id=\"3\" type=\"http_sender\">\n            <name>SuccessFactors API Request</name>\n            <configuration>\n                <url>${SUCCESSFACTORS_API_URL}</url>\n                <method>POST</method>\n                <contentType>application/json</contentType>\n                <requestHeaders>\n                   <!-- Add any necessary headers here -->\n                </requestHeaders>\n            </configuration>\n        </step>\n    </main>\n    <parameters>\n        <parameter name=\"REST_API_URL\" type=\"string\" description=\"URL of the REST API\"/>\n        <parameter name=\"SUCCESSFACTORS_API_URL\" type=\"string\" description=\"URL of the SuccessFactors API\"/>\n    </parameters>\n</iflow>\n```\n\n**2. `src/main/resources/parameters.prop` (Parameters Properties):**\n\n```properties\nREST_API_URL=https://jsonplaceholder.typicode.com/todos/1  # Replace with your actual REST API URL\nSUCCESSFACTORS_API_URL=http://example.com/successfactors/employee  # Replace with your actual SuccessFactors API URL\n```\n\n**3. `src/main/resources/parameters.propdef` (Parameters Property Definitions):**\n\n```properties\nREST_API_URL=string\nSUCCESSFACTORS_API_URL=string\n```\n\n**4. `src/main/resources/script/` (Empty directory - No scripts needed for this example)**\n\n**5. `META-INF/MANIFEST.MF` (Example Manifest File):**\n\n```\nManifest-Version: 1.0\nCreated-By: SAP Integration Suite\nBundle-Name: Employee Sync iFlow\nBundle-SymbolicName: com.example.employeesync\nBundle-Version: 1.0.0\n```\n\n**6. `.project` (Example Project File):**\n\n```xml\n<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<projectDescription>\n\t<name>Employee Sync iFlow</name>\n\t<comment></comment>\n\t<projects>\n\t</projects>\n\t<buildSpec>\n\t\t<buildCommand>\n\t\t\t<name>org.eclipse.jdt.core.javabuilder</name>\n\t\t\t<arguments>\n\t\t\t</arguments>\n\t\t</buildCommand>\n\t</buildSpec>\n\t<natures>\n\t\t<nature>org.eclipse.jdt.core.javanature</nature>\n\t</natures>\n</projectDescription>\n```\n\n**7. `metainfo.prop` (Example Metadata Properties):**\n\n```properties\nadapter.type=scenario\nadapter.version=1.0\n```\n\n**Output (Simulated - Based on the iFlow execution):**\n\nLet's assume the iFlow is deployed and activated in the SAP Integration Suite.  When a message is triggered (e.g., through a test message), the following sequence of events and outputs would occur:\n\n**1. REST API Request (Step 1):**\n\n*   **Input:**  None (This is the starting point)\n*   **Output:**\n    ```json\n    {\n      \"userId\": 1,\n      \"id\": 1,\n      \"title\": \"delectus aut autem\",\n      \"completed\": false\n    }\n    ```\n    (This is the response from the placeholder API)\n\n**2. Map to SuccessFactors (Step 2):**\n\n*   **Input:** The JSON response from the REST API request:\n    ```json\n    {\n      \"userId\": 1,\n      \"id\": 1,\n      \"title\": \"delectus aut autem\",\n      \"completed\": false\n    }\n    ```\n*   **Output:** The mapped JSON payload for the SuccessFactors API:\n    ```json\n    {\n      \"employeeId\": \"1\",\n      \"name\": \"delectus aut autem\",\n      \"email\": null  // No email in the REST API response, so it's null\n    }\n    ```\n\n**3. SuccessFactors API Request (Step 3):**\n\n*   **Input:** The JSON payload from the mapping step:\n    ```json\n    {\n      \"employeeId\": \"1\",\n      \"name\": \"delectus aut autem\",\n      \"email\": null\n    }\n    ```\n*   **Output:**  (Assuming a successful SuccessFactors API call)\n    ```\n    HTTP Status Code: 201 - Created\n    Response Headers:\n      Content-Type: application/json\n    Response Body:\n      {\n        \"employeeId\": \"1\",\n        \"name\": \"delectus aut autem\",\n        \"email\": null,\n        \"successfactorsId\": \"SF12345\"  // Example SuccessFactors generated ID\n      }\n    ```\n\n**Important Considerations:**\n\n*   **Error Handling:** This example lacks error handling. In a real-world scenario, you would need to add error handlers to handle failures at each step (e.g., REST API timeout, SuccessFactors API error).\n*   **Security:**  The API URLs are hardcoded.  Consider using secure storage mechanisms for sensitive information like API keys and passwords.\n*   **Data Types:** The mapping assumes that the data types are compatible. You might need to add data type conversions in the mapping.\n*   **SuccessFactors API:** This is a simplified example.  The actual SuccessFactors API integration would be more complex and require proper authentication and authorization.\n*   **Groovy Scripts:** For more complex transformations, you can use Groovy scripts within the iFlow.\n\nThis example provides a basic understanding of how to create a simple iFlow in SAP Integration Suite for integrating REST APIs and SuccessFactors.  Remember"
                        ]
                    }
                ],
                "usage": {
                    "input": 139,
                    "output": 2000
                }
            }
        ],
        "status": "COMPLETED",
        "workerId": "6lsch88468ji40"
    }
    
    print("Testing RunPod response parsing...")
    print("=" * 50)
    
    # Test the extraction
    extracted_text = extract_output(sample_response)
    
    print("Extraction successful:", bool(extracted_text))
    print("Extracted text length:", len(extracted_text) if extracted_text else 0)
    
    if extracted_text:
        print("\nFirst 200 characters of extracted text:")
        print("-" * 40)
        print(extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text)
        
        print("\nLast 200 characters of extracted text:")
        print("-" * 40)
        print("..." + extracted_text[-200:] if len(extracted_text) > 200 else extracted_text)
    else:
        print("Failed to extract text from response")
    
    print("\n" + "=" * 50)
    print("Test completed")

if __name__ == "__main__":
    test_runpod_response()
