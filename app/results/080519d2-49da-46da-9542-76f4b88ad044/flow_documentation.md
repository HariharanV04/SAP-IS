# API Overview
The Financial Services Cloud Wealth Management API provides comprehensive functionality for managing investment accounts, beneficiaries, standing orders, customer profiles, and specialized financial operations like ACATS (Automated Customer Account Transfer Service) and RMD (Required Minimum Distribution). This API enables financial institutions to handle wealth management operations through standardized RESTful endpoints.

- Base URL: `/fsc-wealth-management-api`

# Endpoints

## Investment Accounts

### POST /InvestmentAccounts/Initiate
- **Purpose**: Initiates the creation of beneficiaries for investment accounts
- **Request Body**: JSON containing investment account details and beneficiary information
- **Response**: 201 Created with the created beneficiaries information
- **Example Response**:
  ```json
  {
    "InvestmentAccounts": {
      "AccountIds": ["account123"],
      "Beneficiaries": {
        "Primary": [
          {
            "BeneficiaryId": "BFR-1234567",
            "BeneficiaryName": "John Doe",
            "BeneficiaryType": "Individual",
            "SharePercentage": "50"
          }
        ],
        "Contingent": [
          {
            "BeneficiaryId": "BFR-7654321",
            "BeneficiaryName": "Jane Doe",
            "BeneficiaryType": "Individual",
            "SharePercentage": "50"
          }
        ]
      }
    }
  }
  ```

### PATCH /InvestmentAccounts/Update
- **Purpose**: Updates existing beneficiaries for investment accounts
- **Request Body**: JSON containing investment account details and beneficiary information to update
- **Response**: 200 OK with the updated beneficiaries information

### DELETE /InvestmentAccounts/Delete
- **Purpose**: Deletes beneficiaries from investment accounts
- **Request Body**: JSON containing investment account and beneficiary IDs to delete
- **Response**: 200 OK with confirmation of deleted beneficiaries

### GET /InvestmentAccounts/{accountId}/Retrieve
- **Purpose**: Retrieves investment account details including beneficiaries
- **Path Parameters**: 
  - `accountId`: The ID of the investment account to retrieve
- **Response**: 200 OK with the investment account details and beneficiaries

## Payments

### POST /InvestmentAccounts/{accountId}/Payments/Initiate
- **Purpose**: Initiates standing orders for an investment account
- **Path Parameters**: 
  - `accountId`: The ID of the investment account
- **Request Body**: JSON containing payment order details
- **Response**: 201 Created with the created payment orders

### PATCH /InvestmentAccounts/{accountId}/Payments/Update
- **Purpose**: Updates or cancels existing standing orders
- **Path Parameters**: 
  - `accountId`: The ID of the investment account
- **Request Body**: JSON containing payment IDs to cancel
- **Response**: 200 OK with confirmation of canceled payment orders

### GET /InvestmentAccounts/{accountId}/Payments/Retrieve
- **Purpose**: Retrieves standing orders for an investment account
- **Path Parameters**: 
  - `accountId`: The ID of the investment account
- **Query Parameters**:
  - `paymentId` (optional): Filter by payment ID
  - `payeeName` (optional): Filter by payee name
  - `amount` (optional): Filter by payment amount
- **Response**: 200 OK with the matching payment orders

## Customer Profile

### PATCH /customers/{customerId}
- **Purpose**: Updates a customer's profile information
- **Path Parameters**: 
  - `customerId`: The ID of the customer
- **Request Body**: JSON containing profile information to update
- **Response**: 200 OK with the updated profile information

## Specialized Financial Operations

### POST /InvestmentAccounts/{accountId}/Acats
- **Purpose**: Initiates an ACATS transfer for an investment account
- **Path Parameters**: 
  - `accountId`: The ID of the investment account
- **Request Body**: JSON containing ACATS transfer details
- **Response**: 201 Created with the ACATS transfer information

### POST /InvestmentAccounts/{accountId}/RMD
- **Purpose**: Initiates a Required Minimum Distribution for an investment account
- **Path Parameters**: 
  - `accountId`: The ID of the investment account
