import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Callable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import groovy.transform.Field;
import groovy.xml.XmlUtil;


@Field String IFLOW_NAME = 'IN1100'

@Field String FILE_LOGGING_MODE = 'ALWAYS';  //ALWAYS, NEVER , PROPERTY
@Field String MPL_LOGGING_MODE = 'ALWAYS';   //ALWAYS, NEVER, PROPERTY

@Field List EXCLUDE_PROPERTIES = ['SAP_MessageProcessingLogID', 'SAP_MonitoringStateProperties', 'MplMarkers', 'SAP_MessageProcessingLog'];
@Field List EXCLUDE_HEADERS = [''];

@Field String LOG_HEADERS       = 'YES';   //YES / NO
@Field String LOG_PROPERTIES    = 'YES';   //YES / NO
@Field String LOG_BODY_INFO     = 'NO';   //YES / NO
@Field String LOG_EXCEPTION     = 'YES';   //YES / NO
@Field String LOG_OTHER         = 'YES';   //YES / NO
@Field String LOG_BODY          = 'YES';   //YES / NO


// if you use this method, you need to copy the script for every usage and adapt the filename (000)
def Message processData(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		
		//def props = message.getProperties();
		//def some_value = props.get('some_property');
		
		processHeadersAndProperties(IFLOW_NAME+"_000", message);
		processBody(IFLOW_NAME+"_000_payload", message, 'text/plain');
		
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	return message;
}


// you can use _010, _020 etc methods to reuse same script from multiple places in the iflow

def boolean isLoggingEnabled( Message message ) {

  def props = message.getProperties();
  def list = [ "YES", "TRUE", "ENABLED", "ON", "USE", "ALWAYS" ];  
  String DO_LOG = props.get("loggingEnabled");
  def result = list.find { DO_LOG.equalsIgnoreCase( it )  };

  if ( result == null )
    return false;

  return true;

}


def Message log_EC_Payload(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		def props = message.getHeaders();
		def String log_id = props.get("SAP_MessageProcessingLogID");
		
		if ( isLoggingEnabled( message ) ) {
			//processHeadersAndProperties(    log_id + "_EC_Headers",    message);
			processBody(IFLOW_NAME + "_1_EC_Payload_" + log_id, message, 'text/xml');
		}

	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	return message;
}

def Message log_305(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		def props = message.getHeaders();
		def String log_id = props.get("SAP_MessageProcessingLogID");

		if ( isLoggingEnabled( message ) ) {
			//processHeadersAndProperties(    log_id + "_",    message);
			processBody(IFLOW_NAME + "_2_305_CSV_" + log_id, message, 'text/csv');
		}
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	return message;
}


def Message log_320(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		def props = message.getHeaders();
		def String log_id = props.get("SAP_MessageProcessingLogID");

		if ( isLoggingEnabled( message ) ) {			
			//processHeadersAndProperties(    log_id+"-SIGNED",          	 message);
			processBody(IFLOW_NAME + "_3_320_CSV_" + log_id, message, 'text/csv');
		}
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	return message;
}

def Message log_350(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		def props = message.getHeaders();
		def String log_id = props.get("SAP_MessageProcessingLogID");

		if ( isLoggingEnabled( message ) ) {			
			//processHeadersAndProperties(    log_id+"-SIGNED",          	 message);
			processBody(IFLOW_NAME + "_4_350_CSV_" + log_id, message, 'text/csv');
		}
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	return message;
}


