// Generate detailed error report for troubleshooting
def errorReport = new StringBuilder()
def timestamp = new Date().format('yyyy-MM-dd HH:mm:ss')

errorReport.append('EC372 - EC to NAVEX Integration Error Report\n')
errorReport.append('Generated: ' + timestamp + '\n\n')

// Error categorization
errorReport.append('Error Categories:\n')
errorReport.append('- Connection Errors: ' + (properties.get('ConnectionErrors') ?: '0') + '\n')
errorReport.append('- Data Validation Errors: ' + (properties.get('ValidationErrors') ?: '0') + '\n')
errorReport.append('- Transformation Errors: ' + (properties.get('TransformationErrors') ?: '0') + '\n')
errorReport.append('- File Delivery Errors: ' + (properties.get('DeliveryErrors') ?: '0') + '\n\n')

// Detailed error information
if (properties.get('ErrorDetails')) {
    errorReport.append('Detailed Error Information:\n')
    errorReport.append(properties.get('ErrorDetails') + '\n\n')
}

// System recommendations
errorReport.append('System Recommendations:\n')
errorReport.append('- Verify SuccessFactors connectivity and authentication\n')
errorReport.append('- Check SFTP server accessibility and credentials\n')
errorReport.append('- Validate process property configurations\n')
errorReport.append('- Review data quality and required field completeness\n')
errorReport.append('- Contact integration support team if errors persist\n')

message.setBody(errorReport.toString())
return message