- **Request Body**: JSON containing RMD details
- **Response**: 201 Created with the RMD information

# Current MuleSoft Flow Logic

## Main API Flow
The main flow (`fsc-wealth-management-api-main`) serves as the entry point for all API requests. It:
1. Receives HTTP requests through a listener component
2. Logs request details including requestId and flowRefId
3. Routes the request to the appropriate flow based on the endpoint
4. Handles errors through a dedicated error handler

## Investment Account Flows

### Add Beneficiaries Flow
**Trigger**: POST request to `/InvestmentAccounts/Initiate`
**Processing Steps**:
1. Routes to `add-beneficiaries-sub-flow`
2. Transforms the request payload using DataWeave
3. Generates unique BeneficiaryId values for each beneficiary
4. Returns the transformed response with status 201

### Update Beneficiaries Flow
**Trigger**: PATCH request to `/InvestmentAccounts/Update`
**Processing Steps**:
1. Routes to `update-beneficiaries-sub-flow`
2. Transforms the request payload using DataWeave
3. Generates BeneficiaryId values for new beneficiaries if needed
4. Returns the transformed response with status 200

### Delete Beneficiaries Flow
**Trigger**: DELETE request to `/InvestmentAccounts/Delete`
**Processing Steps**:
1. Routes to `delete-beneficiaries-sub-flow`
2. Transforms the request payload using DataWeave
3. Marks beneficiaries as "DELETED"
4. Returns the transformed response with status 200

### Retrieve Investment Account Details Flow
**Trigger**: GET request to `/InvestmentAccounts/{accountId}/Retrieve`
**Processing Steps**:
1. Routes to `retrieve-investment-account-details-sub-flow`
2. Sets account details in a variable
3. Transforms the data using DataWeave
4. Returns the account details and beneficiaries with status 200

## Payment Flows

### Add Standing Orders Flow
**Trigger**: POST request to `/InvestmentAccounts/{accountId}/Payments/Initiate`
**Processing Steps**:
1. Routes to `add-standing-orders-sub-flow`
2. Transforms the request payload using DataWeave
3. Generates unique PaymentId values for each payment
4. Returns the transformed response with status 201

### Cancel Standing Orders Flow
**Trigger**: PATCH request to `/InvestmentAccounts/{accountId}/Payments/Update`
**Processing Steps**:
1. Routes to `cancel-standing-orders-sub-flow`
2. Transforms the request payload using DataWeave
3. Marks payments as canceled with current timestamp
4. Returns the transformed response with status 200

### Retrieve Standing Orders Flow
**Trigger**: GET request to `/InvestmentAccounts/{accountId}/Payments/Retrieve`
**Processing Steps**:
1. Routes to `retrieve-standing-orders-sub-flow`
2. Logs query parameters
3. Sets standing orders in a variable
4. Filters orders based on query parameters (paymentId, payeeName, amount)
5. Returns the filtered payment orders with status 200

## Customer Profile Flow

### Update Customer Profile Flow
**Trigger**: PATCH request to `/customers/{customerId}`
**Processing Steps**:
1. Routes to `update-customers-profile-sub-flow`
2. Transforms the request payload using DataWeave
3. Returns the updated profile information with status 200

## Specialized Financial Operations Flows

### ACATS Flow
**Trigger**: POST request to `/InvestmentAccounts/{accountId}/Acats`
**Processing Steps**:
1. Routes to `prepare-acats-response-sub-flow`
2. Transforms the request payload using DataWeave
3. Returns the ACATS information with status 201

### RMD Flow
**Trigger**: POST request to `/InvestmentAccounts/{accountId}/RMD`
**Processing Steps**:
1. Routes to `prepare-rmd-response-sub-flow`
2. Transforms the request payload using DataWeave
3. Returns the RMD information with status 201

# DataWeave Transformations Explained

## Error Handling Transformations

### e-400.dwl
This transformation creates a standardized error response for 400 Bad Request errors.

