// Construct dynamic OData filter expressions for SuccessFactors queries
def legalEntities = message.getProperty('LEGAL_ENTITY_FILTER')
def employeeClasses = message.getProperty('EMPLOYEE_CLASS_FILTER')
def territories = message.getProperty('TERRITORY_FILTER')
def deltaEnabled = message.getProperty('DELTA_PROCESSING_ENABLED')

def filterParts = []

if (legalEntities) {
    filterParts.add("legal_entity_code in ('" + legalEntities.split(',').join("','") + "')")
}

if (employeeClasses) {
    filterParts.add("employee_class in ('" + employeeClasses.split(',').join("','") + "')")
}

if (territories) {
    filterParts.add("company_territory_code in ('" + territories.split(',').join("','") + "')")
}

filterParts.add("employment_status eq 'A'")

if (deltaEnabled == 'true') {
    def lastRunDate = message.getProperty('LAST_RUN_DATE')
    if (lastRunDate) {
        filterParts.add("last_modified_on gt datetime'" + lastRunDate + "'")
    }
}

def finalFilter = filterParts.join(' and ')
message.setProperty('ODATA_FILTER', finalFilter)

return message