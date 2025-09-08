// Transform SuccessFactors employee data to NAVEX format
import groovy.json.JsonBuilder
import groovy.json.JsonSlurper

def jsonSlurper = new JsonSlurper()
def inputData = jsonSlurper.parseText(message.getBody(String.class))

def transformedRecords = []

inputData.d.results.each { employee ->
    def record = [:]
    
    // Map basic employee information
    record['GPID'] = employee.person_id_external
    record['First Name'] = employee.personal_information?.first_name ?: ''
    record['Last Name'] = employee.personal_information?.last_name ?: ''
    record['Email Address'] = employee.employment_information?.email_address ?: ''
    
    // Map employment status with picklist translation
    def empStatus = employee.employment_information?.employment_status
    record['emplStatus'] = translatePicklistValue('employment_status', empStatus)
    
    // Map employee class with picklist translation
    def empClass = employee.employment_information?.employee_class
    record['employee-class'] = translatePicklistValue('employee_class', empClass)
    
    // Map location and country information
    record['Country'] = employee.employment_information?.location?.country ?: ''
    record['Location'] = employee.employment_information?.location?.name ?: ''
    
    // Map manager information
    record['Manager name'] = employee.employment_information?.manager?.name ?: ''
    
    // Map employment dates with standardized formatting
    record['Termination Date'] = formatDate(employee.employment_information?.termination_date)
    record['Original Hire Date'] = formatDate(employee.employment_information?.hire_date)
    
    transformedRecords.add(record)
}

def result = new JsonBuilder(transformedRecords)
message.setBody(result.toString())

return message

// Helper function to translate picklist values
def translatePicklistValue(picklistType, value) {
    def picklistData = message.getProperty('PICKLIST_' + picklistType.toUpperCase())
    if (picklistData && value) {
        def translation = picklistData.find { it.optionId == value }
        return translation?.label ?: value
    }
    return value ?: ''
}

// Helper function to format dates
def formatDate(dateString) {
    if (!dateString) return ''
    try {
        def date = Date.parse("yyyy-MM-dd'T'HH:mm:ss'Z'", dateString)
        return date.format('yyyy-MM-dd')
    } catch (Exception e) {
        return dateString
    }
}