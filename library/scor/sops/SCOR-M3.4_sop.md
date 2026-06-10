# SOP — Package (ETO)
**Process ID:** SCOR-M3.4
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-10

## Purpose
Process of packaging ETO products for delivery including export packaging, preservation treatment, technical documentation packaging and marking per contract requirements

## Triggers
- Receipt of ETOFinishedProduct with linked ContractPackagingRequirement
- Completion signal from SCOR-M3.3

## Inputs Required
- ETO finished products
- contract packaging requirements
- export requirements
- preservation specifications
- documentation packages

## Process Steps
1. IF sector == defense THEN apply MIL-SPEC packaging
2. IF export_controlled THEN add export_control marking
3. IF dangerous_goods THEN apply special preservation and labeling
4. IF contract_specific_packaging THEN override default specs

## Expected Outputs
- packaged ETO products
- technical documentation packages
- export markings
- packaging records

## Business Rules
- All packaging must comply with contract packaging requirements
- Preservation treatment must meet preservation specifications
- Technical documentation must be complete per documentation packages
- Markings must satisfy export requirements

## Exception Handling
- Dangerous goods: route to certified hazmat packaging handler before standard process
- Missing contract requirements: halt and trigger procurement exception workflow
- Failed preservation test: reprocess and log in PackagingRecord

## Success Criteria
- packaging_specification_compliance == true
- documentation_completeness == 1.0
- PackagingRecord created with all outputs
- ExportMarking verified

## Compliance Requirements
- MIL-SPEC packaging if defense
- export control marking
- dangerous goods
- contract-specific packaging