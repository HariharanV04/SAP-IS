import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
import groovy.xml.MarkupBuilder;

def Message processData(Message message) {
    
    // Access message body and properties
    Reader reader = message.getBody(Reader);
    Map properties = message.getProperties();

    // Define XML parser and builder
    def response = new XmlSlurper().parse(reader);//response from SF ODATA API
    def writer = new StringWriter();
    def builder = new MarkupBuilder(writer);

    //Store employee data in structure
    def personList = response.PerPerson;
    def relevantCompanies = properties.get('relevantCompanyCodes').replace("'","").split(",")*.trim();

    def now = new Date();
    def df = "yyyy-MM-dd'T'HH:mm:ss.SSS";
    
    //Store last execution time
    def lastExecutionTime = new Date().parse(df, properties.get('lastExecutionTime'));
    
    def today = new Date().parse(df, properties.get('today'));

    builder.root {
        for (person in personList) {
            //Check if employee has a Global Assignment Record
            //def globalAssignment = person.employmentNav.EmpEmployment.find { elem -> elem.assignmentClass.toString().equals('GA') }
            // The employeeID of a manager should always be updated, independently of whether that manager has been moved to a company that is relevant for Concur
            def isManager = person.userAccountNav.UserAccount.user.User.teamMembersSize != '' ? person.userAccountNav.UserAccount.user.User.teamMembersSize.toInteger() > 0 : false;
            
            //Employee is back from Global Assignment
            if (person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('BGA') }) { 
                def bgaEmploymentJobInfoRecord = person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('BGA') };
                
                if (bgaEmploymentJobInfoRecord.size() == 0)
                    continue;
                    
                /*if (new Date().parse(df, bgaEmploymentJobInfoRecord.createdDateTime.toString()) < lastExecutionTime && new Date().parse(df, bgaEmploymentJobInfoRecord.createdDateTime.toString()) < lastExecutionTime)
                    continue;*/
                    
                def bgaCompany = bgaEmploymentJobInfoRecord.company.toString();
                if ((bgaCompany in relevantCompanies) || isManager) {
                    def bgaEmploymentRecord = person.employmentNav.EmpEmployment.find {elem -> elem.userId.toString() == bgaEmploymentJobInfoRecord.userId.toString()};
                    def egaEmploymentJobInfoRecord = person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('EGA') }//Look for previous employee ID in the record that contains End of Global Assignment
                    def egaEmploymentRecord = person.employmentNav.EmpEmployment.find {elem -> elem.userId.toString() == egaEmploymentJobInfoRecord.userId.toString()};
                    if (removeLeadingZeros(egaEmploymentRecord.assignmentIdExternal.toString()) != removeLeadingZeros(bgaEmploymentRecord.assignmentIdExternal.toString())) {
                        'Record' {
                            'TrxType' (320)
                            'PreviousEmployeeID' (removeLeadingZeros(egaEmploymentRecord.assignmentIdExternal.toString()))
                            'NewEmployeeID' (removeLeadingZeros(bgaEmploymentRecord.assignmentIdExternal.toString()))
                            'NewLoginID' ('')
                            'FutureUse1' ('')
                            'FutureUse2' ('')
                            'FutureUse3' ('')
                            'FutureUse4' ('')
                            'FutureUse5' ('')
                        }
                    }
                }
            }
            //If Global Assignment record is found, then process the record
            if (person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('GA') }) {
                def gaEmploymentJobInfoRecord = person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('GA') };
                
                if (gaEmploymentJobInfoRecord.size() == 0)
                    continue;
                    
                /*if (new Date().parse(df, gaEmploymentJobInfoRecord.createdDateTime.toString()) < lastExecutionTime && new Date().parse(df, gaEmploymentJobInfoRecord.createdDateTime.toString()) < lastExecutionTime)
                    continue;*/
                    
                def gaCompany = gaEmploymentJobInfoRecord.company.toString();
                if ((gaCompany in relevantCompanies) || isManager) {
                    def gaEmploymentRecord = person.employmentNav.EmpEmployment.find {elem -> elem.userId.toString() == gaEmploymentJobInfoRecord.userId.toString()};
                    def agaEmploymentJobInfoRecord = person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.emplStatusNav.PicklistOption.externalCode.toString().equals('D') }//Look for Dormant Employment
                    def agaEmploymentRecord = person.employmentNav.EmpEmployment.find {elem -> elem.userId.toString() == agaEmploymentJobInfoRecord.userId.toString()};
                    if (removeLeadingZeros(agaEmploymentRecord.assignmentIdExternal.toString()) != removeLeadingZeros(gaEmploymentRecord.assignmentIdExternal.toString())) {
                        'Record' {
                            'TrxType' (320)
                            'PreviousEmployeeID' (removeLeadingZeros(agaEmploymentRecord.assignmentIdExternal.toString()))
                            'NewEmployeeID' (removeLeadingZeros(gaEmploymentRecord.assignmentIdExternal.toString()))
                            'NewLoginID' ('')
                            'FutureUse1' ('')
                            'FutureUse2' ('')
                            'FutureUse3' ('')
                            'FutureUse4' ('')
                            'FutureUse5' ('')
                        }
                    }
                }
            }
            //If employee country transfer record is found, then process the record
            if (person.employmentNav.EmpEmployment.jobInfoNav.EmpJob.find { elem -> elem.eventReason.toString().equals('2013') }) { 
                def sortedEmploymentRecords = person.employmentNav.EmpEmployment.sort{ a,b -> new Date().parse(df, a.startDate.toString()) <=> new Date().parse(df, b.startDate.toString()) }; //Sort Job Info Record by startDate
                for (def i = 0; i < sortedEmploymentRecords.size(); i++) {
                    if (sortedEmploymentRecords[i] && sortedEmploymentRecords[i].jobInfoNav.EmpJob.find{elem -> elem.eventReason.toString().equals('2013') } && sortedEmploymentRecords[i + 1] && sortedEmploymentRecords[i + 1].jobInfoNav.EmpJob.find{elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('H') || elem.eventNav.PicklistOption.externalCode.toString().equals('R')}) { //if current record is Country Transfer and next record is not a termination - then we're looking at these two records
                    
                        /*def createdDateTime = new Date().parse(df, sortedEmploymentRecords[i].jobInfoNav.EmpJob.find{elem -> elem.eventReason.toString().equals('2013') }.createdDateTime.toString());
                        def nextCreatedDateTime = new Date().parse(df, sortedEmploymentRecords[i + 1].jobInfoNav.EmpJob.find{elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('H') || elem.eventNav.PicklistOption.externalCode.toString().equals('R')}.createdDateTime.toString());
                        
                        if (createdDateTime < lastExecutionTime && nextCreatedDateTime < lastExecutionTime)
                            continue;*/
                            
                        def nextRecordCompanyCode = sortedEmploymentRecords[i + 1].jobInfoNav.EmpJob.find{elem -> elem.eventNav.PicklistOption.externalCode.toString().equals('H') || elem.eventNav.PicklistOption.externalCode.toString().equals('R')}.company.toString();
                            
                        if ((nextRecordCompanyCode in relevantCompanies) || isManager) {
                            def previousEmployeeId = sortedEmploymentRecords[i].assignmentIdExternal.toString();
                            def currentEmployeeId = sortedEmploymentRecords[i + 1].assignmentIdExternal.toString();
                            if (removeLeadingZeros(previousEmployeeId) != removeLeadingZeros(currentEmployeeId)) {
                                'Record' {
                                    'TrxType' (320)
                                    'PreviousEmployeeID' (removeLeadingZeros(previousEmployeeId))
                                    'NewEmployeeID' (removeLeadingZeros(currentEmployeeId))
                                    'NewLoginID' ('')
                                    'FutureUse1' ('')
                                    'FutureUse2' ('')
                                    'FutureUse3' ('')
                                    'FutureUse4' ('')
                                    'FutureUse5' ('')
                                }
                            }
                        }
                        break;
                    }
                }
            }
        }
    }

    // Generate output
    message.setBody(writer.toString())
    
    return message;
}

def String removeLeadingZeros(String number){
	while(number.startsWith("0")) { 
        number = number.substring(1, number.length());
    }
    return number;
}
