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