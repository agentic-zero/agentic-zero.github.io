# SOP — Authorize Supplier Payment (ETO)
**Process ID:** SCOR-S3.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-10

## Purpose
Process of authorizing milestone-based or delivery-based payments for ETO suppliers upon verified receipt and engineering acceptance of custom components

## Triggers
- Receipt of SupplierInvoice linked to open MilestoneCompletion
- EngineeringAcceptanceReport submission with status accepted

## Inputs Required
- milestone completions
- engineering acceptance reports
- supplier invoices
- contract payment terms
- project financial data

## Process Steps
1. IF EngineeringAcceptanceReport.status == 'accepted' AND SupplierInvoice.amount <= ContractPaymentTerm.milestone_amount AND ProjectFinancialData.available_budget >= SupplierInvoice.amount THEN create MilestonePaymentAuthorization
2. IF milestone_completion_date > ContractPaymentTerm.due_date THEN flag for compliance review before authorization

## Expected Outputs
- milestone payment authorizations
- payment confirmations
- project cost updates
- supplier financial records

## Business Rules
- Authorization requires both verified receipt and engineering acceptance sign-off
- Payment amount must exactly match approved milestone value in ContractPaymentTerm
- All payment authorizations must be logged with timestamp and approver_id for audit

## Exception Handling
- Partial milestone completion: escalate to project manager for manual partial authorization approval
- Missing EngineeringAcceptanceReport: hold authorization and notify engineering team within 24 hours

## Success Criteria
- MilestonePaymentAuthorization created with status 'authorized' within defined payment cycle time
- ProjectCostUpdate reflects exact payment amount and SupplierFinancialRecord updated

## Compliance Requirements
- government contracting regulations
- milestone payment compliance
- GDPR financial data
- export control financial