# SOP — Authorize Supplier Payment (MTO)
**Process ID:** SCOR-S2.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of authorizing and processing supplier payments for MTO materials upon verified receipt, matching invoices against purchase orders and delivery confirmations

## Triggers
- SupplierInvoice received AND GoodsReceipt confirmed AND QualityVerificationResult available

## Inputs Required
- supplier invoices
- goods receipts
- purchase orders
- payment terms
- quality verification results

## Process Steps
1. IF SupplierInvoice.amount == PurchaseOrder.amount AND GoodsReceipt.quantity >= PurchaseOrder.quantity AND QualityVerificationResult.status == 'passed' THEN create PaymentAuthorization
2. IF payment_terms.net_days elapsed AND no discrepancies THEN trigger PaymentConfirmation

## Expected Outputs
- payment authorizations
- payment confirmations
- supplier account updates
- discrepancy resolutions

## Business Rules
- Invoice must three-way match with PO and GoodsReceipt before authorization
- Payment must comply with financial_controls and anti-fraud rules
- Apply payment_terms.discount if paid within discount_period
- Log all payment data under GDPR_financial_data and tax_compliance

## Exception Handling
- Invoice amount mismatch > 1% triggers DiscrepancyResolution and holds PaymentAuthorization
- QualityVerificationResult.failed blocks payment and routes to SCOR-S2.4 for return
- Missing tax_compliance data rejects authorization and logs for audit

## Success Criteria
- PaymentAuthorization created with status 'approved'
- SupplierAccount balance updated
- PaymentConfirmation sent within payment_cycle_time SLA
- invoice_match_rate == 100% for the transaction

## Compliance Requirements
- financial controls compliance
- GDPR financial data
- tax compliance
- anti-fraud controls