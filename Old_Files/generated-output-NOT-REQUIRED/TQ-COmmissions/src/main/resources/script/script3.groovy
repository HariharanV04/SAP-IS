/* Refer the link below to learn more about the use cases of script.
https://help.sap.com/viewer/368c481cd6954bdfa5d0435479fd4eaf/Cloud/en-US/148851bf8192412cba1f9d2c17f4bd25.html

If you want to know more about the SCRIPT APIs, refer the link below
https://help.sap.com/doc/a56f52e1a58e4e2bac7f7adbf45b2e26/Cloud/en-US/index.html */
import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.*;

def Message processData(Message message) {
 //Body 
def body = message.getBody(java.lang.String) as String;
def root = new XmlParser().parseText(body);
def i=0;
def errors="";
def finalmessage='"';
def allmessage=[];
root.'**'.findAll { it.name() == 'TargetType'}.each { a ->allmessage << a.text()};
int len = allmessage.size();
//println len
while(i<len)
{
//errors=errors+","+'"'+allmessage[i=0,i=1,i=2]+'"';
errors=errors+","+allmessage[i=i]
//errors=errors+","+"'"+allmessage[i=i]+"'"
i++;
}
//println errors
errors=errors.substring(1);
finalmessage=errors
message.setProperty("TargetTypeList", finalmessage);
//message.setBody(finalmessage);
return message;
}
