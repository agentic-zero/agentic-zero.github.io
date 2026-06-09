# SOP — Receive, Configure, Enter and Validate MTO Order
**Process ID:** SCOR-D2.2
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of receiving and validating MTO customer orders including configuration verification, feasibility assessment, lead time commitment and order acknowledgment

## Triggers
- CustomerOrder received via API or EDI

## Inputs Required
- customer order
- product configurator
- capacity data
- lead time data
- pricing data

## Process Steps
1. IF configuration_valid == true AND capacity_available >= required AND lead_time_feasible == true THEN commit_delivery_date ELSE return rejection_reason

## Expected Outputs
- validated order
- order acknowledgment
- production order trigger
- delivery commitment

## Business Rules
- order_validation_cycle_time <= 4 hours
- configuration_accuracy >= 99 percent
- order_acknowledgment_on_time_rate >= 98 percent
- GDPR consent flag must be true on CustomerOrder
- contractual_terms must match pricing_data before commitment

## Exception Handling
- IF product_configurator returns invalid_options THEN auto-reject with reason_code CONFIG_ERROR and notify customer
- IF capacity_data shows overload THEN escalate to SCOR-M2.1 for rescheduling

## Success Criteria
- ValidatedOrder created with status=APPROVED
- OrderAcknowledgment sent within SLA
- ProductionOrderTrigger emitted to SCOR-M2.1
- DeliveryCommitment recorded with accuracy >= 95 percent

## Compliance Requirements
- GDPR customer order data
- consumer protection regulations
- contractual compliance