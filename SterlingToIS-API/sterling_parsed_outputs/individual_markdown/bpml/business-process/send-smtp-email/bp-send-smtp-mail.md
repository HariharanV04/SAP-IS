# Demo_BP_test_smtp

**Type**: sterling.process
**File**: bp-send-smtp-mail.bpml

## Description

Sterling B2B Business Process: Demo_BP_test_smtp

## Operations

### 1. Send
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `xport-smtp-mailhost`: {'from': '//mailhost/text()'}
  - `xport-smtp-mailport`: 25
  - `xport-smtp-mailfrom`: a@company.com
  - `xport-smtp-mailto`: b@company.com
  - `xport-smtp-mailCC`: c@company.com
  - `xport-smtp-mailsubject`: {'from': '//MAIL_SUBJECT/text()'}

