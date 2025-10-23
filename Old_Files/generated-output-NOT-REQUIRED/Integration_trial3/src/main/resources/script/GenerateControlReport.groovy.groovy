// Generate comprehensive control report
def reportContent = new StringBuilder()
def timestamp = new Date().format('yyyy-MM-dd HH:mm:ss')

reportContent.append('EC372 - EC to NAVEX Integration Control Report\n')
reportContent.append('Generated: ' + timestamp + '\n\n')

// Process execution metrics
reportContent.append('Process Execution Summary:\n')
reportContent.append('- Total Records Processed: ' + (properties.get('RecordCount') ?: '0') + '\n')
reportContent.append('- Successful Records: ' + (properties.get('SuccessCount') ?: '0') + '\n')
reportContent.append('- Error Records: ' + (properties.get('ErrorCount') ?: '0') + '\n')
reportContent.append('- Processing Mode: ' + (properties.get('FileType') ?: 'Unknown') + '\n')
reportContent.append('- Execution Duration: ' + (properties.get('ExecutionDuration') ?: 'Unknown') + '\n\n')

// File delivery status
reportContent.append('File Delivery Status:\n')
reportContent.append('- NAVEX Delivery: ' + (properties.get('NAVEXDeliveryStatus') ?: 'Unknown') + '\n')
reportContent.append('- Internal Archive: ' + (properties.get('ArchiveStatus') ?: 'Unknown') + '\n')
reportContent.append('- Generated Filename: ' + (properties.get('GeneratedFilename') ?: 'Unknown') + '\n\n')

// Error summary
if (properties.get('ErrorCount') && Integer.parseInt(properties.get('ErrorCount')) > 0) {
    reportContent.append('Error Summary:\n')
    reportContent.append('- Business Rule Errors: ' + (properties.get('RPT_INT_ALL_BRULE_ERR_CNT') ?: '0') + '\n')
    reportContent.append('- Validation Errors: ' + (properties.get('RPT_INT_ALL_CLEANSE_ERR_CNT') ?: '0') + '\n')
    reportContent.append('- Decision Errors: ' + (properties.get('RPT_INT_ALL_DECISION_ERR_CNT') ?: '0') + '\n')
    reportContent.append('- Route Errors: ' + (properties.get('RPT_INT_ALL_ROUTE_ERR_CNT') ?: '0') + '\n')
    reportContent.append('- General Errors: ' + (properties.get('RPT_INT_ALL_GENERAL_ERR_CNT') ?: '0') + '\n')
}

message.setBody(reportContent.toString())
return message