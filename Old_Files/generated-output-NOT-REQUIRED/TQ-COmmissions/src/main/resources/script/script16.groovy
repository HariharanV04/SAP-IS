import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.json.JsonSlurper

def Message processData(Message message) {
    def body = message.getBody(java.lang.String) as String
    def jsonParser = new JsonSlurper()
    def jsonObject = jsonParser.parseText(body)
    def existingSalesOrderListSize = jsonObject != null && jsonObject.salesOrders != null ? jsonObject.salesOrders.size() : 0;
    message.setProperty("salesOrderListSize", existingSalesOrderListSize);
    return message;
}
