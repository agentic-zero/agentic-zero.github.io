# SOP — Transport Management
**Process ID:** BPMN-TRP-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-10

## Purpose
Transport management process from shipment planning to proof of delivery including carrier selection, booking, tracking and freight payment

## Triggers
- ShipmentOrder Created event received from ERP or order management system

## Inputs Required
- shipment orders
- carrier contracts
- route data
- customs requirements
- delivery addresses

## Process Steps
1. IF Carrier Available? THEN Book Transport ELSE Select Carrier
2. IF Exception? THEN Manage Exceptions ELSE Track In Transit
3. IF Delivery Confirmed? THEN Process Freight Invoice ELSE Manage Exceptions
4. IF Invoice Match? THEN End Process ELSE Exception Resolved

## Expected Outputs
- carrier bookings
- shipping documents
- tracking data
- proof of delivery
- freight invoices

## Business Rules
- Carrier must have active contract before booking
- Dangerous goods require ADR compliance flag on ShippingDocument
- ProofOfDelivery must include timestamp and recipient signature
- FreightInvoice amount must match TransportBooking rate within 2% tolerance

## Exception Handling
- Carrier no-show: trigger Select Carrier again and log performance penalty
- Customs hold: pause Track In Transit and create ExceptionCase with compliance flag
- Delivery address mismatch: require Customer confirmation before Hand Over to Carrier

## Success Criteria
- ProofOfDelivery received with status DELIVERED
- FreightInvoice matched and paid within KPI on-time delivery threshold
- Exception rate below 5% for the shipment

## Compliance Requirements
- customs compliance
- dangerous goods ADR
- GDPR shipment data
- driver regulations