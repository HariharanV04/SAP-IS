import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.XmlUtil;
def Message processData(Message message) {   

    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    def mesgproperties=message.getProperties();
    
    def orderseq = mesgproperties.get("tqpreferencevalue") as String;
    
    def terquotadata=root.territoryQuotas;
    def tqProgramstartdate=terquotadata.territoryProgramStartDate.text();
    println terquotadata.size();
    def tqprgstartdate=Date.parse('yyyy-MM-dd',tqProgramstartdate.substring(0,10))
    String newlinenumber = tqprgstartdate.format('yyyyMMdd')

    //Properties
    def properties = message.getProperties();
    def count = properties.get("vcount");
    def cnt=count.toInteger();
    //count = 1;

    for (int i=0; i<terquotadata.size() ; i++)
   {
     root.territoryQuotas[i].linenumber.each { row ->
                row.appendNode("linenumber", newlinenumber)
     }
     root.territoryQuotas[i].sublinenumber.each { row ->
                row.appendNode("sublinenumber", cnt)
     }
     root.territoryQuotas[i].OrderIDSeq.each { row ->
                row.appendNode("OrderIDSeq", orderseq)
                }
     cnt++;
                
   }
    message.setProperty("vcount", cnt);
    message.setBody(XmlUtil.serialize(root));
    return message;
}
