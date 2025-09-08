<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:param name="TargetTypeList" />
<xsl:variable name="tokenizedList" select="tokenize($TargetTypeList, ',')"/>
<xsl:output method="xml" encoding="UTF-8" indent="yes" />

<xsl:template match="@*|node()">
<xsl:copy>
<xsl:apply-templates select="@*|node()"/>
</xsl:copy>
</xsl:template>

<xsl:template match="/root/territoryQuotas[not(targetTypeId = $tokenizedList) or not(quotaValue) or normalize-space(quotaValue)='' or not(caseStatus) or normalize-space(caseStatus)='']" />

<xsl:template match="caseStatus"/>


</xsl:transform>
