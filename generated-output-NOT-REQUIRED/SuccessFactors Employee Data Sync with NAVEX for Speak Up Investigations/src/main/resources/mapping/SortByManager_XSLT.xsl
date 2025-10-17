<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:multimap="http://sap.com/xi/XI/SplitAndMerge" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>
    <!-- This script sorts the Staff file by GlobalID (aka employeeID) -->
	<xsl:template match="@* | node()">
		<xsl:copy>
			<xsl:apply-templates select="@* | node()"/>
		</xsl:copy>
	</xsl:template>
	
    <xsl:template match="root">
		<xsl:copy>
			<xsl:apply-templates select="Record">
				<xsl:sort select="ExpenseCashAdvanceApprover" data-type="text" order="descending"/>
			</xsl:apply-templates>
		</xsl:copy>
	</xsl:template>
	
	

</xsl:stylesheet>