```dataweave
%dw 2.0
output application/json
---
{
  "errorCode": "400",
  "errorMessage": (((error.description splitBy "\n") distinctBy $) orderBy $)[-1 to 0],
  "transactionId": correlationId,
  "timeStamp": now()
}
```

The transformation:
- Takes the error description and splits it by newlines
- Removes duplicates with `distinctBy $`
- Orders the remaining messages
- Takes the last message (most specific) using array slicing `[-1 to 0]`
- Adds a transaction ID and timestamp

## Beneficiary Management Transformations

### p-addBeneficiariesResponse.dwl
This transformation generates a response for adding beneficiaries, including unique IDs.

```dataweave
%dw 2.0
var bfr= "BFR-"
var bfrTrack= "BFRTRACK"
var bfrNumbers= '0123456789'
var bfrCharSetLength= sizeOf(bfrNumbers) - 1
var bfrNumbersLength= 7
output application/json skipNullOn = "everywhere"
---
{
	InvestmentAccounts: {
		AccountIds: payload.InvestmentAccounts.AccountIds map ( accountId , indexOfAccountId ) -> accountId,
		Beneficiaries: {
			Primary: payload.InvestmentAccounts.Beneficiaries.Primary map ($ ++ {
				BeneficiaryId: bfr ++ (1 to bfrNumbersLength map bfrNumbers[randomInt(bfrCharSetLength)] joinBy '')
			}),
			Contingent: payload.InvestmentAccounts.Beneficiaries.Contingent map ($ ++ {
				BeneficiaryId: bfr ++ (1 to bfrNumbersLength map bfrNumbers[randomInt(bfrCharSetLength)] joinBy '')
			})
		}
	}
}
```

The transformation:
- Defines variables for generating unique beneficiary IDs
- Maps through the account IDs from the input payload
- For each primary and contingent beneficiary, adds a unique BeneficiaryId
- The ID format is "BFR-" followed by 7 random digits
- Uses `skipNullOn = "everywhere"` to remove null values from the output

### p-updateBeneficiariesResponse.dwl
This transformation handles updating beneficiaries, including generating IDs for new beneficiaries.

```dataweave
%dw 2.0
var bfr= "BFR-"
var bfrTrack= "BFRTRACK"
var bfrNumbers= '0123456789'
var bfrCharSetLength= sizeOf(bfrNumbers) - 1
var bfrNumbersLength= 7

fun treeFilter(value: Any, predicate: (value:Any) -> Boolean) =
    value  match {
            case object is Object ->  do {
               object mapObject ((value, key, index) -> 
                    (key): treeFilter(value, predicate)
                )
                filterObject ((value, key, index) -> predicate(value))
            }
            case array is Array -> do {
                    array map ((item, index) -> treeFilter(item, predicate))
                                         filter ((item, index) -> predicate(item))                 
            }
            else -> $
    }
    
output application/json skipNullOn = "everywhere"
---
{
	InvestmentAccounts: {
		AccountIds: payload.InvestmentAccounts.AccountIds map ( accountId , indexOfAccountId ) -> accountId,
		Addresses: payload.InvestmentAccounts.Addresses,
		Beneficiaries: {
			Primary: payload.InvestmentAccounts.Beneficiaries.Primary map if ( $.BeneficiaryId == null ) ($ ++ {
				"BeneficiaryId": bfr ++ (1 to bfrNumbersLength map bfrNumbers[randomInt(bfrCharSetLength)] joinBy '')
			}) else $,
			Contingent: payload.InvestmentAccounts.Beneficiaries.Contingent map if ( $.BeneficiaryId == null ) ($ ++ {
				"BeneficiaryId": bfr ++ (1 to bfrNumbersLength map bfrNumbers[randomInt(bfrCharSetLength)] joinBy '')
			}) else $
		}
	}
} treeFilter ((value) -> 
    value match {
        case v is Array| Object | Null | "" -> !isEmpty(v)
        else -> true
    }
)
```

