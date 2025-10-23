// Transform SuccessFactors Employee Central data to NAVEX format
import groovy.json.JsonSlurper
import groovy.json.JsonBuilder

def jsonSlurper = new JsonSlurper()
def employeeData = jsonSlurper.parseText(message.getBody(String.class))
def picklistCache = properties.get('PicklistCache')
def transformedRecords = []

employeeData.d.results.each { employee ->
    def navexRecord = [:]
    
    // Core identity mappings
    navexRecord['GPID'] = employee.person_id_external?.split('-')[0] ?: ''
    navexRecord['First Name'] = employee.first_name ?: ''
    navexRecord['Last Name'] = employee.last_name ?: ''
    navexRecord['Email Address'] = employee.email_address ?: ''
    
    // Employment status with picklist lookup
    navexRecord['emplStatus'] = lookupPicklistValue(picklistCache, 'employee-status', employee.employment_status)
    navexRecord['employee-class'] = lookupPicklistValue(picklistCache, 'GlobalEmployeeClass', employee.employee_class)
    navexRecord['pay-grade'] = employee.pay_grade ?: ''
    navexRecord['Position Title'] = employee.custom_string15 ?: ''
    
    // Union information
    navexRecord['Is Union Employee'] = employee.custom_string30 ?: ''
    navexRecord['Participating in Union'] = employee.custom_string31 ?: ''
    
    // Location and organizational hierarchy
    navexRecord['location'] = buildLocationString(employee)
    navexRecord['Region'] = employee.employment_information?.region?.externalName_en_US ?: ''
    navexRecord['Sector'] = employee.employment_information?.sector?.externalName_en_US ?: ''
    navexRecord['Country'] = translateCountryCode(employee.company_territory_code)
    
    // Management hierarchy
    navexRecord['manager-id'] = employee.manager_id?.split('-')[0] ?: ''
    navexRecord['User ID'] = employee.user_id?.split('-')[0] ?: ''
    navexRecord['Relationship Type'] = lookupPicklistValue(picklistCache, 'jobRelType', employee.relationship_type)
    navexRecord['Manager name'] = lookupManagerName(employee.manager_person_id_external)
    navexRecord['HRA Manager name'] = lookupHRManagerName(employee.user_id)
    
    // Employment dates
    navexRecord['Termination Date'] = formatDate(employee.end_date)
    navexRecord['Termination Reason'] = calculateTerminationReason(employee.employment_status, employee.event_reason)
    navexRecord['Original Hire Date'] = calculateOriginalHireDate(employee.person_id_external, employee.original_start_date)
    
    transformedRecords.add(navexRecord)
}

def result = new JsonBuilder(transformedRecords)
message.setBody(result.toString())
return message

// Helper functions
def lookupPicklistValue(cache, picklistId, code) {
    // Implementation for picklist lookup
    return code // Simplified for example
}

def buildLocationString(employee) {
    def parts = [employee.location, employee.custom_string19, employee.custom_string14, employee.name].findAll { it }
    return parts.join(' ')
}

def translateCountryCode(territoryCode) {
    def countryMap = ['US': 'United States', 'CA': 'Canada', 'MX': 'Mexico']
    return countryMap[territoryCode] ?: territoryCode
}

def lookupManagerName(managerId) {
    // Implementation for manager name lookup
    return managerId // Simplified for example
}

def lookupHRManagerName(userId) {
    // Implementation for HR manager lookup
    return userId // Simplified for example
}

def formatDate(dateString) {
    // Format date from SuccessFactors format to MM/dd/yyyy
    return dateString // Simplified for example
}

def calculateTerminationReason(status, reason) {
    // Business logic for termination reason
    return reason // Simplified for example
}

def calculateOriginalHireDate(personId, startDate) {
    // Business logic for original hire date calculation
    return startDate // Simplified for example
}