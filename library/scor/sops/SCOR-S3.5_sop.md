# SOP — Authorize Supplier Payment (ETO)
**Process ID:** SCOR-S3.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of authorizing milestone-based or delivery-based payments for ETO suppliers upon verified receipt and engineering acceptance of custom components

## Triggers
- new SupplierInvoice received with linked milestone_id
- EngineeringAcceptanceReport status changed to verified

## Inputs Required
- milestone completions
- engineering acceptance reports
- supplier invoices
- contract payment terms
- project financial data

## Process Steps
1. IF milestone_completed == true AND engineering_accepted == true AND invoice_matches_terms == true THEN create MilestonePaymentAuthorization
2. IF compliance_flags contain government_contracting_regulations THEN require additional_approval == true

## Expected Outputs
- milestone payment authorizations
- payment confirmations
- project cost updates
- supplier financial records

## Business Rules
- authorization_amount must equal contract_payment_term.amount for the milestone
- payment_cycle_time must be <= KPI threshold
- all inputs must have matching project_id and supplier_id
- GDPR_financial_data and export_control_financial must be masked before storage

## Exception Handling
- missing EngineeringAcceptanceReport: reject and notify engineering team
- invoice_amount mismatch > 2%: route to exception queue for manual review
- contract compliance rate < 95%: block authorization and escalate to procurement

## Success Criteria
- MilestonePaymentAuthorization created with status=approved
- PaymentConfirmation timestamp recorded within payment_cycle_time KPI
- ProjectCostUpdate and SupplierFinancialRecord updated with zero errors

## Compliance Requirements
- government contracting regulations
- milestone payment compliance
- GDPR financial data
- export control financial