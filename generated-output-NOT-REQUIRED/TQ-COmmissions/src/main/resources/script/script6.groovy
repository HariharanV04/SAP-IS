import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.json.*;

def Message processData(Message message) {    
    //Body 
    def body = message.getBody(String.class); 
    //def properties = message.getProperties();
    def jsonSlurper = new JsonSlurper()
    def list = jsonSlurper.parseText(body);
    def jobsummaryID=list.backgroundJobSummarySeq.toString();
    //println jobsummaryID
    //jobsummary = jobsummaryID.replaceAll("[","").replaceAll("]","");
    def jobsummary = jobsummaryID.replace("[","").replace("]","");
    println jobsummary

    message.setProperty("tqjobsummaryseq", jobsummary)

    return message;
}
