<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:multimap="http://sap.com/xi/XI/SplitAndMerge" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>

	<xsl:template match="node()|@*">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
		</xsl:copy>
	</xsl:template>
	
	<!-- Remove Employees that don't have an email address of type Business or any job info records -->
	<xsl:template match="PerPerson/PerPerson[count(emailNav/PerEmail/emailTypeNav/PicklistOption[externalCode = 'B']) = 0 or count(employmentNav/EmpEmployment/jobInfoNav/EmpJob) = 0]"/>

</xsl:stylesheet>