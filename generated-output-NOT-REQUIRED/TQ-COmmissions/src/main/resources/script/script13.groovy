import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.XmlUtil;

def Message processData(Message message) {   
    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    //def properties = message.getProperties();

    //def extXmltevent = properties.get("p_eventtypes") as String;
    //def extXmlteventDoc = new XmlParser().parseText(extXmltevent);

    def tqtargetdata=root.element;
    println tqtargetdata.size();
    message.setProperty("p_eventcnt", tqtargetdata.size());

    message.setBody(XmlUtil.serialize(root));
    return message;
}
