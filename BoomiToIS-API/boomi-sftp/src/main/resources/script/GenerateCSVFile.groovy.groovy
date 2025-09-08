// Generate CSV file from transformed employee data
import groovy.json.JsonSlurper

def jsonSlurper = new JsonSlurper()
def records = jsonSlurper.parseText(message.getBody(String.class))

if (!records || records.isEmpty()) {
    message.setProperty('RECORD_COUNT', '0')
    message.setBody('')
    return message
}

// Define CSV headers
def headers = ['GPID', 'First Name', 'Last Name', 'Email Address', 'emplStatus', 'employee-class', 'Country', 'Location', 'Manager name', 'Termination Date', 'Original Hire Date']

// Build CSV content
def csvContent = new StringBuilder()
csvContent.append(headers.join(',') + '\n')

records.each { record ->
    def row = headers.collect { header ->
        def value = record[header] ?: ''
        // Escape quotes and wrap in quotes if contains comma or quote
        if (value.contains(',') || value.contains('"') || value.contains('\n')) {
            value = '"' + value.replace('"', '""') + '"'
        }
        return value
    }
    csvContent.append(row.join(',') + '\n')
}

message.setProperty('RECORD_COUNT', records.size().toString())
message.setProperty('FILE_NAME', 'employees_' + new Date().format('yyyyMMdd_HHmmss') + '.csv')
message.setBody(csvContent.toString())

return message