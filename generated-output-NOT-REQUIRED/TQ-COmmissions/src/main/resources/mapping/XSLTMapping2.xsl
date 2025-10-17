<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs">
  <xsl:output method="xml" encoding="UTF-8" indent="yes" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <xsl:variable name="var1_initial" select="."/>
    <root>
 <xsl:for-each select="Root/element/beans">
        <xsl:variable name="var2_cur" select="."/>
         <xsl:for-each select="territory/territoryQuotas">
            <xsl:variable name="var3_cur" select="."/>
               <territoryQuotas>
                <territoryQuotaSeq><xsl:value-of select="territoryQuotaSeq"/></territoryQuotaSeq>
                <linenumber></linenumber>
                <sublinenumber></sublinenumber>
                <OrderIDSeq></OrderIDSeq>
                <targetTypeId><xsl:value-of select="targetType/targetTypeId"/></targetTypeId>
                <quotaValue><xsl:value-of select="finalQuotaValue/value"/></quotaValue>
                <unitType><xsl:value-of select="finalQuotaValue/unitType/name"/></unitType>
                <caseStatus><xsl:value-of select="caseStatus"/></caseStatus>
               <territorySeq><xsl:value-of select="territory/territorySeq"/></territorySeq>  
               <territoryname><xsl:value-of select="territory/name"/></territoryname>
               <isExplicit><xsl:value-of select="ancestor::territory/isExplicit"/></isExplicit>
               <overlaytype><xsl:value-of select="ancestor::territory/territoryProgramOverlay/overlayType/name"/></overlaytype>
               <territoryStartDate><xsl:value-of select="ancestor::territory/effectiveStartDate"/></territoryStartDate>
               <territoryEndDate><xsl:value-of select="ancestor::territory/effectiveEndDate"/></territoryEndDate>
               
              <territoryProgramSeq><xsl:value-of select="territory/territoryProgram/territoryProgramSeq"/></territoryProgramSeq>
              <territoryProgramname><xsl:value-of select="territory/territoryProgram/name"/></territoryProgramname>
              <territoryProgramStartDate><xsl:value-of select="ancestor::territory/territoryProgram/effectiveStartDate"/></territoryProgramStartDate>
              <territoryProgramEndDate><xsl:value-of select="ancestor::territory/territoryProgram/effectiveEndDate"/></territoryProgramEndDate> 
              <periodname><xsl:value-of select="ancestor::territory/territoryProgram/period/name"/></periodname>
              <geographyHierarchyname><xsl:value-of select="ancestor::territory/territoryProgram/geographyHierarchy/name"/></geographyHierarchyname>
              <quotaCellPeriodType><xsl:value-of select="ancestor::territory/territoryProgram/quotaCellPeriodType/name"/></quotaCellPeriodType>
              <quotaSettingMethodology><xsl:value-of select="ancestor::territory/territoryProgram/quotaSettingMethodology"/></quotaSettingMethodology>
               
              <positionname><xsl:value-of select="following::position/name"/></positionname>
              <positionbuname><xsl:value-of select="following::position/businessUnits/name"/></positionbuname>
              <positionbumask><xsl:value-of select="following::position/businessUnits/mask"/></positionbumask>
              <split><xsl:value-of select="following::split"/></split>
              <tPAlignmentType><xsl:value-of select="following::position/tPAlignmentType/name"/></tPAlignmentType>
             </territoryQuotas>
         </xsl:for-each>
      </xsl:for-each>
    </root>
  </xsl:template>
</xsl:stylesheet>