def Message error(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	def props = message.getHeaders();
	def String log_id = props.get("SAP_MessageProcessingLogID");
	
	try {
		processData(IFLOW_NAME + "_Error_" + log_id, message);
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	// get an exception java class instance
	    def map = message.getProperties();
        def errorMessage = map.get("CamelExceptionCaught");
	    processException(IFLOW_NAME + "_Error_" + log_id, message, errorMessage.getMessage()); 
	try {
	    
          
	} catch (Exception ex) {
		log.error("processData error" , ex);
	}
	
	return message;
}


def Message processDataWithCounterIncreasing(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		processDataIncreasing("LOG_", "COUNTER", message);
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
	return message;
}



def Message processDataIncreasing(String prefix, String propertyName, Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	def props = message.getProperties();
	def StringBuffer counter = props.get(propertyName);
	if (counter==null) {
		counter = new StringBuffer();
		counter.append("0");
		message.setProperty(propertyName, counter);
	}
	
	int cnt = Integer.valueOf(counter.toString());
	cnt = cnt+1;
	def counterS = ""+cnt;
	counter.setLength(0);
	counter.append(counterS);
	processData(prefix+"_"+counter, message);
	return message;
}





// use this method if you want to have an counter in file name
// this method does not increase the counter after usage
def Message processDataWithCounter(Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	
	try {
		def props = message.getProperties();
		def String counter = props.get("COUNTER");
		if ((counter==null)||("".equals(counter))) {
			counter = "0";
		}
		return processData("LOG_"+counter, message);
		
	} catch (Exception ex) {
		log.error("processData error",ex);
	}
}


def Message processData(String prefix, Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	try {
		processBody(prefix + "_payload", message, 'text/plain');
		//processHeadersAndProperties(prefix, message);
	} catch (Exception ex00) {
		log.error("processData error",ex00)
		StringWriter sw = new StringWriter();
		ex00.printStackTrace(new PrintWriter(sw));
		log.error(sw.toString());
	}
	return message;
}

def Message processException(String prefix, Message message, String errorMessage) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	try {
		processBody(prefix + "_exception", message, 'text/plain', errorMessage);
		//processHeadersAndProperties(prefix, message);
	} catch (Exception ex00) {
		log.error("processData error",ex00)
		StringWriter sw = new StringWriter();
		ex00.printStackTrace(new PrintWriter(sw));
		log.error(sw.toString());
	}
	return message;
}


def Map excludeEntries(Map map, List excluded) {
	def newMap = new HashMap();
	newMap.putAll(map);
	newMap.keySet().removeAll(excluded);
	return newMap;
	
}



def void processBody(String prefix, Message message, String fileFormat, def errorMessage = null) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	def byte[] body_bytes = null;
	try {
		
		def enable = false;
	
		if ('YES'.equalsIgnoreCase(LOG_BODY)) {
			enable = true;
		}
			
		if (!enable) return;
		
		if (errorMessage != null)
		    body_bytes = errorMessage;
		else if (message == null) {
			body_bytes = new byte[0];
		} else if (message.getBody() == null) {
			body_bytes = new byte[0];
		} else {
			body_bytes = message.getBody(byte[].class);
		}
		
		def props = message.getProperties();
		def property_ENABLE_MPL_LOGGING = props.get("ENABLE_MPL_LOGGING");
		def property_ENABLE_FILE_LOGGING = props.get("ENABLE_FILE_LOGGING");
		
		def mpl_enabled = false;
		if ("ALWAYS".equalsIgnoreCase(MPL_LOGGING_MODE)) {
			mpl_enabled = true;
		} else if ("YES".equalsIgnoreCase(MPL_LOGGING_MODE)) {
		   mpl_enabled = true;
		} else ("PROPERTY".equalsIgnoreCase(MPL_LOGGING_MODE)) {
			if ("TRUE".equalsIgnoreCase(property_ENABLE_MPL_LOGGING)) {
				mpl_enabled = true;
			}
		}
		
		
		def file_enabled = false;
		if ("ALWAYS".equalsIgnoreCase(FILE_LOGGING_MODE)) {
			file_enabled = true;
		} else if ("YES".equalsIgnoreCase(FILE_LOGGING_MODE)) {
			mpl_enabled = true;
		} else ("PROPERTY".equalsIgnoreCase(FILE_LOGGING_MODE)) {
			if ("TRUE".equalsIgnoreCase(property_ENABLE_FILE_LOGGING)) {
				file_enabled = true;
			}
		}
		
		
		
		if (mpl_enabled) {
			def messageLog = messageLogFactory.getMessageLog(message);
			messageLog.addAttachmentAsString(prefix, new String(body_bytes), fileFormat);
		}
		
		if (file_enabled) {
			ExecutorService pool = Executors.newSingleThreadExecutor();
			def task = {c -> pool.submit( c as Callable)}
			task{saveFile("" + prefix + ".xml", body_bytes)}
		}
		
		
	} catch (Exception ex01) {
		log.error("cannot save body",ex01);
		StringWriter sw = new StringWriter();
		ex01.printStackTrace(new PrintWriter(sw));
		log.info(sw.toString());
	}
}

