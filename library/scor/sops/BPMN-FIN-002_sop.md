# SOP — Accounts Payable Automation
**Process ID:** BPMN-FIN-002
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Automated accounts payable process from invoice receipt to payment execution including AI-powered invoice capture, 3-way matching, exception handling and payment processing

## Triggers
- Invoice Received event from supplier or e-invoicing platform

## Inputs Required
- supplier invoices
- purchase orders
- goods receipts
- payment terms
- bank data

## Process Steps
1. IF Duplicate? == true THEN reject Invoice
2. IF 3-Way Match OK? == false THEN HandleException
3. IF Within Tolerance? == false THEN Route for Approval
4. IF Approval Required? == true THEN route to Approver lane ELSE PostInvoice

## Expected Outputs
- posted invoices
- payment files
- reconciliation data
- supplier remittances

## Business Rules
- Invoice must have valid VAT/GST tax data before PostInvoice
- 3-way match tolerance must be <= 2% on amount and quantity
- Payment execution requires bank data validation and anti-fraud check
- GDPR financial data must be encrypted at rest and in transit

## Exception Handling
- Duplicate invoice detected: auto-reject and notify Finance lane
- 3-way match failure: create Exception record and route to Finance for manual review within 24h
- Amount outside tolerance: escalate to Approver with mismatch details

## Success Criteria
- Payment Executed status reached with reconciliation data generated
- Straight-through processing rate >= 70%
- Invoice cycle time <= 5 business days

## Compliance Requirements
- tax compliance VAT/GST
- GDPR financial data
- e-invoicing mandate
- anti-fraud controls