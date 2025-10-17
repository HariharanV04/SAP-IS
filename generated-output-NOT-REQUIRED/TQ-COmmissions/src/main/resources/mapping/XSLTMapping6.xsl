<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:key name="kTripByContent" match="bean"
             use="orderId"/>
<xsl:template match="node()|@*">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*"/>
        </xsl:copy>
    </xsl:template>
<xsl:template match="/root/element/bean[generate-id() != generate-id(key('kTripByContent',orderId)[1])]"/>    
</xsl:stylesheet>