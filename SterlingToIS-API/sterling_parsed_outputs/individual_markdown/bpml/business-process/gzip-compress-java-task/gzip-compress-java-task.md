# JavaTaskGzipCompress

**Type**: sterling.process
**File**: gzip-compress-java-task.bpml

## Description

Sterling B2B Business Process: JavaTaskGzipCompress

## Operations

### 1. GzipCompress
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: 
import com.sterlingcommerce.woodstock.workflow.Document;
import java.io.*;
import java.util.zip.GZIPOutputStream;

try {
    String fileName = "myfilename.gz";

    Document doc = wfc.getPrimaryDocument();
    String bodyNameInput = doc.getBodyName();
    wfc.addWFContent("DocumentNameInput",bodyNameInput); 

    // Open the file for reading
    InputStream is = doc.getBodyInputStream();
    BufferedInputStream bis = new BufferedInputStream(is);


    // Open the gzip file for writing
    Document newDoc = new Document();
    OutputStream os = newDoc.getOutputStream();

    //FileOutputStream fos = new FileOutputStream(fileName + ".gz");
    //GZIPOutputStream gzos = new GZIPOutputStream(fos, 9);
    GZIPOutputStream gzos = new GZIPOutputStream(os, 9);
    BufferedOutputStream bos = new BufferedOutputStream(gzos);

    // Write the compressed data
    byte[] buffer = new byte[1024];
    int bytesRead;
    while ((bytesRead = bis.read(buffer)) != -1) {
    bos.write(buffer, 0, bytesRead);
    }

    // Close the streams
    bos.close();
    bis.close();

    //String newContent = "This is the content of the new Primary Document";
    //Document newDoc = new Document();
    //OutputStream os = newDoc.getOutputStream();
    //os.write(newContent.getBytes());
    os.flush();
    os.close();
    wfc.putPrimaryDocument(newDoc);
    wfc.addWFContent("DocumentNameOutput",fileName); 
} catch (IOException e) {
    log.log("Error: " + e.getMessage());
}
return "OK";
    
  - `.`: {'from': '*'}

