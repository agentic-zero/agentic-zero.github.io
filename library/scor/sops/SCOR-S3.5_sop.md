# SOP — Authorize Supplier Payment (ETO)
**Process ID:** SCOR-S3.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of authorizing milestone-based or delivery-based payments for ETO suppliers upon verified receipt and engineering acceptance of custom components

## Triggers
- new SupplierInvoice received with matching milestone_id
- EngineeringAcceptanceReport status changed to accepted

## Inputs Required
- milestone completions
- engineering acceptance reports
- supplier invoices
- contract payment terms
- project financial data

## Process Steps
1. IF milestone_completion.verified == true AND engineering_acceptance.status == 'accepted' AND invoice.amount <= contract.terms.max_milestone THEN create MilestonePaymentAuthorization
2. IF contract.compliance_flags contains 'export_control' THEN require additional_approval == true before authorization

## Expected Outputs
- milestone payment authorizations
- payment confirmations
- project cost updates
- supplier financial records

## Business Rules
- payment only after verified receipt and engineering acceptance
- authorization amount must exactly match contract_payment_term.milestone_value
- cycle_time must be logged for KPI calculation
- all financial data must satisfy GDPR and government contracting regulations

## Exception Handling
- missing engineering acceptance: hold authorization and notify engineering team
- invoice amount mismatch > 2%: reject and return to supplier with discrepancy report
- contract compliance failure: escalate to compliance officer and block payment

## Success Criteria
- MilestonePaymentAuthorization created with status 'authorized'
- payment_cycle_time < target_threshold
- contract_compliance_rate == 1.0
- PaymentConfirmation sent to supplier

## Compliance Requirements
- government contracting regulations
- milestone payment compliance
- GDPR financial data
- export control financial