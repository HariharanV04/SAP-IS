%dw 2.0
output application/json
---
{
	LinkedAccount: vars.investmentAccountDetails.LinkedAccount,
	Beneficiaries: vars.investmentAccountDetails.Beneficiaries
}