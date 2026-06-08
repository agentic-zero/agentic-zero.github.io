# SOP — Package (MTO)
**Process ID:** SCOR-M2.4
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of packaging MTO finished products according to customer requirements and specifications including labeling, marking, protective packaging and compliance documentation

## Triggers
- Completion signal from SCOR-M2.3 with finished_product_id
- Customer order release containing packaging specifications

## Inputs Required
- finished products
- customer packaging specifications
- labeling requirements
- packaging materials
- shipping requirements

## Process Steps
1. IF sector == 'pharma' THEN enforce GxP packaging and add ComplianceFlag
2. IF ShippingRequirement contains 'dangerous_goods' THEN apply IATA/ADR packaging rules
3. IF customer_spec_adherence < 1.0 THEN trigger rework before shipment

## Expected Outputs
- packaged products
- customer-specific labels
- packaging records
- packing lists

## Business Rules
- All CustomerSpecificLabel must match LabelingRequirement exactly
- Packaging cycle time must be logged in PackagingRecord
- Environmental packaging regulations must be checked before material selection

## Exception Handling
- Missing customer specs: halt process and request clarification from order management
- Material shortage: substitute only with documented approval and update PackagingRecord

## Success Criteria
- packaging_accuracy == 1.0
- labeling_compliance_rate == 1.0
- PackingList matches PackagedProduct contents exactly

## Compliance Requirements
- GxP packaging if pharma
- dangerous goods packaging regulations
- customer packaging standards
- environmental packaging regulations