The transformation:
- Defines variables for generating unique beneficiary IDs
- Defines a recursive `treeFilter` function to remove empty values from the output
- Maps through account IDs from the input payload
- For each primary and contingent beneficiary, checks if BeneficiaryId is null
- If null, generates a new ID; otherwise, keeps the existing ID
- Applies the treeFilter function to remove empty values from the entire output

### p-deleteBeneficiariesResponse.dwl
This transformation creates a response for deleting beneficiaries.

```dataweave
%dw 2.0
output application/json skipNullOn = "everywhere"
---
{
	InvestmentAccounts: {
		AccountIds: payload.InvestmentAccounts.AccountIds map ( accountId , indexOfAccountId ) -> accountId, 
		Beneficiaries: payload.InvestmentAccounts.Beneficiaries map {
			BeneficiaryId: $.BeneficiaryId,
			Status: "DELETED"
		}
	}
}
```

The transformation:
- Maps through account IDs from the input payload
- For each beneficiary, creates an object with the BeneficiaryId and a "DELETED" status
- Uses `skipNullOn = "everywhere"` to remove null values from the output

## Payment Management Transformations

### p-addPaymentOrdersResponse.dwl
This transformation generates a response for adding payment orders, including unique IDs.

```dataweave
%dw 2.0
var sot= "PMT"
var stordTrack= "STORDTRACK"
var sotNumbers= '0123456789'
var sotCharSetLength= sizeOf(sotNumbers) - 1
var sotNumbersLength= 7
output application/json skipNullOn = "everywhere"
---
{
	Payments: payload.Payments map ($ ++ {
		CreationDateTime: now(),
		PaymentId: sot ++ (1 to sotNumbersLength map sotNumbers[randomInt(sotCharSetLength)] joinBy '')
	})
}
```

The transformation:
- Defines variables for generating unique payment IDs
- Maps through the payments from the input payload
- For each payment, adds a CreationDateTime (current time) and a unique PaymentId
- The ID format is "PMT" followed by 7 random digits
- Uses `skipNullOn = "everywhere"` to remove null values from the output

### p-cancelPaymentOrdersResponse.dwl
This transformation creates a response for canceling payment orders.

```dataweave
%dw 2.0
output application/json
---
{
	PaymentIds: payload.PaymentIds,
	CancelDateTime: now()
}
```

The transformation:
- Takes the PaymentIds from the input payload
- Adds a CancelDateTime with the current time

### p-retrievePaymentOrdersResponse.dwl
This transformation filters payment orders based on query parameters.

```dataweave
%dw 2.0
output application/json  
---
{
  PaymentOrders: 
    if (attributes.queryParams.paymentId? and attributes.queryParams.payeeName? and attributes.queryParams.amount?)
      vars.paymentOrders filter ($.PaymentId ~= attributes.queryParams.paymentId and $.Payments.PayeeReference.PayeeName ~= attributes.queryParams.payeeName and $.Payments.PaymentDefinition.PaymentAmount.Amount ~= attributes.queryParams.amount)
    else if (attributes.queryParams.paymentId? and attributes.queryParams.payeeName?)
      vars.paymentOrders filter ($.PaymentId ~= attributes.queryParams.paymentId and $.Payments.PayeeReference.PayeeName ~= attributes.queryParams.payeeName)
    else if (attributes.queryParams.paymentId? and attributes.queryParams.amount?)
      vars.paymentOrders filter ($.PaymentId ~= attributes.queryParams.paymentId and $.Payments.PaymentDefinition.PaymentAmount.Amount ~= attributes.queryParams.amount)
    else if (attributes.queryParams.payeeName? and attributes.queryParams.amount?)
      vars.paymentOrders filter ($.Payments.PayeeReference.PayeeName ~= attributes.queryParams.payeeName and $.Payments.PaymentDefinition.PaymentAmount.Amount ~= attributes.queryParams.amount)
    else if (attributes.queryParams.paymentId?)
      vars.paymentOrders filter ($.PaymentId ~= attributes.queryParams.paymentId)
    else if (attributes.queryParams.payeeName?)
      vars.paymentOrders filter ($.Payments.PayeeReference.PayeeName ~= attributes.queryParams.payeeName)
    else if (attributes.queryParams.amount?)
      vars.paymentOrders filter ($.Payments.PaymentDefinition.PaymentAmount.Amount ~= attributes.queryParams.amount)
    else
      vars.paymentOrders
}
```

