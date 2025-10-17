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