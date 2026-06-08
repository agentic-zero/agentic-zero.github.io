# SOP — Receive Defective Product Return
**Process ID:** SCOR-DR1.3
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Physical receipt, inspection and verification of defective product returns against RMA authorization including condition assessment and system update

## Triggers
- Arrival of scheduled ReturnShipment at receiving dock with RMADocument

## Inputs Required
- scheduled return shipment
- RMA documentation
- inspection criteria
- receiving equipment

## Process Steps
1. IF ReturnShipment matches RMADocument AND passes InspectionCriteria THEN create InspectionReport ELSE flag exception
2. IF inspection passes THEN issue CreditTrigger ELSE hold for quarantine review

## Expected Outputs
- received return confirmation
- inspection report
- system inventory update
- credit trigger

## Business Rules
- ReturnShipment must have valid RMADocument before physical receipt
- InspectionReport must be generated before SystemInventoryUpdate
- CreditTrigger only issued after successful inspection and confirmation

## Exception Handling
- Mismatch between ReturnShipment and RMADocument: quarantine item and notify originator within 4 hours
- Personal data detected in records: apply GDPR masking before SystemInventoryUpdate

## Success Criteria
- ReceivedReturnConfirmation generated
- InspectionReport completed with pass flag
- SystemInventoryUpdate executed
- CreditTrigger issued

## Compliance Requirements
- GxP if pharma
- quality inspection standards
- GDPR if personal data in records