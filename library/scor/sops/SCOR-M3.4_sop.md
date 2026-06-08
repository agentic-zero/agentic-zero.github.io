# SOP — Package (ETO)
**Process ID:** SCOR-M3.4
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of packaging ETO products for delivery including export packaging, preservation treatment, technical documentation packaging and marking per contract requirements

## Triggers
- Receipt of ETO finished products from SCOR-M3.3 with status 'complete'
- Availability of signed contract packaging requirements

## Inputs Required
- ETO finished products
- contract packaging requirements
- export requirements
- preservation specifications
- documentation packages

## Process Steps
1. IF Sector == 'defense' THEN apply MIL-SPEC packaging and set Compliance_Flag
2. IF Export_Requirement contains dangerous_goods THEN apply IATA/IMO labeling and special containment
3. IF contract packaging requirements specify preservation THEN execute Preservation_Specification before final sealing

## Expected Outputs
- packaged ETO products
- technical documentation packages
- export markings
- packaging records

## Business Rules
- All contract packaging requirements must be validated before packaging starts
- Export markings must match destination country regulations
- Documentation_Package must be included inside and outside the shipping container
- Packaging cycle time must be logged for KPI calculation

## Exception Handling
- Missing contract packaging requirements: halt process and trigger procurement exception workflow
- Dangerous goods without proper classification: escalate to compliance officer before proceeding

## Success Criteria
- packaging_specification_compliance == 100%
- documentation_completeness == true
- preservation_effectiveness test passed
- Packaging_Record created and linked to contract_id

## Compliance Requirements
- MIL-SPEC packaging if defense
- export control marking
- dangerous goods
- contract-specific packaging