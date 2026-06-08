# SOP — Return Excess Product to Supplier
**Process ID:** SCOR-SR3.5
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Physical execution of excess product return to supplier including preparation, shipment execution and credit confirmation

## Triggers
- Receipt of ReturnAuthorization from Supplier
- Publication of ReturnShipmentSchedule

## Inputs Required
- return shipment schedule
- return authorization
- product preparation
- carrier pickup

## Process Steps
1. IF ReturnAuthorization.valid == true AND expiry_compliance == true THEN proceed to product preparation
2. IF carrier_pickup.confirmed == true THEN execute shipment and generate ReturnedExcessShipment

## Expected Outputs
- returned excess shipment
- proof of delivery
- credit note

## Business Rules
- chain_of_custody document must be recorded at every handover
- financial_credit_documentation required before CreditNote creation
- return_accuracy must be verified against ReturnAuthorization before shipment

## Exception Handling
- IF product expired beyond policy: reject shipment, log exception, notify Supplier and update KPIs
- IF ProofOfDelivery missing after 48h: hold CreditNote and trigger compliance audit

## Success Criteria
- ProofOfDelivery received AND CreditNote issued AND return_completion_rate >= 0.95 AND credit_recovery_rate >= 0.90

## Compliance Requirements
- expiry compliance
- chain of custody
- financial credit documentation