import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.XmlUtil;

def Message processData(Message message) {   
    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    def properties = message.getProperties();

    def extXmltevent = properties.get("p_eventtypes") as String;
    def extXmlteventDoc = new XmlParser().parseText(extXmltevent);

    def tqtargetdata=root.element;
    println tqtargetdata.size();
    def indicator=1

    def eventdata=extXmlteventDoc.eventTypes;
    println eventdata.size();

   for (int i=0; i<tqtargetdata.size() ; i++)
   {
       def tqtargetdata2=root.element[i];
       def targetID=tqtargetdata2.valuemapId[0].valuemapId.text();
       println  targetID

       for (int k=0; k<eventdata.size() ; k++)
       {
         def commeventdata=extXmlteventDoc.eventTypes[k];
       def eventtype=commeventdata.eventTypeId.text();
       println eventtype

       if (targetID == eventtype)
       {
          root.element[i].ExistsinCommission.each { row ->
                row.appendNode("ExistsinCommission", indicator)
                }
 
       }
       }
       
   }

    message.setBody(XmlUtil.serialize(root));
    return message;
}
