<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:multimap="http://sap.com/xi/XI/SplitAndMerge" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>

	<xsl:template match="node()|@*">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
		</xsl:copy>
	</xsl:template>

	<!-- In case there is more than one PerPersonal Record, keep the latest one -->
	<xsl:template match = "personalInfoNav">
	    <xsl:variable name="sortedPerPersonal" as="element(PerPersonal)*">
		    <xsl:apply-templates select="PerPersonal">
			    <xsl:sort select="endDate" order="descending"/>
			</xsl:apply-templates>
		</xsl:variable>
		<personalInfoNav>
    	    <xsl:copy-of select="$sortedPerPersonal[1]"/>
		</personalInfoNav>
	</xsl:template>
	
	<!-- In case there is more than one EmpJob Record, keep the latest one -->
	<xsl:template match = "jobInfoNav">
	    <xsl:variable name="sortedEmpJob" as="element(EmpJob)*">
		    <xsl:apply-templates select="EmpJob">
			    <xsl:sort select="endDate" order="descending"/>
			</xsl:apply-templates>
		</xsl:variable>
		<jobInfoNav>
			<xsl:choose>
				<xsl:when test="count($sortedEmpJob[eventNav/PicklistOption/externalCode = 'H' or eventNav/PicklistOption/externalCode = 'R' or eventNav/PicklistOption/externalCode = 'GA'])">
					<xsl:copy-of select="$sortedEmpJob[eventNav/PicklistOption/externalCode = 'H' or eventNav/PicklistOption/externalCode = 'R' or eventNav/PicklistOption/externalCode = 'GA']"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:copy-of select="$sortedEmpJob[1]"/>
				</xsl:otherwise>
			</xsl:choose> 
		</jobInfoNav>
	</xsl:template>

</xsl:stylesheet>