# SOP — Receive Defective Product Return
**Process ID:** SCOR-DR1.3
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-08

## Purpose
Physical receipt, inspection and verification of defective product returns against RMA authorization including condition assessment and system update

## Triggers
- Arrival of scheduled return shipment at receiving dock with valid RMA

## Inputs Required
- scheduled return shipment
- RMA documentation
- inspection criteria
- receiving equipment

## Process Steps
1. IF received_serials match RMA AND condition passes inspection_criteria THEN accept ELSE quarantine

## Expected Outputs
- received return confirmation
- inspection report
- system inventory update
- credit trigger

## Business Rules
- RMA must be valid and not expired before physical receipt
- Inspection must complete within KPI cycle_time before system update
- GxP compliance required if sector=pharma: all inspection data immutable

## Exception Handling
- Serial mismatch or damage beyond RMA: quarantine item, create exception ticket, notify originating SCOR-DR1.2

## Success Criteria
- received return confirmation emitted
- inspection_report generated with pass/fail
- inventory_system updated
- credit_trigger emitted within KPI time

## Compliance Requirements
- GxP if pharma
- quality inspection standards
- GDPR if personal data in records