import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;

def Message processData(Message message) {
    // Validation: Validate customer data before processing
log.info('Validating: ' + message.getBody(String.class));
return message;
    return message
