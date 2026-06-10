# SOP — Invoice-to-Cash (Accounts Receivable)
**Process ID:** BPMN-FIN-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-10

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
2. IF DisputeRaised? == true THEN ManageDispute ELSE SendReminder
3. IF Overdue? == true AND Escalate? == true THEN EscalateDunning ELSE SendReminder
4. IF NegotiatePaymentPlan accepted THEN update PaymentTerms ELSE WriteOff

## Expected Outputs
- cash receipts
- applied payments
- dispute records
- aging reports
- DSO metrics

## Business Rules
- dunning_rules must define reminder intervals and escalation thresholds
- payment_terms must be attached to every Invoice before SendInvoice
- cash_application_accuracy must exceed 99.5% for automated ApplyCash
- GDPR financial data requires anonymization after 7 years

## Exception Handling
- DisputeRaised with amount > 5000 requires Management approval before resolution
- PaymentReceived but unapplied after 3 days triggers manual Reconcile
- Customer in lane triggers Sales notification on Escalated Dunning

## Success Criteria
- end_event == CashApplied
- DSO <= target_DSO
- collection_rate >= 0.95

## Compliance Requirements
- tax compliance
- GDPR financial data
- e-invoicing regulations
- financial reporting