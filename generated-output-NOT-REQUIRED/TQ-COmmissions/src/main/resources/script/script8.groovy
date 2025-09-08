import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.*;
def Message processData(Message message) {   
    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    //def properties = message.getProperties();

    def tqprogramdata=root.Root;
    println tqprogramdata.size();
    def tqpreferencevalue = tqprogramdata.value.text();
    def initseq = 1;

    if ( tqpreferencevalue == '')
    {
      message.setProperty("tqpreferencevalue", initseq);
    }
    else
    {
        //tqpreferencevalue = tqprogramdata.value.text();
        tqpreferencevalue = java.lang.Integer.parseInt(tqpreferencevalue)
        tqpreferencevalue = tqpreferencevalue + 1;
        message.setProperty("tqpreferencevalue", tqpreferencevalue);
    }

    message.setBody(XmlUtil.serialize(root));
    return message;
}