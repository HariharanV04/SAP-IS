import com.sap.gateway.ip.core.customdev.util.Message;
def Message processData(Message message) {
    //Body 
     //def body = message.getBody();
     def map = message.getProperties();
     def offset = map.get("offset");
     def terposcount = map.get("territoryposcount");
     def size = Integer.valueOf(map.get("size"));
     offset = offset+size;
     message.setProperty("offset",offset);
     
     if (offset.toInteger() >= terposcount.toInteger())
     {
         message.setProperty("exitTerritoryLoop","true");
     }
     else
     {
         message.setProperty("exitTerritoryLoop","false");
     }

     return message;
}
