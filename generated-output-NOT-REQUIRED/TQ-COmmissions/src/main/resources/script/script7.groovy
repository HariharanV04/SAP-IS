import com.sap.gateway.ip.core.customdev.util.Message;
import groovy.xml.XmlUtil;

def Message processData(Message message) {   
    def body = message.getBody(java.lang.String) as String;
    def root = new XmlParser().parseText(body);
    //def properties = message.getProperties();

    def tqprogramdata=root.beans;
    println tqprogramdata.size();

    def tqProgramname=tqprogramdata.name.text();
    def tqProgramstartdate=tqprogramdata.effectiveStartDate.text();
    //def tqProgramenddate=tqprogramdata.effectiveEndDate.text();

    // Period details
    //def Periodname=tqprogramdata.period.name.text();
    def Periodseq=tqprogramdata.period.periodSeq.text();
    //def calendarname=tqprogramdata.period.calendar.name.text();
    def calendarseq=tqprogramdata.period.calendar.calendarSeq.text();
    //def quotacellperiodtype=tqprogramdata.quotaCellPeriodType.name.text();
    def quotacellperiodtypeseq=tqprogramdata.quotaCellPeriodType.periodTypeSeq.text();

    tqProgramstartdate=tqprogramdata.effectiveStartDate.text();
    def tqprgstartdate=Date.parse('yyyy-MM-dd',tqProgramstartdate.substring(0,10))
    String tqprgstartdateformat = tqprgstartdate.format('yyyyMMdd')
    
 /*   println Periodname
    println Periodseq
    println calendarname
    println calendarseq
    println quotacellperiodtype
    println quotacellperiodtypeseq
    println newlinenumber
*/
   message.setProperty("tqpreferencekey", tqProgramname+"_"+tqprgstartdateformat);
   message.setProperty("quotacellperiodtypeseq", quotacellperiodtypeseq);
   message.setProperty("calendarseq", calendarseq);
   message.setProperty("Periodseq", Periodseq);
   //message.setProperty("quotacellperiodtypeseq", quotacellperiodtypeseq);

    message.setBody(XmlUtil.serialize(root));
    return message;
}
