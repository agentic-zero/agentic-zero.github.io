# SOP — Load Vehicle and Generate Shipping Docs (MTO)
**Process ID:** SCOR-D2.11
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of loading MTO shipments onto carrier vehicles and generating all required shipping documentation including bills of lading, customs documents and customer notifications

## Triggers
- PackedShipment status == packed AND LoadPlan status == approved AND CarrierVehicle status == available

## Inputs Required
- packed shipments
- load plan
- carrier vehicle
- documentation requirements
- customs data

## Process Steps
1. IF customsData.requiresExportLicense == true THEN generateExportLicenseDoc
2. IF loadPlan.totalWeight > carrierVehicle.maxPayload THEN rejectLoadAndAlert
3. IF packedShipment.containsDangerousGoods == true THEN requireDangerousGoodsDeclaration

## Expected Outputs
- loaded vehicle
- bill of lading
- customs documentation
- customer shipment notification
- proof of dispatch

## Business Rules
- All PackedShipment items must match LoadPlan before loading
- BillOfLading must include carrierVehicle.id, PackedShipment.ids and departureTimestamp
- CustomsDocumentation must comply with destinationCountry regulations
- LoadingCycleTime must be recorded with start and end timestamps

## Exception Handling
- IF loading accuracy < 100% THEN halt departure and trigger recount
- IF documentCompleteness < 100% THEN block ProofOfDispatch and queue missing documents
- IF carrierVehicle unavailable THEN reroute to SCOR-D2.12

## Success Criteria
- loadingAccuracy == 100%
- documentCompleteness == 100%
- onTimeDeparture == true
- ProofOfDispatch generated with all output entities

## Compliance Requirements
- customs documentation compliance
- dangerous goods documentation
- GDPR shipment data
- export compliance