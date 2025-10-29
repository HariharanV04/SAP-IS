# Demo_BP_RenameRegexJavaTask

**Type**: sterling.process
**File**: demo-rename-regex-java-task.bpml

## Description

Sterling B2B Business Process: Demo_BP_RenameRegexJavaTask

## Operations

### 1. RegexMapTest
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: 
  import java.util.regex.Matcher;
  import java.util.regex.Pattern;

	String fileName = (String)wfc.getWFContent("fileName");
	String matchPattern = (String)wfc.getWFContent("matchPattern");
	String replacePattern = (String)wfc.getWFContent("replacePattern");

  Pattern p1 = Pattern.compile(matchPattern);
  Matcher m1 = p1.matcher(fileName);

  if (m1.find( )) {
    String output = m1.replaceFirst(replacePattern);
    wfc.addWFContent("resultFilename", output);
  } else {
    wfc.addWFContent("resultFilename", fileName);
    wfc.addWFContent("nomatch", "true");
  }

	return "OK";
  - `.`: {'from': '*'}

