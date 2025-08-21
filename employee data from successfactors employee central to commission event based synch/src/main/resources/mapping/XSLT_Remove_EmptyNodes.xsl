<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="node()">
        <xsl:if test="normalize-space(string(.)) != ''
                        or count(@*[normalize-space(string(.)) != '']) > 0
                        or count(descendant::*[normalize-space(string(.)) != '']) > 0
                        or count(descendant::*/@*[normalize-space(string(.)) != '']) > 0">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
        </xsl:if>
    </xsl:template>

    <xsl:template match="@*">
        <xsl:if test="normalize-space(string(.)) != ''">
            <xsl:copy>
                <xsl:apply-templates select="@*" />
            </xsl:copy>
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="etag" />
     <xsl:template match="createdBy" />
</xsl:stylesheet>