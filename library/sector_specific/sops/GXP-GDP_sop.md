# SOP — Good Distribution Practice (GDP)
**Process ID:** GXP-GDP
**Framework:** EU GDP Guidelines 2013/C 343/01 | **Domain:** GxP
**Generated:** 2026-06-10

## Purpose
Good Distribution Practice requirements for pharmaceutical distribution including quality system, personnel, premises, documentation, operations, complaints and returns management

## Triggers
- New distribution order received from qualified Customer
- Product arrival at warehouse with storage requirements

## Inputs Required
- product specifications
- storage requirements
- distribution routes
- customer qualifications
- temperature monitoring data

## Process Steps
1. IF temperature > Storage_Requirement.max OR temperature < Storage_Requirement.min THEN create Temperature_Record with excursion_flag=true and trigger investigation
2. IF Customer.qualification_status != 'approved' THEN block distribution and log exception

## Expected Outputs
- GDP-compliant distribution
- qualification records
- temperature records
- complaint records
- return records

## Business Rules
- All distribution must maintain temperature within Storage_Requirement range for entire route
- Customer must have valid Qualification_Record before any shipment
- Temperature_Record must be stored for minimum 5 years per EU GDP Guidelines 2013
- Complaint_Record must be created within 24 hours of receipt and linked to batch_id

## Exception Handling
- Temperature excursion: log deviation, quarantine product, notify QA, decide on release/reject within 48 hours
- Return: inspect product integrity, update Return_Record, destroy if compromised or restock only after re-qualification

## Success Criteria
- GDP audit compliance rate == 100%
- temperature excursion rate < 0.5%
- delivery quality rate >= 99.5%
- all Temperature_Record and Qualification_Record created and immutable

## Compliance Requirements
- EU GDP Guidelines 2013
- WHO GDP
- GDPR serialization data
- temperature chain compliance