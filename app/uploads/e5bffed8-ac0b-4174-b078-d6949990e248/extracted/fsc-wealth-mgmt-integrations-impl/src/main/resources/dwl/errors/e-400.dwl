%dw 2.0
output application/json
---
{
  "errorCode": "400",
  "errorMessage": (((error.description splitBy "\n") distinctBy $) orderBy $)[-1 to 0],
  "transactionId": correlationId,
  "timeStamp": now()
}