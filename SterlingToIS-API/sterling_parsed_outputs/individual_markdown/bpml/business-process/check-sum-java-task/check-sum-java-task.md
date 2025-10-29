# JavaTaskCheckSum

**Type**: sterling.process
**File**: check-sum-java-task.bpml

## Description

Sterling B2B Business Process: JavaTaskCheckSum

## Operations

### 1. JavaTaskSample
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: 
import com.sterlingcommerce.woodstock.workflow.Document;
import com.sterlingcommerce.woodstock.workflow.WFCBase;
import java.io.InputStream;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import org.apache.commons.codec.digest.DigestUtils;

String digest = null;
Document document = new Document();
Document srcDoc = wfc.getPrimaryDocument();
InputStream is = srcDoc.getInputStream();

try {
  digest = DigestUtils.md5Hex(is);
  wfc.setBasicStatus(WFCBase.SUCCESS);
  wfc.addWFContent("CheckSum", digest.toString());
} catch (Exception ex) {
  wfc.setBasicStatus(WFCBase.ERROR);
  wfc.addWFContent("CheckSumError", ex.getMessage());
}
return "000";
				
  - `.`: {'from': '*'}

