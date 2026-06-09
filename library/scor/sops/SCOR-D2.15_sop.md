# SOP — Invoice (MTO)
**Process ID:** SCOR-D2.15
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of generating and sending customer invoices for MTO products upon delivery or milestone completion, managing payment terms and accounts receivable

## Triggers
- delivery_confirmation received
- milestone_completion event from SCOR-D2.13

## Inputs Required
- delivery confirmation
- order data
- pricing data
- payment terms
- customer billing data

## Process Steps
1. IF delivery_confirmation.status == 'complete' OR milestone_reached == true THEN generate_invoice
2. IF invoice_accuracy_rate < 0.98 THEN trigger_manual_review

## Expected Outputs
- customer invoices
- accounts receivable records
- payment tracking
- revenue recognition trigger

## Business Rules
- invoice must include tax_compliance_fields for sector
- customer_financial_data must be GDPR_masked before storage
- e-invoicing_format required for manufacturing and automotive sectors
- revenue_recognition must follow ASC 606 standards

## Exception Handling
- missing_pricing_data: default to order.pricing_data and flag for audit
- payment_terms_conflict: escalate to finance team within 4 hours

## Success Criteria
- invoice_cycle_time < 24 hours
- invoice_accuracy_rate >= 0.99
- payment_collection_rate >= 0.95
- days_sales_outstanding <= target_DSO

## Compliance Requirements
- tax compliance
- GDPR customer financial data
- e-invoicing regulations
- revenue recognition standards