The transformation:
- Uses a series of conditional statements to filter payment orders based on query parameters
- Checks for various combinations of filter parameters (paymentId, payeeName, amount)
- Uses the `~=` operator for case-insensitive matching
- Returns all payment orders if no filters are provided

## Specialized Financial Operations Transformations

### p-acatResponse.dwl
This transformation creates a response for ACATS transfers.

```dataweave
%dw 2.0
output application/json skipNullOn="everywhere"
---
{
	AcatDetails: {
		TransferType: payload.AcatDetails.TransferType,
		AcatType: payload.AcatDetails.AcatType default null,
		TransferAction: payload.AcatDetails.TransferAction,
		TransferDetails: {
			Securities: payload.AcatDetails.TransferDetails.Securities,
			Cash: payload.AcatDetails.TransferDetails.Cash,
			FundsTransfer: payload.AcatDetails.TransferDetails.FundsTransfer,
			CashTransfer: payload.AcatDetails.TransferDetails.CashTransfer,
			CDTransfer: payload.AcatDetails.TransferDetails.CDTransfer,
			AnnuityTransfer: payload.AcatDetails.TransferDetails.AnnuityTransfer,
			ManagedAccountTransfer: payload.AcatDetails.TransferDetails.ManagedAccountTransfer
		},
		ExternalAccountDetails: {
			AccountNumber: payload.AcatDetails.ExternalAccountDetails.AccountNumber,
			AccountType: payload.AcatDetails.ExternalAccountDetails.AccountType,
			AccountTitle: payload.AcatDetails.ExternalAccountDetails.AccountTitle,
			TransferringFirmDetails: {
				FirmName: payload.AcatDetails.ExternalAccountDetails.TransferringFirmDetails.FirmName,
				Phone: payload.AcatDetails.ExternalAccountDetails.TransferringFirmDetails.Phone,
				Address: payload.AcatDetails.ExternalAccountDetails.TransferringFirmDetails.Address
			}
		}
	}
}
```

The transformation:
- Maps the ACATS details from the input payload to the output structure
- Uses `default null` for the AcatType field to handle cases where it's not provided
- Uses `skipNullOn="everywhere"` to remove null values from the output

### p-rmdResponse.dwl
This transformation creates a response for Required Minimum Distribution requests.

```dataweave
%dw 2.0
output application/json skipNullOn="everywhere"
---
{
		PaymentOption: payload.PaymentOption,
		PaymentFrequency: payload.PaymentFrequency,
		DistributionSchedule: payload.DistributionSchedule,
		TaxYear: payload.TaxYear,
		CalculateRMDAmount: payload.CalculateRMDAmount,
		WithdrawlAmount: payload.WithdrawlAmount,
		PaymentInstructions: payload.PaymentInstructions,
		TaxWithholdings: payload.TaxWithholdings
}
```

The transformation:
- Maps the RMD details from the input payload to the output structure
- Uses `skipNullOn="everywhere"` to remove null values from the output

## Customer Profile Transformation

### p-updateProfileResponse.dwl
This transformation creates a response for updating customer profiles.

```dataweave
%dw 2.0
var ProfileInformation = payload.ProfileInformation
output application/json skipNullOn="everywhere"
---
{
	ProfileInformation: {
		Addresses: ProfileInformation.Addresses map ( address , indexOfAddress ) -> {
			AddressLine2: address.AddressLine2,
			AddressLine1: address.AddressLine1,
			State: address.State,
			PostalCode: address.PostalCode,
			City: address.City,
			AddressType: address.AddressType,
			Country: address.Country
		},
		Email: ProfileInformation.Email,
		FirstName: ProfileInformation.FirstName,
		Phone: ProfileInformation.Phone,
		LastName: ProfileInformation.LastName,
		Mobile: ProfileInformation.Mobile,
		BirthDate: ProfileInformation.BirthDate,
		MaritalStatus: ProfileInformation.MaritalStatus,
		EmploymentDetails: ProfileInformation.EmploymentDetails
	}
}
```

