import com.sap.it.api.mapping.*;
import com.sap.it.api.mapping.MappingContext;

def String isRelevantCompany(String property_name, String companyCode, MappingContext context) {
    def relevantCompanies = context.getProperty(property_name);
	def relevantCompaniesSplitted = relevantCompanies.replace("'","").split(",")*.trim();
    
    return (companyCode in relevantCompaniesSplitted);
}