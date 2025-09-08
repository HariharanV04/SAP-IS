import com.sap.gateway.ip.core.customdev.util.Message;
def Message processData(Message message) {
    //Body 
       //def body = message.getBody(java.lang.String)as String;
       def messageHeaders = message.getHeaders();
       
       String ProcessExceptionMessage  = messageHeaders.get('ExceptionMessage');
    
       throw new Exception(ProcessExceptionMessage);

       //return message;
}
