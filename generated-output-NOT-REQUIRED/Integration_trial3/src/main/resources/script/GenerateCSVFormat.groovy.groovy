// Generate CSV format for NAVEX delivery
import groovy.json.JsonSlurper

def jsonSlurper = new JsonSlurper()
def records = jsonSlurper.parseText(message.getBody(String.class))
def csvContent = new StringBuilder()

// CSV Header
def headers = ['GPID', 'First Name', 'Last Name', 'Email Address', 'emplStatus', 'employee-class', 'pay-grade', 'Position Title', 'Is Union Employee', 'Participating in Union', 'location', 'Region', 'Sector', 'Country', 'manager-id', 'User ID', 'Relationship Type', 'Manager name', 'HRA Manager name', 'Termination Date', 'Termination Reason', 'Original Hire Date']
csvContent.append(headers.join(',') + '\n')

// CSV Data Rows
records.each { record ->
    def row = headers.collect { header ->
        def value = record[header] ?: ''
        // Escape CSV special characters
        if (value.contains(',') || value.contains('"') || value.contains('\n')) {
            value = '"' + value.replace('"', '""') + '"'
        }
        return value
    }
    csvContent.append(row.join(',') + '\n')
}

message.setBody(csvContent.toString())
properties.put('RecordCount', records.size().toString())
return message