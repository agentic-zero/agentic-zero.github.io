# SOP — Return Excess Product to Supplier
**Process ID:** SCOR-SR3.5
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Physical execution of excess product return to supplier including preparation, shipment execution and credit confirmation

## Triggers
- receipt of approved ReturnAuthorization and ReturnShipmentSchedule

## Inputs Required
- return shipment schedule
- return authorization
- product preparation
- carrier pickup

## Process Steps
1. IF ReturnAuthorization.status == 'approved' THEN execute ProductPreparation
2. IF carrier pickup confirmed THEN generate ReturnedExcessShipment

## Expected Outputs
- returned excess shipment
- proof of delivery
- credit note

## Business Rules
- chain_of_custody: maintain signed logs for all pharma and food shipments
- financial_credit_documentation: CreditNote must reference original PO and return authorization ID
- expiry_compliance: reject return if product expiry < 30 days from receipt

## Exception Handling
- IF product damaged during CarrierPickup THEN quarantine shipment and create exception ticket with photos before proceeding to credit
- IF CreditNote rejected by supplier THEN escalate to SCOR-SR3.4 for dispute resolution

## Success Criteria
- ReturnCompletionRate == 1.0
- CreditRecoveryRate >= 0.95
- ReturnAccuracy == 1.0 with ProofOfDelivery received

## Compliance Requirements
- expiry compliance
- chain of custody
- financial credit documentation