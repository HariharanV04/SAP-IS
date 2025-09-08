import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.XmlUtil;

def Message processData(Message message) {   
    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    def properties = message.getProperties();

    def extXmltevent = properties.get("p_valuemapEventtype") as String;
    println "test" + extXmltevent
    def extXmlteventDoc = new XmlParser().parseText(extXmltevent);

    def tqtargetdata=root.territoryQuotas;
    println tqtargetdata.size();
    //message.setProperty("p_eventcnt", tqtargetdata.size());
   
    def tqeventdata=extXmlteventDoc.element
    println tqeventdata.size();

    if (tqeventdata.size() > 0)
    {
    for (def it : root.children())
     {
        for (int i=0;i<tqeventdata.size();i++)
        {
         def tqeventdata2=extXmlteventDoc.element[i];
         def targetTypeId=tqeventdata2.targetTypeId.text();
         def valuemapId=tqeventdata2.valuemapId.valuemapId.text();
        
        if(it.targetTypeId.text().equals(targetTypeId) ) {
        it.targetTypeId[0].value = valuemapId;

        }
    
       }
     }
    }

    message.setBody(XmlUtil.serialize(root));
    return message;
}
