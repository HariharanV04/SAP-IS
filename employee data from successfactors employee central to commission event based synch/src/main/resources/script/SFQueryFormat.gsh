import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import com.sap.it.api.ITApiFactory;
import com.sap.it.api.mapping.ValueMappingApi;

/* This scripts builds the query to get the Employee data from SuccessFactors . */

def Message processData(Message message) {
	 
	 def body = message.getBody(java.lang.String);
     def xmlmessage = new XmlSlurper().parseText(body);
       

 def getPayees = { xml -> xml.'**'.findAll{it.name() == 'userId'} };
 def Payees= Payees = getPayees(xmlmessage);

String PayeeID=Payees.join(",") 

 
	def pMap = message.getProperties();
	
	def adhocrun_ext = pMap.get("adhocrun");
	def valueMapApi = ITApiFactory.getApi(ValueMappingApi.class, null);
    def Sf_select_field = valueMapApi.getMappedValue("SuccessFactors", "PerPerson", "SFFields", "Commission", "Participant");
    def Sf_entities = valueMapApi.getMappedValue("SuccessFactors", "PerPerson", "SFEntities", "Commission", "Participant");
     def sfkey = valueMapApi.getMappedValue("SuccessFactors", "PerPerson", "SFKey", "Commission", "Participant");
   
    def EOT=pMap.get("EndOfTime");
    
	StringBuffer str = new StringBuffer();
	StringBuffer commstr = new StringBuffer();
	StringBuffer query = new StringBuffer();
	DateFormat dateFormat= new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
	Date date = new Date();
	
	
    message.setProperty("SelectStr",Sf_select_field.toString());
    message.setProperty("Entity",Sf_entities.toString());
    
	
	commstr.append ("(effectiveEndDate eq " +EOT+ ")");
	

	if(!(PayeeID.trim().isEmpty()))
	{			
		   if (PayeeID.contains(","))
		{
    		def pid=PayeeID.split(',').collect{it as String};
    		str.append(" (");
    		commstr.append (" and (");
    		int x = 1
    		for (payee in pid)
    		{
    		if ( x == pid.size()) 
    		{
    		    str.append(" "+sfkey+" eq '" + payee + "')");
    		    commstr.append (" payeeId eq '" + payee + "')");
    		}
    		else 
    		{
    		    str.append(" "+sfkey+" eq '" + payee + "' or");
    		    commstr.append (" payeeId eq '" + payee + "' or");
    		}
    		x++;
    		}
		}
		else
		{
    	str.append(" "+sfkey+" eq '" + PayeeID + "'");
    	commstr.append (" and  payeeId eq '" + PayeeID + "'");
		}

	}

	message.setProperty("QueryFilter",str.toString());
	message.setProperty("CommFilter",commstr.toString());
	
	if (Sf_select_field != "" || Sf_select_field.toString().toUpperCase() != "ALL")
	{
	    query.append("\$select=");
	    query.append(Sf_select_field.toString());
	    query.append("&")
	}
	
	if (Sf_entities )
	{
	    query.append("\$expand=");
	    query.append(Sf_entities.toString());
	    query.append("&")
	}
	
	if (str != "" )
	{
	    query.append("\$filter=");
	    query.append(str.toString());
	}
	
	message.setProperty("Query",query.toString());
	

	return message;
}