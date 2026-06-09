# SOP — Load Vehicle and Generate Shipping Docs (MTO)
**Process ID:** SCOR-D2.11
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of loading MTO shipments onto carrier vehicles and generating all required shipping documentation including bills of lading, customs documents and customer notifications

## Triggers
- All inputs (packed shipments, load plan, carrier vehicle, documentation requirements, customs data) received and validated

## Inputs Required
- packed shipments
- load plan
- carrier vehicle
- documentation requirements
- customs data

## Process Steps
1. IF CustomsData contains export-controlled items THEN require export_compliance flag before generating CustomsDocumentation
2. IF PackedShipment contains dangerous goods THEN enforce dangerous_goods_documentation rule before loading

## Expected Outputs
- loaded vehicle
- bill of lading
- customs documentation
- customer shipment notification
- proof of dispatch

## Business Rules
- All PackedShipment must match LoadPlan quantities before CarrierVehicle departure
- BillOfLading must be generated only after 100% loading accuracy verified
- GDPR shipment data must be anonymized in CustomerShipmentNotification

## Exception Handling
- IF documentation incomplete THEN block ProofOfDispatch and route to manual review queue
- IF carrier vehicle capacity exceeded THEN reject LoadPlan and trigger replanning with SCOR-D2.10

## Success Criteria
- loading accuracy == 100%
- document completeness == true
- on-time departure == true
- ProofOfDispatch generated with valid carrier signature

## Compliance Requirements
- customs documentation compliance
- dangerous goods documentation
- GDPR shipment data
- export compliance