def void processHeadersAndProperties(String prefix, Message message) {
	Logger log = LoggerFactory.getLogger(this.getClass());
	try {
		def StringBuffer sb_html = new StringBuffer();
		def StringBuffer sb_text = new StringBuffer();
		def map = message.getHeaders();
		
		def enable = false;
		if ('YES'.equalsIgnoreCase(LOG_HEADERS)) {
			enable = true;
		}
		
		if (enable) {
			map = excludeEntries(map, EXCLUDE_HEADERS);
			dumpProperties_HTML("Headers", map, sb_html);
			dumpProperties_TEXT("Headers", map, sb_text);
		}
		
		
		map = message.getProperties();
		
		enable = false;
		if ('YES'.equalsIgnoreCase(LOG_PROPERTIES)) {
			enable = true;
		}

		if (enable) {
			map = excludeEntries(map, EXCLUDE_PROPERTIES);
			dumpProperties_HTML("Properties", map, sb_html);
			dumpProperties_TEXT("Properties", map, sb_text);
		}
		
		
		enable = false;
		if ('YES'.equalsIgnoreCase(LOG_EXCEPTION)) {
			enable = true;
		}
		
		if (enable) {
			
		def ex = map.get("CamelExceptionCaught");
		if (ex!=null) {
			
			def exmap = new HashMap();
			exmap.put("exception",ex);
			exmap.put("getCanonicalName",ex.getClass().getCanonicalName());
			exmap.put("getMessage",ex.getMessage());
			
			StringWriter swe = new StringWriter();
			ex.printStackTrace(new PrintWriter(swe));
			exmap.put("stacktrace",swe.toString());
			
			if (ex.getClass().getCanonicalName().equals("org.apache.camel.component.ahc.AhcOperationFailedException")) {
				exmap.put("responseBody",org.apache.commons.lang.StringEscapeUtils.escapeXml(ex.getResponseBody()));
				exmap.put("getStatusText",ex.getStatusText());
				exmap.put("getStatusCode",ex.getStatusCode());
			}
			
			if (ex instanceof org.apache.cxf.interceptor.Fault) {
				exmap.put("getDetail",org.apache.commons.lang.StringEscapeUtils.escapeXml(ex.getDetail()));
				exmap.put("getFaultCode",ex.getFaultCode());
				exmap.put("getMessage",ex.getMessage());
				exmap.put("getStatusCode",""+ex.getStatusCode());
				exmap.put("hasDetails",""+ex.hasDetails());
				
				//message.getHeaders().put("SoapFaultMessage", ex.getMessage());
				exmap.put("getCause",""+ex.getCause());
				
				def cause_message = ex.getCause().getMessage();
				if (ex.getCause() instanceof org.apache.cxf.transport.http.HTTPException) {
					cause_message = ex.getCause().getResponseMessage();
				}
				exmap.put("getCause.getResponseMessage",""+cause_message);
				
				message.getHeaders().put("SoapFaultMessage", ex.getMessage() +": "+ ex.getCause().getResponseMessage());
				
			}
			
			
			dumpProperties_HTML("property.CamelExceptionCaught", exmap, sb_html);
			dumpProperties_TEXT("property.CamelExceptionCaught", exmap, sb_text);
		}
			
		}

		
		enable = false;
		if ('YES'.equalsIgnoreCase(LOG_BODY_INFO)) {
			enable = true;
		}
		
		if (enable) {

			def body_test = message.getBody();
			def bodymap = new HashMap();
			
			bodymap.put("Body",body_test);
			
			if (body_test!=null) {
				bodymap.put("CanonicalClassName",body_test.getClass().getCanonicalName());
			}
			
			
			
			dumpProperties_HTML("Body", bodymap, sb_html);
			dumpProperties_TEXT("Body", bodymap, sb_text);
			

		}
		
		
		enable = false;
		if ('YES'.equalsIgnoreCase(LOG_OTHER)) {
			enable = true;
		}
		
		if (enable) {
	   
			def othermap = new HashMap();
			def timestamp = new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssZ").format(new Date());
			othermap.put("timestamp",timestamp);
			dumpProperties_HTML("Others", othermap, sb_html);
			dumpProperties_TEXT("Others", othermap, sb_text);
			
			
			
		}
		
		
		
		def props = message.getProperties();
		def property_ENABLE_MPL_LOGGING = props.get("ENABLE_MPL_LOGGING");
		def property_ENABLE_FILE_LOGGING = props.get("ENABLE_FILE_LOGGING");
		
		def mpl_enabled = false;
		if ("ALWAYS".equalsIgnoreCase(MPL_LOGGING_MODE)) {
			mpl_enabled = true;
		} else if ("YES".equalsIgnoreCase(MPL_LOGGING_MODE)) {
			mpl_enabled = true;
		} else ("PROPERTY".equalsIgnoreCase(MPL_LOGGING_MODE)) {
			if ("TRUE".equalsIgnoreCase(property_ENABLE_MPL_LOGGING)) {
				mpl_enabled = true;
			}
		}
		
		
		def file_enabled = false;
		if ("ALWAYS".equalsIgnoreCase(FILE_LOGGING_MODE)) {
			file_enabled = true;
		} else if ("YES".equalsIgnoreCase(FILE_LOGGING_MODE)) {
			mpl_enabled = true;
		} else ("PROPERTY".equalsIgnoreCase(FILE_LOGGING_MODE)) {
			if ("TRUE".equalsIgnoreCase(property_ENABLE_FILE_LOGGING)) {
				file_enabled = true;
			}
		}
		
		
		if (mpl_enabled) {
			def messageLog = messageLogFactory.getMessageLog(message);
			messageLog.addAttachmentAsString(prefix, sb_text.toString(), "text/plain");
		}
		
		if (file_enabled) {
			ExecutorService pool = Executors.newSingleThreadExecutor();
			def task = {c -> pool.submit( c as Callable)}
			task{saveFile("" + prefix + ".html", sb_html.toString().getBytes())};
		}
		
	} catch (Exception ex01) {
		log.error("cannot save headers and properties",ex01)
		StringWriter sw = new StringWriter();
		ex01.printStackTrace(new PrintWriter(sw));
		log.info(sw.toString());
	}
	
}


