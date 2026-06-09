# SOP — Authorize Supplier Payment (MTO)
**Process ID:** SCOR-S2.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of authorizing and processing supplier payments for MTO materials upon verified receipt, matching invoices against purchase orders and delivery confirmations

## Triggers
- SupplierInvoice received in ERP with linked po_id after GoodsReceipt.verified_date is not null

## Inputs Required
- supplier invoices
- goods receipts
- purchase orders
- payment terms
- quality verification results

## Process Steps
1. IF SupplierInvoice.amount == PurchaseOrder.amount AND GoodsReceipt.received_qty == PurchaseOrder.ordered_qty AND QualityVerificationResult.status == 'passed' THEN create PaymentAuthorization with status='approved'

## Expected Outputs
- payment authorizations
- payment confirmations
- supplier account updates
- discrepancy resolutions

## Business Rules
- Three-way match (invoice, PO, goods receipt) required before PaymentAuthorization creation
- PaymentAuthorization.due_date must respect PaymentTerms.net_days from GoodsReceipt.date
- PaymentAuthorization.amount must equal SupplierInvoice.amount after tax adjustments

## Exception Handling
- IF any three-way match field differs by >0.01 THEN create DiscrepancyResolution with status='open' and block PaymentAuthorization
- IF QualityVerificationResult.status == 'failed' THEN reject SupplierInvoice and notify supplier via email workflow

## Success Criteria
- PaymentAuthorization.status == 'approved' AND SupplierAccount.last_payment_date updated AND discrepancy_count == 0

## Compliance Requirements
- financial controls compliance
- GDPR financial data
- tax compliance
- anti-fraud controls