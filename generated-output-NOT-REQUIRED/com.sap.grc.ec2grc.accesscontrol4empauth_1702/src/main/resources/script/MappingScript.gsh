import com.sap.gateway.ip.core.customdev.util.Message;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Map;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import org.xml.sax.SAXException;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Attr;

class XMLHelper {

	private XPath xPath;
	
	public XMLHelper() {
		XPathFactory factory = XPathFactory.newInstance();
		xPath = factory.newXPath();
	}
	
	// Create a new node with a tag name and value
	public Node createNode(String name, String value, Node newParentNode, Document doc) {		
		Node newNode = doc.createElement(name);
		newNode.setTextContent(value);		
		newParentNode.appendChild(newNode);
		return newNode;
	}

	// Create a new node based on an existing node
	public Node createNode(String name, Node baseNode, Node newParentNode, Document doc) {
		if (baseNode != null) {
			return createNode(name, baseNode.getNodeName(), newParentNode, doc);
		} else {
			return null;
		}
	}

	// Retrieve a node of a given path for a specific parent node
	public Node retrieveNodeOfParentNode(String path, Node parentNode) throws XPathExpressionException {		
		return (Node) this.xPath.evaluate(path, parentNode, XPathConstants.NODE);		
	}

	// Retrieve a value of Node
	public String getNodeValue(Node node) {		
		if (!node){
			String nodeValue = node.getTextContent();		
			return nodeValue;	
		}
	}

	// Retrieve a node of a given path for a specific parent node
	public Node retrieveNodeOfDocument(String path, Document doc) throws XPathExpressionException {
		return (Node) this.xPath.evaluate(path, doc, XPathConstants.NODE);
	}

