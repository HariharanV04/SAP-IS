import com.sap.it.api.mapping.*;
import com.sap.it.api.mapping.MappingContext;

def String isRelevantCountry(String property_name, String countryCode, MappingContext context) {
    def relevantCountries = context.getProperty(property_name);
	def relevantCountriesSplitted = relevantCountries.replace("'","").split(",")*.trim();
    
    return (countryCode in relevantCountriesSplitted);
}