// Encrypt CSV file using PGP encryption
import java.security.Security
import org.bouncycastle.jce.provider.BouncyCastleProvider
import org.bouncycastle.openpgp.*
import org.bouncycastle.openpgp.operator.jcajce.*

// Add BouncyCastle provider
Security.addProvider(new BouncyCastleProvider())

def csvContent = message.getBody(String.class)
def fileName = message.getProperty('FILE_NAME')
def publicKeyString = message.getProperty('PGP_PUBLIC_KEY')

if (!csvContent || !publicKeyString) {
    throw new Exception('Missing CSV content or PGP public key')
}

try {
    // Load public key
    def publicKeyStream = new ByteArrayInputStream(publicKeyString.bytes)
    def publicKeyRing = new PGPPublicKeyRingCollection(PGPUtil.getDecoderStream(publicKeyStream))
    def publicKey = publicKeyRing.getPublicKey()
    
    if (publicKey == null) {
        throw new Exception('Could not find public key for encryption')
    }
    
    // Encrypt the content
    def outputStream = new ByteArrayOutputStream()
    def encryptedDataGenerator = new PGPEncryptedDataGenerator(
        new JcePGPDataEncryptorBuilder(PGPEncryptedData.AES_256)
            .setWithIntegrityPacket(true)
            .setSecureRandom(new SecureRandom())
            .setProvider('BC')
    )
    
    encryptedDataGenerator.addMethod(new JcePublicKeyKeyEncryptionMethodGenerator(publicKey).setProvider('BC'))
    
    def encryptedOut = encryptedDataGenerator.open(outputStream, new byte[1024])
    
    def compressedDataGenerator = new PGPCompressedDataGenerator(PGPCompressedData.ZIP)
    def compressedOut = compressedDataGenerator.open(encryptedOut)
    
    def literalDataGenerator = new PGPLiteralDataGenerator()
    def literalOut = literalDataGenerator.open(compressedOut, PGPLiteralData.BINARY, fileName, new Date(), new byte[1024])
    
    literalOut.write(csvContent.bytes)
    literalOut.close()
    compressedOut.close()
    encryptedOut.close()
    
    def encryptedContent = outputStream.toByteArray()
    
    // Set encrypted content and update filename
    message.setBody(encryptedContent)
    message.setProperty('ENCRYPTED_FILE_NAME', fileName + '.pgp')
    message.setProperty('ENCRYPTION_STATUS', 'SUCCESS')
    
} catch (Exception e) {
    message.setProperty('ENCRYPTION_STATUS', 'FAILED')
    message.setProperty('ENCRYPTION_ERROR', e.getMessage())
    throw new Exception('PGP encryption failed: ' + e.getMessage())
}

return message