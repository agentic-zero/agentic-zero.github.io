# SOP — Receive and Verify Product by Customer (MTO)
**Process ID:** SCOR-D2.13
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of supporting customer receipt and verification of MTO products including proof of delivery confirmation, customer acceptance support and invoice triggering

## Triggers
- Shipment delivered event received from carrier API

## Inputs Required
- shipment tracking data
- proof of delivery
- customer acceptance criteria
- invoice data
- customer feedback

## Process Steps
1. IF ProofOfDelivery exists AND AcceptanceCriteria met THEN create AcceptanceRecord and trigger InvoiceTrigger ELSE log exception

## Expected Outputs
- delivery confirmation
- customer acceptance record
- invoice trigger
- customer satisfaction data

## Business Rules
- ProofOfDelivery must be recorded before AcceptanceRecord creation
- InvoiceTrigger only fires after AcceptanceRecord status=accepted
- GDPR consent flag required on all CustomerFeedback storage

## Exception Handling
- Missing ProofOfDelivery: notify carrier and hold invoice for 48h
- AcceptanceCriteria failure: create return authorization and update delivery_exception_rate KPI

## Success Criteria
- DeliveryConfirmation.status=confirmed
- AcceptanceRecord.status=accepted
- InvoiceTrigger emitted within SLA
- proof_of_delivery_rate >= 0.98

## Compliance Requirements
- GDPR customer acceptance data
- contractual acceptance terms
- invoice compliance