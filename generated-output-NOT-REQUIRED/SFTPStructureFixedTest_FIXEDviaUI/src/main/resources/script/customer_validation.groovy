import com.sap.gateway.ip.core.customdev.util.Message;

def Message validateCustomerData(Message message) {
    def body = message.getBody(String.class);
    def messageLog = messageLogFactory.getMessageLog(message);
    if (messageLog != null) {
        messageLog.setStringProperty('Validation', 'Customer Data Validation');
        messageLog.addAttachmentAsString('Customer Payload', body, 'text/plain');
    }
    if (body && body.contains('customer_id')) {
        message.setHeader('Validation-Status', 'PASSED');
        message.setHeader('Validated-By', 'validateCustomerData');
    } else {
        message.setHeader('Validation-Status', 'FAILED');
        message.setHeader('Error', 'Missing customer_id in payload');
    }
    return message;
}