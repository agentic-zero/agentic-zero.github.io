# SOP — Good Distribution Practice (GDP)
**Process ID:** GXP-GDP
**Framework:** EU GDP Guidelines 2013/C 343/01 | **Domain:** GxP
**Generated:** 2026-06-10

## Purpose
Good Distribution Practice requirements for pharmaceutical distribution including quality system, personnel, premises, documentation, operations, complaints and returns management

## Triggers
- New distribution order received with product specifications and storage requirements
- Scheduled temperature data upload from vehicle IoT device
- Customer complaint or return notification received

## Inputs Required
- product specifications
- storage requirements
- distribution routes
- customer qualifications
- temperature monitoring data

## Process Steps
1. IF temperature > validated_range THEN quarantine batch and log excursion
2. IF customer_qualification_status == false THEN reject order
3. IF complaint_severity == critical THEN initiate recall and notify authority within 24h

## Expected Outputs
- GDP-compliant distribution
- qualification records
- temperature records
- complaint records
- return records

## Business Rules
- All personnel must hold current GDP training certificate before performing operations
- Temperature must be logged every 5 minutes during transit with 0.5C accuracy
- Returns must be physically segregated within 4 hours of receipt
- Documentation retention period minimum 5 years or 1 year after expiry whichever longer

## Exception Handling
- Temperature excursion <30min and <2C deviation: auto-approve with CAPA record
- Emergency delivery to unqualified customer: requires QP-signed deviation and post-delivery audit within 7 days

## Success Criteria
- GDP audit compliance rate >= 98%
- temperature_excursion_rate == 0 for validated shipments
- delivery_quality_rate >= 99.5% with zero critical complaints

## Compliance Requirements
- EU GDP Guidelines 2013
- WHO GDP
- GDPR serialization data
- temperature chain compliance