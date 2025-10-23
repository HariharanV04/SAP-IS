import com.sap.gateway.ip.core.customdev.util.Message;

def Message processData(Message message) {
        def body = message.getBody(java.lang.String) as String;
       message.setProperty("territoryposcount",body);
       message.setProperty("offset",1);
       return message;
}