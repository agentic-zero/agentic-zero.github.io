# SOP — Receive, Configure, Enter and Validate MTO Order
**Process ID:** SCOR-D2.2
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of receiving and validating MTO customer orders including configuration verification, feasibility assessment, lead time commitment and order acknowledgment

## Triggers
- Inbound customer order received via EDI/API/portal

## Inputs Required
- customer order
- product configurator
- capacity data
- lead time data
- pricing data

## Process Steps
1. IF configuration valid AND capacity sufficient AND lead time feasible THEN commit order ELSE reject or renegotiate

## Expected Outputs
- validated order
- order acknowledgment
- production order trigger
- delivery commitment

## Business Rules
- Validate all customer order fields against product configurator before proceeding
- Order acknowledgment must be issued within SLA time window
- GDPR consent flag required on all customer order data

## Exception Handling
- Configuration mismatch: route to sales for manual review and customer clarification
- Capacity shortfall: trigger alternative sourcing or delay commitment

## Success Criteria
- ValidatedOrder created with zero validation errors
- OrderAcknowledgment timestamp within SLA
- ProductionOrderTrigger emitted to SCOR-M2.1

## Compliance Requirements
- GDPR customer order data
- consumer protection regulations
- contractual compliance