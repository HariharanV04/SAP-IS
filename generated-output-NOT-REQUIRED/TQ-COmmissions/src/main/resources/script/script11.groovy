import com.sap.gateway.ip.core.customdev.util.Message;

import com.sap.it.api.ITApiFactory;
import com.sap.it.api.mapping.ValueMappingApi;
import groovy.xml.XmlUtil;

def Message processData(Message message) {   
    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    //def properties = message.getProperties();

    def tqprogramdata=root.element;
    def Existsinvaluemap =1;
    println tqprogramdata.size();

    def a = ITApiFactory.getApi(ValueMappingApi.class, null);

//format sourceAgency, sourceIdentifier, sourceValue, targetAgency, targetIdentifier
    //def map = message.getHeaders();
    def srcAgency = "SrcAgency";  //map.get("SrcAgency").toString();
    def trgAgency = "TrgAgency";  //map.get("TrgAgency").toString();
    def srcIdentifier = "targetTypeId";  //map.get("SrcIdentifier").toString();
    def trgidentifier = "EventType";    //map.get("TrgIdentifier").toString();
    //def sourceValue = "Orders";   //map.get("Key");
    //def mappedValue = a.getMappedValue(srcAgency, srcIdentifier, sourceValue, trgAgency, trgidentifier);
    
    for (int i=0; i<tqprogramdata.size() ; i++)
       {
           //def tqprogramdata=root.element;
           def targetid= root.element[i].targetTypeId.text();
           
           def sourceValue = targetid;   //map.get("Key");
           def mappedValue = a.getMappedValue(srcAgency, srcIdentifier, sourceValue, trgAgency, trgidentifier);
    
           if (mappedValue == null)
           {
               root.element[i].valuemapId.each { row ->
           row.appendNode("valuemapId", targetid)
              }
           }
           else
           {
             root.element[i].valuemapId.each { row ->
           row.appendNode("valuemapId", mappedValue)
              }
             root.element[i].Existsinvaluemap.each { row ->
           row.appendNode("Existsinvaluemap", Existsinvaluemap)
              }
           }
           
       }
    

    message.setBody(XmlUtil.serialize(root));
    return message;
}
