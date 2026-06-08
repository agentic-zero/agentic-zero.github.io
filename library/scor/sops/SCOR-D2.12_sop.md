# SOP — Ship Product (MTO)
**Process ID:** SCOR-D2.12
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of executing MTO shipment dispatch including carrier handover, tracking initiation, customer notification and in-transit monitoring

## Triggers
- LoadedVehicle status == ready AND ShippingDocument validated

## Inputs Required
- loaded vehicle
- shipping documents
- tracking systems
- customer notification templates
- carrier contact data

## Process Steps
1. IF dangerous_goods_flag == true THEN apply DG transport rules and carrier approval
2. IF export_compliance_check == false THEN hold shipment and trigger customs review

## Expected Outputs
- dispatched shipment
- tracking confirmation
- customer notification
- in-transit monitoring

## Business Rules
- dispatch only after LoadedVehicle and ShippingDocument both present
- tracking_initiation must complete within 15 minutes of carrier handover
- customer_notification must use approved template and include shipment_id + ETA

## Exception Handling
- missing tracking confirmation: auto-retry 3 times then escalate to carrier contact
- GDPR data flag: anonymize tracking data after 90 days

## Success Criteria
- on-time dispatch rate >= 98%
- tracking confirmation received within SLA
- customer notification sent within 5 minutes of dispatch

## Compliance Requirements
- customs export compliance
- dangerous goods transport
- GDPR tracking data
- carrier liability