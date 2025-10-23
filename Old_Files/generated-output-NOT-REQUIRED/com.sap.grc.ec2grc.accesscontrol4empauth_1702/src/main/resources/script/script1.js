/*
/*
 * The integration developer needs to create the method processData 
 * This method takes Message object of package com.sap.gateway.ip.core.customdev.util
 * which includes helper methods useful for the content developer:
 * 
 * The methods available are:
    public java.lang.Object getBody()
    
    //This method helps User to retrieve message body as specific type ( InputStream , String , byte[] ) - e.g. message.getBody(java.io.InputStream)
    public java.lang.Object getBody(java.lang.String fullyQualifiedClassName)

    public void setBody(java.lang.Object exchangeBody)

    public java.util.Map<java.lang.String,java.lang.Object> getHeaders()

    public void setHeaders(java.util.Map<java.lang.String,java.lang.Object> exchangeHeaders)

    public void setHeader(java.lang.String name, java.lang.Object value)

    public java.util.Map<java.lang.String,java.lang.Object> getProperties()

    public void setProperties(java.util.Map<java.lang.String,java.lang.Object> exchangeProperties) 

 * 
 */

importClass(com.sap.gateway.ip.core.customdev.util.Message);
importClass(java.util.HashMap);

 
function processData(message) {

	var map = message.getProperties();
	var CustomFromDateTime = map.get("ExecutionFromDate");
	var LastRunDateTime= map.get("LastRunDateTime");
	var FutureNoOfDays= map.get("FutureNoOfDays");
	var ToDate;
	var FromDate;
	
	if (CustomFromDateTime != null && CustomFromDateTime != "") {
		CustomFromDateTime.trim();
		message.setProperty("maxDateFromLastRun", map.get("ExecutionFromDate"));
		FromDate = "\'" + CustomFromDateTime.substring(0,10) + "\'";
		message.setProperty("FromDate", FromDate);
	} else {
		message.setProperty("maxDateFromLastRun", LastRunDateTime);
		FromDate = "\'" + LastRunDateTime.substring(0,10) + "\'";
		message.setProperty("FromDate", FromDate);
	}
	
	
	var currentDate = new Date();
	if (FutureNoOfDays == null || FutureNoOfDays == "") {
//		message.setProperty("currentDateTime", currentDate.toISOString());
		ToDate = currentDate.toISOString();
		ToDate = "\'" + ToDate.substring(0,10) + "\'";
		message.setProperty("ToDate", ToDate);
		
	} else {
		FutureNoOfDays.trim(); 
		var value = parseInt(FutureNoOfDays,10);
		currentDate.setDate(currentDate.getDate()+ value);
//		message.setProperty("currentDateTime", currentDate.toISOString());
		ToDate = currentDate.toISOString();
		ToDate = "\'" + ToDate.substring(0,10) + "\'";
		message.setProperty("ToDate", ToDate);
	}
	
	return message;
}

