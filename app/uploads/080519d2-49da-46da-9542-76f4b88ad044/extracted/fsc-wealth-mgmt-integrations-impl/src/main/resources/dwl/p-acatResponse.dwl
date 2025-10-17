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