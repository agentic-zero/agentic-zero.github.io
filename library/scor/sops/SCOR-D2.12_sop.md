# SOP — Ship Product (MTO)
**Process ID:** SCOR-D2.12
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of executing MTO shipment dispatch including carrier handover, tracking initiation, customer notification and in-transit monitoring

## Triggers
- SCOR-D2.11 completion event with LoadedVehicle payload

## Inputs Required
- loaded vehicle
- shipping documents
- tracking systems
- customer notification templates
- carrier contact data

## Process Steps
1. IF LoadedVehicle.status == 'ready' AND ShippingDocument.compliance == true THEN execute CarrierHandover
2. IF carrier accepts handover THEN start TrackingSystem and send CustomerNotification

## Expected Outputs
- dispatched shipment
- tracking confirmation
- customer notification
- in-transit monitoring

## Business Rules
- dispatch_time must be <= planned_dispatch_time + 30min for on-time KPI
- tracking_coverage must include GPS + carrier_API for 100% coverage
- GDPR: anonymize customer tracking data after 30 days
- dangerous_goods: attach UN_number and MSDS to ShippingDocument

## Exception Handling
- IF customs_export_compliance fails THEN hold shipment and notify compliance_officer
- IF carrier rejects handover THEN fallback to secondary_carrier from CarrierContactData within 2 hours

## Success Criteria
- on-time dispatch rate >= 95%
- tracking confirmation received within 15min of handover
- customer notification sent before vehicle departure

## Compliance Requirements
- customs export compliance
- dangerous goods transport
- GDPR tracking data
- carrier liability