	// Retrieve a list of nodes for a given path of a complete document or a
	// specific parent node
	public NodeList retrieveNodes(String path, Node parentNode, Document doc) {			
		try {
			if (doc == null) {
				return (NodeList) xPath.evaluate(path, parentNode, XPathConstants.NODESET);
			} else {
				return (NodeList) xPath.evaluate(path, doc, XPathConstants.NODESET);
			}
		} catch (XPathExpressionException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
	}
	
	public Document createXMLNodes(String sourceString) {
		DocumentBuilderFactory builderFactory = DocumentBuilderFactory.newInstance();
		builderFactory.setNamespaceAware(true);
		DocumentBuilder builder = null;
		try {
		    builder = builderFactory.newDocumentBuilder();
		    InputStream is = new ByteArrayInputStream(sourceString.getBytes(StandardCharsets.UTF_8));
			return builder.parse(is);
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParserConfigurationException e) {
		    e.printStackTrace();  
		}
		return null;
	}
}

def Message processData(Message message) {

	// add log entry for performance measurement
	System.out.println("Performance measurement: After Notification upsert. Before mapping script");
	
	// get payload (compound employee api query result)
    Document body = message.getBody(org.w3c.dom.Document);

	// initiate xml helper
	XMLHelper xmlHelper = new XMLHelper();
	

	// get process properties
// String extensibilityUsage = message.getProperty("EXTENSIBILITY_USAGE");
// String fullTransmissionStartDate =
// message.getProperty("FULL_TRANSMISSION_START_DATE");
// String replicationTargetSystem =
// message.getProperty("REPLICATION_TARGET_SYSTEM");
// String replicationStartedDateTime =
// message.getProperty("LAST_MODIFIED_DATE_TMP");
	
// String correctionPhaseIndicator = "false";
	
	
	String targetXML = "<ns2:GracSfecHrTriggerReceiver xmlns:ns2=\"urn:sap-com:document:sap:soap:functions:mc-style\"><UserChangeDetails/></ns2:GracSfecHrTriggerReceiver>";
	
		
	NodeList compoundEmployeeList = xmlHelper.retrieveNodes("//CompoundEmployee", null, body);
	
	// create erp inbound message
	Document employeeHRTriggerReceiverRequest = xmlHelper.createXMLNodes(targetXML);
	
	String[] arrEmployeeDetailsAttributesSFEC = ["./person/logon_user_name",
												"./person/email_information/email_address",
												"./person/employment_information/job_information/job_code",
												"./person/employment_information/job_information/position",
												"./person/employment_information/job_information/department",
												"./person/employment_information/job_information/company",
												"./person/employment_information/job_information/manager_id",
												"./person/employment_information/job_information/cost_center",
												"./person/personal_information/first_name",
												"./person/personal_information/last_name",
												"./person/phone_information/phone_number",
												"./person/employment_information/start_date",
												"./person/employment_information/end_date",
													"Title",
									               "SncName",
									               "UnsecSnc",
									               "Accno",
									               "UserGroup",
									              "./person/person_id_external", 
									               "Personnelarea",
									               "CommMethod",
									               "Fax",
									               "./person/employment_information/job_information/location",
									               "Printer",
									               "Orgunit",
									               "Emptype",
									               "ManagerEmail",
									               "ManagerFirstname",
									               "ManagerLastname",
									               "StartMenu",
									               "LogonLang",
									               "DecNotation",
									               "DateFormat",
									               "Alias",
									               "UserType",
									               "Companyid"
												];
	String[] arrEmployeeDetailsAttributesSAPAC = ["Userid",
				                              	"Email",
				                              	"Empjob",
				                              	"Empposition",
				                              	"Department",
				                              	"Company",
				                              	"Manager",
				                              	"Costcenter",
				                              	"Fname",
				                              	"Lname",
				                              	"Telnumber",
				                              	"ValidFrom",
				                              	"ValidTo",
													"Title",
									               "SncName",
									               "UnsecSnc",
									               "Accno",
									               "UserGroup",
									               "Personnelno",
									               "Personnelarea",
									               "CommMethod",
									               "Fax",
									               "Location",
									               "Printer",
									               "Orgunit",
									               "Emptype",
									               "ManagerEmail",
									               "ManagerFirstname",
									               "ManagerLastname",
									               "StartMenu",
									               "LogonLang",
									               "DecNotation",
									               "DateFormat",
									               "Alias",
									               "UserType",
									               "Companyid"
	         	                           ];


	String[] arrEmployeeChangeAttributesSFEC = ["./person/logon_user_name",
	                                        "./person/email_information/email_address",
	                                        "./person/personal_information/first_name",
	                                        "./person/personal_information/last_name",
	                                        "./person/person_id_external",
	         	                           	"./person/employment_information/job_information/business_unit",
	         	                           	"./person/employment_information/job_information/company",
	         	                           	"./person/employment_information/job_information/company_territory_code",
	         	                           	"./person/employment_information/job_information/department",
	         	                           	"./person/employment_information/job_information/division",
	         	                           	"./person/employment_information/job_information/job_code",
	         	                           	"./person/employment_information/job_information/position",
	         	                           	"./person/employment_information/job_information/emplStatus",
	         	                           	"./person/employment_information/job_information/event",
	         	                           	"./person/employment_information/job_information/start_date",
	         	                           	"./person/employment_information/end_date"
	         	                           ];
	String[] arrEmployeeChangeAttributesSAPAC = ["USERID",
	                                    "EMAIL",
	                                    "FNAME",
	                                    "LNAME",
	                                    "PERSONNELNO",
			                          	"BUSINESS_AREA",
			                          	"COMPANY",
			                          	"COMPANY_TERRITORY_CODE",
			                          	"DEPARTMENT",
			                          	"PERSONNELAREA",
			                          	"EMPJOB",
			                          	"EMPPOSITION",
			                          	"EMPLSTATUS",
			                          	"EVENT",
			                          	"VALID_FROM",
			                          	"VALID_TO"
	         	                           ];


    String[] arrEmployeeCustomFieldsSFEC = [
                                   	"./person/employment_information/job_information/company",
                                   	"./person/employment_information/job_information/job_code"
                                   	];

    String[] arrEmployeeCustomFieldsSAPAC = [
                                 	"ZVALUE",
                                 	"ZVALUE1"
                                 ];
	         	                         
	         	                             
	def messageBody  = message.getBody(java.lang.String) as String;
	def messageLog = messageLogFactory.getMessageLog(message);
	
    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    SimpleDateFormat dateGRCFormat = new SimpleDateFormat("yyyyMMdd");

	Node nodeUserChangeDetails = xmlHelper.retrieveNodeOfDocument("//UserChangeDetails", employeeHRTriggerReceiverRequest);


	// loop at queried employee master data records and create related nodes in
	// erp inbound message
	for (int i = 0; i < compoundEmployeeList.getLength(); i++) {	
		
		// get current emoyee data
		Node compoundEmployeeNode = compoundEmployeeList.item(i);
		
		Node actionNode = xmlHelper.retrieveNodeOfParentNode( "./person/employment_information/job_information/action", compoundEmployeeNode);
		String actionValue = "";
		if(actionNode!=null){
			actionValue = actionNode.getTextContent();
			System.out.println("Debug log- UserChangeDetails0: /person/employment_information/job_information/action - " + actionValue);
		}else{
			System.out.println("Debug log- UserChangeDetails1: Employee Attribute /person/employment_information/job_information/action not found");

		}

        Node nodeItem = xmlHelper.createNode("item", new String(), nodeUserChangeDetails, employeeHRTriggerReceiverRequest);

		for (int j = 0; j < arrEmployeeDetailsAttributesSFEC.length; j++) {
			attributeValue = "";
			attributeOldValue = "";
			attributeNode = xmlHelper.retrieveNodeOfParentNode( arrEmployeeDetailsAttributesSFEC[j], compoundEmployeeNode);
			if(attributeNode){ 
				attributeValue = attributeNode.getTextContent();
				System.out.println("Debug log- UserChangeDetails2: " + arrEmployeeDetailsAttributesSFEC[j] + "-" + attributeValue);
			}else{
				System.out.println("Debug log- UserChangeDetails3: Employee Attribute " + arrEmployeeDetailsAttributesSFEC[j] + " not found");
			}
			
			if (arrEmployeeDetailsAttributesSFEC[j].contains("logon_user_name") == true ) {
                if(attributeValue){
                messageBody = messageBody + ("Debug log- UserChangeDetails4: Employee Attribute "+ arrEmployeeDetailsAttributesSFEC[j] +" Logon User Value: " + attributeValue ) + "\n";
                                }
						    }
			
			if (attributeValue){
				String attributePreviousPath = arrEmployeeDetailsAttributesSFEC[j] + "/previous"
				attributeNodePrevious = xmlHelper.retrieveNodeOfParentNode( attributePreviousPath, compoundEmployeeNode);
				if(attributeNodePrevious){
						// <previous> tag found
						attributeOldValue = attributeNodePrevious.getTextContent();
						int lenValue = attributeValue.length() - attributeOldValue.length();
						int endPos = lenValue;
						if (endPos >= 0 ) {
						    attributeValue = attributeValue.substring(0, endPos);
						}else{
						   messageBody = messageBody + ("Debug log - UserChangeDetails5: Employee Attribute "+ arrEmployeeChangeAttributesSFEC[j] +" Changed Value:" + attributeValue ) + "\n"; 
						} 
				}else{
					attributeOldValue = "";
				}
			}
					if (arrEmployeeDetailsAttributesSFEC[j].contains("start_date") == true || arrEmployeeDetailsAttributesSFEC[j].contains("end_date") == true) {
						Date dateValue; 
						if(attributeValue){
							dateValue = dateFormat.parse(attributeValue);
							attributeValue = dateGRCFormat.format(dateValue);
						}
						if(attributeOldValue){
							dateValue = dateFormat.parse(attributeOldValue);
							attributeOldValue = dateGRCFormat.format(dateValue);
						}
					}
// Concatenate department description field to department field
            if (arrEmployeeDetailsAttributesSFEC[j].contains("department")) {
                Node descriptionNode = xmlHelper.retrieveNodeOfParentNode("./person/employment_information/job_information/FODepartment/description", compoundEmployeeNode);
                String descriptionValue = descriptionNode != null ? descriptionNode.getTextContent() : "";
                attributeValue = descriptionValue +" ("+ attributeValue +")";
            }

			xmlHelper.createNode(arrEmployeeDetailsAttributesSAPAC[j], attributeValue, nodeItem, employeeHRTriggerReceiverRequest);
		}


        Node nodeUserChange = xmlHelper.createNode("UserChange", new String(), nodeItem, employeeHRTriggerReceiverRequest);

		Node attributeNode;
		Node attributeNodePrevious;
		String attributeValue;
		String attributeOldValue;
		for (int j = 0; j < arrEmployeeChangeAttributesSFEC.length; j++) {
            
            // change should be only for field that is Changed
            actionValue = "";
            if (null != arrEmployeeChangeAttributesSFEC[j] && arrEmployeeChangeAttributesSFEC[j].length() > 0 )
            {
                int endIndex = arrEmployeeChangeAttributesSFEC[j].lastIndexOf("/");
                if (endIndex != -1)  
                {
                    String newstr = arrEmployeeChangeAttributesSFEC[j].substring(0, endIndex); 
                    actionStr = newstr + "/action";
        			actionNode = xmlHelper.retrieveNodeOfParentNode( actionStr , compoundEmployeeNode);
        			if(actionNode){ 
        				actionValue = actionNode.getTextContent();
        				System.out.println("Debug log- UserChange0: " + actionStr + "-" + actionValue);
        			}else{
        				System.out.println("Debug log- UserChange1: Employee Attribute " + actionStr + " not found");
        			}
                }
                
            } 
            
			attributeValue = "";
			attributeNode = xmlHelper.retrieveNodeOfParentNode( arrEmployeeChangeAttributesSFEC[j], compoundEmployeeNode);
			if(attributeNode){ 
				attributeValue = attributeNode.getTextContent();
				System.out.println("Debug log- UserChange2: " + arrEmployeeChangeAttributesSFEC[j] + "-" + attributeValue);
			}else{
				System.out.println("Debug log- UserChange3: Employee Attribute " + arrEmployeeChangeAttributesSFEC[j] + " not found");
			}
			if (attributeValue){
				String attributePreviousPath = arrEmployeeChangeAttributesSFEC[j] + "/previous"
				attributeNodePrevious = xmlHelper.retrieveNodeOfParentNode( attributePreviousPath, compoundEmployeeNode);
				if(attributeNodePrevious){
						// <previous> tag found
						attributeOldValue = attributeNodePrevious.getTextContent();
						int lenValue = attributeValue.length() - attributeOldValue.length();
						int endPos = lenValue;
						if (endPos >= 0 ) {
						    attributeValue = attributeValue.substring(0, endPos);
						}else{
						   messageBody = messageBody + ("Debug log- UserChange4: Employee Attribute "+ arrEmployeeChangeAttributesSFEC[j] +" Changed Value:" + attributeValue ) + "\n"; 
						}  
						// if there is previous tag then actionValue should be change
						actionValue = "CHANGE"; 

				}else{
					attributeOldValue = "";
				}


    			if (arrEmployeeChangeAttributesSFEC[j].contains("start_date") == true || arrEmployeeChangeAttributesSFEC[j].contains("end_date") == true) {
    				Date dateValue; 
    				if(attributeValue){
    					dateValue = dateFormat.parse(attributeValue);
    					attributeValue = dateGRCFormat.format(dateValue);
    				}
    				if(attributeOldValue){
    					dateValue = dateFormat.parse(attributeOldValue);
    					attributeOldValue = dateGRCFormat.format(dateValue);
    					// if there is previous tag then actionValue should be change
						actionValue = "CHANGE"; 
    				}
    			}
    			
    			if(arrEmployeeChangeAttributesSFEC[j].contains("end_date") == true){
    			    attributeValue = "";
        			attributeNode = xmlHelper.retrieveNodeOfParentNode( "./person/employment_information/start_date", compoundEmployeeNode);
        			if(attributeNode){ 
        				attributeValue = attributeNode.getTextContent();
        				if(attributeValue){
        					dateValue = dateFormat.parse(attributeValue);
        					attributeValue = dateGRCFormat.format(dateValue);
        				}
        				messageBody = messageBody + ("Debug log- UserChange5: Employee Attribute "+ attributeNode +" Changed Value:" + attributeValue ) + "\n"; 
        			}
    			}


			    Node nodeUserChangeItem = xmlHelper.createNode("item", new String(), nodeUserChange, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("FieldName1", arrEmployeeChangeAttributesSAPAC[j], nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("NewValue1", attributeValue, nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("OldValue1", attributeOldValue, nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("FieldName2", "ACTION", nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("NewValue2", actionValue, nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("OldValue2", new String(), nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("FieldName3", new String(), nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("NewValue3", new String(), nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("OldValue3", new String(), nodeUserChangeItem, employeeHRTriggerReceiverRequest);
			}

		}

	    Node nodeCustomFields = xmlHelper.createNode("CustomFields", new String(), nodeItem, employeeHRTriggerReceiverRequest);

		//Node attributeNode;
		//Node attributeNodePrevious;
		//String attributeValue;
		//String attributeOldValue;
		for (int j = 0; j < arrEmployeeCustomFieldsSFEC.length; j++) {
//			//Fortesting
//			if (j == 0){
//				break;
//			} 

			attributeValue = "";
			attributeNode = xmlHelper.retrieveNodeOfParentNode( arrEmployeeCustomFieldsSFEC[j], compoundEmployeeNode);
			if(attributeNode){ 
				attributeValue = attributeNode.getTextContent();
				System.out.println("Debug log: " + arrEmployeeCustomFieldsSFEC[j] + "-" + attributeValue);
			}else{
				System.out.println("Debug log: Employee Attribute " + arrEmployeeCustomFieldsSFEC[j] + " not found");
			}
			if (attributeValue){
				String attributePreviousPath = arrEmployeeCustomFieldsSFEC[j] + "/previous"
				attributeNodePrevious = xmlHelper.retrieveNodeOfParentNode( attributePreviousPath, compoundEmployeeNode);
				if(attributeNodePrevious){
						// <previous> tag found
						attributeOldValue = attributeNodePrevious.getTextContent();
						int lenValue = attributeValue.length() - attributeOldValue.length();
						int endPos = lenValue;
						if (endPos >= 0 ) {
						    attributeValue = attributeValue.substring(0, endPos);
						}else{
						   messageBody = messageBody + ("Debug log: Employee Attribute "+ arrEmployeeChangeAttributesSFEC[j] +" Changed Value:" + attributeValue ) + "\n"; 
						} 
				}else{
					attributeOldValue = "";
				}

					if (arrEmployeeCustomFieldsSFEC[j].contains("start_date") == true || arrEmployeeCustomFieldsSFEC[j].contains("end_date") == true) {
						Date dateValue; 
						if(attributeValue){
							dateValue = dateFormat.parse(attributeValue);
							attributeValue = dateGRCFormat.format(dateValue);
						}
					}

			    Node nodeCustomFieldsItem = xmlHelper.createNode("item", new String(), nodeCustomFields, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("Fieldname", arrEmployeeCustomFieldsSAPAC[j], nodeCustomFieldsItem, employeeHRTriggerReceiverRequest);
			    xmlHelper.createNode("Value", attributeValue, nodeCustomFieldsItem, employeeHRTriggerReceiverRequest);
			}

//			//Fortesting
//			if (j == 0){
//				break;
//			} 
		}

	}
	
	messageLog.addAttachmentAsString("Log Attachment", messageBody, " Log messages ");
	
 //set mapped target message as payload
	message.setBody(employeeHRTriggerReceiverRequest);

	
	// add log entry for performance measurement
	System.out.println("Performance measurement: After mapping script");
	
	return message;
}
