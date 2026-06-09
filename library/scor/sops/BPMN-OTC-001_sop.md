# SOP — Order-to-Cash
**Process ID:** BPMN-OTC-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-08

## Purpose
End-to-end Order-to-Cash process from order receipt to payment collection including order validation, fulfillment, shipping, invoicing and cash application

## Triggers
- Order Received event from customer via API or portal

## Inputs Required
- customer order
- inventory data
- credit data
- pricing data
- shipping requirements

## Process Steps
1. IF Items in Stock? == true THEN Pick & Pack ELSE Order Cancelled
2. IF Credit Check Passed? == true THEN Process Payment ELSE Order Cancelled
3. IF Payment Approved? == true THEN Pick & Pack ELSE Order Cancelled

## Expected Outputs
- fulfilled order
- invoice
- cash receipt
- customer confirmation

## Business Rules
- customer order must contain pricing data and shipping requirements before Validate Order
- inventory data must be checked before Pick & Pack
- credit data must pass before Process Payment
- GDPR: customer data must be anonymized after cash receipt
- tax compliance: invoice must be generated before Apply Cash

## Exception Handling
- Order Cancelled if Items in Stock? == false or Credit Check Passed? == false or Payment Approved? == false; notify customer and log reason
- Order Cancelled if any task exceeds 48 hours; escalate to supervisor

## Success Criteria
- Order Complete end event reached with outputs: fulfilled order, invoice, cash receipt, customer confirmation
- perfect order rate >= 0.95 and order cycle time <= SLA

## Compliance Requirements
- GDPR customer data
- tax compliance
- consumer protection