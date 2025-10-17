<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:multimap="http://sap.com/xi/XI/SplitAndMerge" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>
	
	<xsl:template match="node()|@*">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
		</xsl:copy>
	</xsl:template>
	
	<!-- Get list of relevant countries for Concur -->
	<xsl:param name="relevantCompanyCodes"/>
	
	<!-- Get interface last execution time -->
	<xsl:param name="lastExecutionTime"/>
	
	<!-- Process Employees that have more than one employment record - either because he/she is on global assignment or has been transfered for another country -->
	<xsl:template match="PerPerson/PerPerson/employmentNav[count(EmpEmployment) > 1]">
		<xsl:choose>
		    <!-- Looking for an active employment on a relevant company for Concur --> 
			<xsl:when test="EmpEmployment[jobInfoNav/EmpJob/emplStatusNav/PicklistOption/externalCode = 'A' and contains($relevantCompanyCodes, jobInfoNav/EmpJob/company)]">
				<employmentNav>
					<xsl:copy-of select="EmpEmployment[jobInfoNav/EmpJob/emplStatusNav/PicklistOption/externalCode = 'A' and contains($relevantCompanyCodes, jobInfoNav/EmpJob/company)][1]"/>
				</employmentNav>
			</xsl:when>
			<!-- If there's no active employment, then look for a Dormant employment - in this case the employee is on Global Assignment on a company that is not relevant for Concur -->
			<xsl:when test="EmpEmployment[jobInfoNav/EmpJob/emplStatusNav/PicklistOption/externalCode = 'D' and contains($relevantCompanyCodes, jobInfoNav/EmpJob/company) and (translate(jobInfoNav/EmpJob/createdDateTime, '-:.','') &gt; translate($lastExecutionTime, '-:.',''))]">
				<employmentNav>
					<xsl:copy-of select="EmpEmployment[jobInfoNav/EmpJob/emplStatusNav/PicklistOption/externalCode = 'D' and contains($relevantCompanyCodes, jobInfoNav/EmpJob/company)][1]"/>
				</employmentNav>
			</xsl:when>
			<!-- If there's no active or dormant employment, then look for the latest terminated employment that is relevant for Concur -->
			<xsl:when test="EmpEmployment[jobInfoNav/EmpJob/emplStatusNav/PicklistOption/externalCode = 'T' and contains($relevantCompanyCodes, jobInfoNav/EmpJob/company) and (translate(jobInfoNav/EmpJob/createdDateTime, '-:.','') &gt; translate($lastExecutionTime, '-:.',''))]">
				<xsl:variable name="sortedEmployments">
                  <xsl:perform-sort select="EmpEmployment">
                     <xsl:sort select="endDate" order="descending"/>
                  </xsl:perform-sort>
                </xsl:variable>
                <employmentNav>
                    <xsl:copy-of select="$sortedEmployments/EmpEmployment[1]"/>
                </employmentNav>
			</xsl:when>
			<xsl:otherwise/>
		</xsl:choose>
	</xsl:template>
	
</xsl:stylesheet>