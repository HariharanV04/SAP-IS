// Build dynamic WHERE clause for SuccessFactors OData query
def whereClause = ''
def filters = []

// GPID filtering
if (properties.get('Filter_GPID') != null && !properties.get('Filter_GPID').isEmpty()) {
    def gpids = properties.get('Filter_GPID').split(',')
    def gpidFilter = "person_id_external in ('" + gpids.join("','") + "')"
    filters.add(gpidFilter)
}

// Territory code filtering
if (properties.get('Filter_company_territory_code') != null && !properties.get('Filter_company_territory_code').isEmpty()) {
    def territories = properties.get('Filter_company_territory_code').split(',')
    def territoryFilter = "company_territory_code in ('" + territories.join("','") + "')"
    filters.add(territoryFilter)
}

// Employee class filtering
if (properties.get('Filter_EmployeeClass') != null && !properties.get('Filter_EmployeeClass').isEmpty()) {
    def classes = properties.get('Filter_EmployeeClass').split(',')
    def classFilter = "employee_class in ('" + classes.join("','") + "')"
    filters.add(classFilter)
}

// Legal entity filtering
if (properties.get('Filter_LegalEntity') != null && !properties.get('Filter_LegalEntity').isEmpty()) {
    def entities = properties.get('Filter_LegalEntity').split(',')
    def entityFilter = "legal_entity_code in ('" + entities.join("','") + "')"
    filters.add(entityFilter)
}

// Date range filtering
if (properties.get('FileType') == 'Delta' && properties.get('Filter_LSRD') != null) {
    def lsrd = properties.get('Filter_LSRD')
    def dateFilter = "last_modified_on gt datetime'" + lsrd + "'"
    filters.add(dateFilter)
} else if (properties.get('FileType') == 'Full') {
    def startDate = properties.get('Full_File_Start_Date')
    def dateFilter = "effective_end_date >= '" + startDate + "'"
    filters.add(dateFilter)
}

// Combine all filters
if (filters.size() > 0) {
    whereClause = filters.join(' and ')
}

properties.put('DynamicWhereClause', whereClause)
return message