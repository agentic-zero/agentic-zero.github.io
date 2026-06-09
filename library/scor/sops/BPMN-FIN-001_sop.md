# SOP — Invoice-to-Cash (Accounts Receivable)
**Process ID:** BPMN-FIN-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Invoice-to-Cash process from invoice generation to cash collection including invoice dispatch, dunning, dispute management and cash application

## Triggers
- Invoice Generated event from ERP

## Inputs Required
- invoices
- payment terms
- customer data
- bank data
- dunning rules

## Process Steps
1. IF PaymentReceived? == true THEN ApplyCash ELSE MonitorPayment
2. IF DisputeRaised? == true THEN ManageDispute ELSE ContinueDunning
3. IF Overdue? == true AND Escalate? == true THEN EscalateDunning ELSE SendReminder
4. IF PaymentPlan negotiated THEN NegotiatePaymentPlan ELSE WriteOff

## Expected Outputs
- cash receipts
- applied payments
- dispute records
- aging reports
- DSO metrics

## Business Rules
- Invoice must contain payment terms before SendInvoice
- Dunning rules must be applied after 7/14/30 days overdue
- CashApplication accuracy must exceed 99% before closing process
- GDPR financial data must be masked for non-Finance lanes

## Exception Handling
- Dispute unresolved after 45 days triggers WriteOff
- Partial payment received requires manual reconciliation before CashApplied
- Customer bankruptcy forces immediate WriteOff and aging report update

## Success Criteria
- CashApplied end event reached with collection_rate >= 95%
- DSO metric updated and within target threshold

## Compliance Requirements
- tax compliance
- GDPR financial data
- e-invoicing regulations
- financial reporting