public void saveFile(String fileName, byte[] bytes) {
	try {
		def String METVIEWER_FOLDER = "metviewer";
		java.nio.file.Path path = Paths.get(METVIEWER_FOLDER+"/"+fileName);
		path.toFile().delete();
		path.getParent().toFile().mkdir();
		if (bytes!=null) {
			Files.write(path, bytes, StandardOpenOption.CREATE);
		} else {
			Files.write(path, "".getBytes(), StandardOpenOption.CREATE);
		}
	} catch (Exception ex) {
		System.out.println("saveFile.exception: filename:"+fileName+" ex:"+ex);
		throw new RuntimeException(ex);
	}
}




public void dumpProperties(String title, Map<String, Object> map, StringBuffer sb) {
	sb.append(title+"\n");
	for (String key : map.keySet()) {
		sb.append(key+"\t"+map.get(key)+"\n");
	}
}

public void dumpProperties_HTML(String title, Map<String, Object> map, StringBuffer sb) {
	sb.append("<h1>"+title+"</h1><br>\n");
	sb.append("<table>\n");
	for (String key : map.keySet()) {
		sb.append("<tr>\n");
		sb.append("<td>"+key+"</td><td>"+map.get(key)+"</td>\n");
		sb.append("</tr>\n");
	}
	sb.append("</table>\n");
}


public void dumpProperties_TEXT(String title, Map<String, Object> map, StringBuffer sb) {
	sb.append(title+"\n");
	for (String key : map.keySet()) {
		sb.append(String.format(" %-40s: %-40s\n",key, map.get(key)));
	}
	sb.append("\n");
}