The transformation:
- Stores the ProfileInformation from the payload in a variable for easier access
- Maps through the addresses in the profile information
- Restructures each address with the specified fields
- Maps the remaining profile fields directly
- Uses `skipNullOn="everywhere"` to remove null values from the output

# SAP Integration Suite Implementation

## Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|-------------------|----------------------------------|-------|
| HTTP Listener | HTTPS Adapter | Configure with the same path and method settings |
| Router | Router | Direct equivalent in SAP Integration Suite |
| Flow Reference | Process Call | Used to call subflows in SAP Integration Suite |
| Transform Message | Message Mapping | Maps to the Content Modifier with mapping capabilities |
| Set Variable | Content Modifier | Used to set variables in the message header or properties |
| Set Payload | Content Modifier | Used to set the message body |
| Logger | Write Message to Log | Configure with the same log message format |
| Error Handler | Exception Subprocess | Handles errors in a dedicated subprocess |

## Integration Flow Visualization

### Flow 1: fsc-wealth-management-api-main

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Main API Flow
start((Start)) --> listener[HTTP Listener]:::httpAdapter
listener --> response[Response]:::contentModifier
response --> headers1[Headers]:::contentModifier
headers1 --> errorResponse[Error Response]:::contentModifier
errorResponse --> body[Body]:::contentModifier
body --> headers2[Headers]:::contentModifier
headers2 --> logger1[Logger]:::contentModifier
logger1 --> logger2[Logger]:::contentModifier
logger2 --> router{Router}:::router
router --> logger3[Logger]:::contentModifier
logger3 --> end((End))

%% Error Handler
listener -->|Error| errorHandler[(Error Handler)]:::exception
errorHandler --> end
```

### Flow 2: patch:/InvestmentAccounts/Update:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Update Beneficiaries Flow
start((Start)) --> updateBeneficiariesSubFlow[[update-beneficiaries-sub-flow]]:::processCall
updateBeneficiariesSubFlow --> end((End))
```

### Flow 3: delete:/InvestmentAccounts/Delete:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Delete Beneficiaries Flow
start((Start)) --> deleteBeneficiariesSubFlow[[delete-beneficiaries-sub-flow]]:::processCall
deleteBeneficiariesSubFlow --> end((End))
```

### Flow 4: get:/InvestmentAccounts/accountId/Retrieve:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Retrieve Investment Account Details Flow
start((Start)) --> retrieveInvestmentAccountDetailsSubFlow[[retrieve-investment-account-details-sub-flow]]:::processCall
retrieveInvestmentAccountDetailsSubFlow --> end((End))
```

### Flow 5: post:/InvestmentAccounts/Initiate:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Add Beneficiaries Flow
start((Start)) --> addBeneficiariesSubFlow[[add-beneficiaries-sub-flow]]:::processCall
addBeneficiariesSubFlow --> end((End))
```

### Flow 6: patch:/customers/customerId:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Update Customers Profile Flow
start((Start)) --> updateCustomersProfileSubFlow[[update-customers-profile-sub-flow]]:::processCall
updateCustomersProfileSubFlow --> end((End))
```

### Flow 7: patch:/InvestmentAccounts/accountId/Payments/Update:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Cancel Standing Orders Flow
start((Start)) --> cancelStandingOrdersSubFlow[[cancel-standing-orders-sub-flow]]:::processCall
cancelStandingOrdersSubFlow --> end((End))
```

### Flow 8: post:/InvestmentAccounts/accountId/Payments/Initiate:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Add Standing Orders Flow
start((Start)) --> addStandingOrdersSubFlow[[add-standing-orders-sub-flow]]:::processCall
addStandingOrdersSubFlow --> end((End))
```

