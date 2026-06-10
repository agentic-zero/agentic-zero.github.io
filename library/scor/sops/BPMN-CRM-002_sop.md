# SOP — After-Sales Service & Field Service
**Process ID:** BPMN-CRM-002
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
After-sales service process from service request to resolution including ticket creation, technician dispatch, parts ordering, on-site service and invoicing

## Triggers
- ServiceRequestReceived event via portal/email/API with required service_request_id and equipment_serial

## Inputs Required
- service request
- equipment data
- service history
- parts inventory
- technician schedule

## Process Steps
1. IF RemoteResolutionPossible == true THEN execute DiagnoseRemotely ELSE execute ScheduleTechnician
2. IF PartsAvailable == true THEN execute DispatchTechnician ELSE execute OrderParts
3. IF UnderWarranty == true THEN skip InvoiceService ELSE execute InvoiceService
4. IF CustomerSatisfied == true THEN execute CloseTicket ELSE reopen ServiceTicket

## Expected Outputs
- service report
- resolved equipment
- invoice
- parts consumption
- customer feedback

## Business Rules
- ServiceTicket.status must transition from Created to Closed only after CustomerSign-off == true
- Technician dispatch requires SLA_compliance check before 24h from ticket creation
- Parts consumption must update inventory in real-time via Parts lane
- All customer data access must log GDPR consent timestamp

## Exception Handling
- Parts unavailable after OrderParts: escalate to procurement lane and extend SLA by 48h
- CustomerSatisfied == false after TestVerify: create follow-up ServiceTicket with same Equipment reference
- Equipment cannot be repaired: trigger EquipmentReplaced end event and archive original ServiceTicket

## Success Criteria
- ServiceTicket.status == Closed
- first_time_fix_rate == true
- SLA_compliance == true
- NPS_score >= 8
- ServiceReport and Invoice both generated

## Compliance Requirements
- safety regulations
- warranty compliance
- GDPR customer data
- export control if defense