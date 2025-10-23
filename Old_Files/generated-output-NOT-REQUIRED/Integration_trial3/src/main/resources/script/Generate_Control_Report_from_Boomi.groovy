import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;

def Message processMessage(Message message) {
    // Get the message body
    def body = message.getBody(String.class);

    // Log the message
    def messageLog = messageLogFactory.getMessageLog(message);
    if (messageLog != null) {
        messageLog.setStringProperty("Processing", "Processing in Generate_Control_Report_from_Boomi");
        messageLog.addAttachmentAsString("Payload", body, "text/plain");
    }

    // Add a header to indicate processing
    message.setHeader("Processed-By", "Generate_Control_Report_from_Boomi");

    return message;
}
