import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
import java.nio.charset.StandardCharsets;

def Message processData(Message message) {
		
	def payload = message.getBody(java.lang.String) as String;
	
	String charset = "utf-8";
    byte[] BOM = [0xEF,0xBB,0xBF];
    String s2 = new String(BOM, charset) + payload;
    
    message.setBody(s2); 

	return message;
}