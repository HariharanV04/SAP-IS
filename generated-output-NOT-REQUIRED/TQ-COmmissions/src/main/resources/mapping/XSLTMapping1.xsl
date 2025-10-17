<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs">
  <xsl:output method="xml" encoding="UTF-8" indent="yes" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <xsl:variable name="var1_initial" select="."/>
    <root>
 <xsl:for-each select="Root/element/beans">
        <xsl:variable name="var2_cur" select="."/>
        <element>
        <territorySeq><xsl:value-of select="territory/territorySeq"/></territorySeq>  
        <territoryname><xsl:value-of select="territory/name"/></territoryname>
        <territoryStartDate><xsl:value-of select="territory/effectiveStartDate"/></territoryStartDate>
        <territoryEndDate><xsl:value-of select="territory/effectiveEndDate"/></territoryEndDate>
        <territoryProgramSeq><xsl:value-of select="territory/territoryProgram/territoryProgramSeq"/></territoryProgramSeq>
        <territoryProgramname><xsl:value-of select="territory/territoryProgram/name"/></territoryProgramname>
        <territoryProgramStartDate><xsl:value-of select="territory/territoryProgram/effectiveStartDate"/></territoryProgramStartDate>
       <territoryProgramEndDate><xsl:value-of select="territory/territoryProgram/effectiveEndDate"/></territoryProgramEndDate> 
       <isExplicit><xsl:value-of select="territory/isExplicit"/></isExplicit>
         <xsl:for-each select="territory/territoryQuotas">
            <xsl:variable name="var3_cur" select="."/>
               <territoryQuotas>'
                <territoryQuotaSeq><xsl:value-of select="territoryQuotaSeq"/></territoryQuotaSeq>
                <targetTypeId><xsl:value-of select="targetType/targetTypeId"/></targetTypeId>
                <quotaValue><xsl:value-of select="quotaValue/value"/></quotaValue>
                <unitType><xsl:value-of select="quotaValue/unitType/name"/></unitType>
               </territoryQuotas>
         </xsl:for-each>
         <positionname><xsl:value-of select="position/name"/></positionname>
         <positionbuname><xsl:value-of select="position/businessUnits/name"/></positionbuname>
         <positionbumask><xsl:value-of select="position/businessUnits/mask"/></positionbumask>
         <split><xsl:value-of select="split"/></split>
        </element>
      </xsl:for-each>
    </root>
  </xsl:template>
</xsl:stylesheet>