# SOP — Transport Management
**Process ID:** BPMN-TRP-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Transport management process from shipment planning to proof of delivery including carrier selection, booking, tracking and freight payment

## Triggers
- ShipmentOrderCreated event received from ERP system

## Inputs Required
- shipment orders
- carrier contracts
- route data
- customs requirements
- delivery addresses

## Process Steps
1. IF CarrierAvailable == true THEN BookTransport ELSE select alternative carrier
2. IF ExceptionDetected == true THEN ManageExceptions ELSE continue tracking
3. IF DeliveryConfirmed == true THEN ProcessFreightInvoice ELSE escalate
4. IF InvoiceMatch == true THEN close process ELSE dispute invoice

## Expected Outputs
- carrier bookings
- shipping documents
- tracking data
- proof of delivery
- freight invoices

## Business Rules
- Carrier must have valid contract before booking
- Dangerous goods require ADR compliance flag
- Shipment data must comply with GDPR before sharing with carrier
- On-time delivery KPI threshold >= 95%
- Freight cost per unit must be within contracted rate

## Exception Handling
- ExceptionDetected triggers ManageExceptions task and routes to ExceptionResolved end event
- Invoice mismatch creates dispute case and pauses payment
- Carrier unavailability triggers re-selection within 4 hours

## Success Criteria
- end event DeliveryConfirmed reached
- ProofOfDelivery received and archived
- FreightInvoice status = paid
- on_time_delivery == true

## Compliance Requirements
- customs compliance
- dangerous goods ADR
- GDPR shipment data
- driver regulations