import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def Message processData(Message message) {
    def body = message.getBody(java.lang.String) as String
    def jsonParser = new JsonSlurper()
    def jsonObject = jsonParser.parseText(body)
    def isCloudDeployment = message.getProperties().get("isCloudDeployment")
    if(isCloudDeployment && isCloudDeployment == "true"){
        def beanArray = jsonObject.element.collect { it.bean }
        message.setBody(JsonOutput.toJson(beanArray))
    } else {
        message.setBody(JsonOutput.toJson(jsonObject["element"]))
    }
    return message;
}