%dw 2.0
output application/json
---
{
  "errorCode": "405",
  "errorMessage": error.description splitBy "\n",
  "transactionId": correlationId,
  "timeStamp": now()
}