### Flow 9: get:/InvestmentAccounts/accountId/Payments/Retrieve:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Retrieve Standing Orders Flow
start((Start)) --> retrieveStandingOrdersSubFlow[[retrieve-standing-orders-sub-flow]]:::processCall
retrieveStandingOrdersSubFlow --> end((End))
```

### Flow 10: post:/InvestmentAccounts/accountId/Acats:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% ACATS Flow
start((Start)) --> prepareAcatsResponseSubFlow[[prepare-acats-response-sub-flow]]:::processCall
prepareAcatsResponseSubFlow --> end((End))
```

### Flow 11: post:/InvestmentAccounts/accountId/RMD:application/json:fsc-wealth-management-api-config

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% RMD Flow
start((Start)) --> prepareRmdResponseSubFlow[[prepare-rmd-response-sub-flow]]:::processCall
prepareRmdResponseSubFlow --> end((End))
```

### Flow 12: delete-beneficiaries-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Delete Beneficiaries Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 13: retrieve-investment-account-details-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Retrieve Investment Account Details Subflow
start((Start)) --> setVariable[Set Variable]:::contentModifier
setVariable --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 14: retrieve-standing-orders-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Retrieve Standing Orders Subflow
start((Start)) --> logger[Logger]:::contentModifier
logger --> setVariable[Set Variable]:::contentModifier
setVariable --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 15: update-customers-profile-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Update Customers Profile Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 16: cancel-standing-orders-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Cancel Standing Orders Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 17: update-beneficiaries-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Update Beneficiaries Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 18: prepare-acats-response-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Prepare ACATS Response Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 19: add-standing-orders-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Add Standing Orders Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 20: prepare-rmd-response-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Prepare RMD Response Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

### Flow 21: add-beneficiaries-sub-flow

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Add Beneficiaries Subflow
start((Start)) --> transform[Transform]:::mapping
transform --> message[Message]:::contentModifier
message --> setPayload[Set Payload]:::contentModifier
setPayload --> end((End))
```

## Configuration Details

### HTTPS Adapter Configuration
- **Address**: `/fsc-wealth-management-api`
- **Port**: 443 (HTTPS)
- **Authentication**: Basic or OAuth2 (configuration decision)
- **TLS Configuration**: Required, using keystore from `integration@keystore` secret

### Router Configuration
- **Condition Type**: Content-based routing
- **Routing Rules**: Based on HTTP method and path patterns
- **Default Route**: Error response

### Content Modifier Configuration
- **Message Headers**: Set appropriate response headers
- **Message Body**: Set response payload
- **Exchange Properties**: Set variables for processing

### Message Mapping Configuration
- **Source Format**: JSON
- **Target Format**: JSON
- **Mapping Scripts**: Implement the DataWeave transformations using SAP Integration Suite mapping capabilities

### Process Call Configuration
- **Process Reference**: Reference to the appropriate subflow
- **Parameters**: Pass necessary context variables

### Write Message to Log Configuration
- **Log Level**: INFO
- **Message**: Same format as in MuleSoft logger components

### Exception Subprocess Configuration
- **Error Types**: Map to MuleSoft error types (APIKIT:BAD_REQUEST, APIKIT:NOT_FOUND, etc.)
- **Error Handling**: Generate appropriate error responses with status codes

# Configuration

## Important Configuration Parameters
- **API Definition**: The API is defined in RAML 1.0 format with the main file `fsc-wealth-management-api.raml`
- **HTTP Listener Configuration**: Named `fsc-wealth-management-api-httpListenerConfig`
- **API Configuration**: Named `fsc-wealth-management-api-config` with outbound headers map and HTTP status variable

## Environment Variables
- No explicit environment variables are defined in the source documentation

## Dependencies on External Systems
- The application appears to be self-contained with mock responses
- No explicit external system dependencies are mentioned in the source documentation

## Security Settings and Certificates
- **TLS Configuration**: The application uses TLS with keystore and key secrets defined in `config.yaml`
- **Keystore Secret**: `integration@keystore`
- **Key Secret**: `integration@keystore`