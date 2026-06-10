# SOP — Package (ETO)
**Process ID:** SCOR-M3.4
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-10

## Purpose
Process of packaging ETO products for delivery including export packaging, preservation treatment, technical documentation packaging and marking per contract requirements

## Triggers
- Receipt of ETOFinishedProduct from SCOR-M3.3
- Availability of ContractPackagingRequirement and DocumentationPackage

## Inputs Required
- ETO finished products
- contract packaging requirements
- export requirements
- preservation specifications
- documentation packages

## Process Steps
1. IF sector == 'defense' THEN apply MIL-SPEC packaging and set ComplianceFlag='MIL-SPEC packaging if defense'
2. IF ExportRequirement contains dangerous_goods THEN apply special handling and set ComplianceFlag='dangerous goods'
3. IF contract_packaging_requirements exist THEN enforce contract-specific packaging and set ComplianceFlag='contract-specific packaging'

## Expected Outputs
- packaged ETO products
- technical documentation packages
- export markings
- packaging records

## Business Rules
- All PackagedETOProduct must include export control marking when ExportRequirement.export_control == true
- DocumentationPackage must be complete before PackagingRecord is created
- PreservationSpecification must be applied to ETOFinishedProduct prior to final packaging
- Packaging cycle time must be logged in PackagingRecord

## Exception Handling
- IF preservation treatment fails effectiveness check THEN reapply treatment and increment packaging cycle time KPI
- IF export marking non-compliant THEN hold shipment and trigger compliance review

## Success Criteria
- packaging_specification_compliance == 1.0
- documentation_completeness == 1.0
- PackagingRecord created with all required fields
- ExportMarking applied per ExportRequirement

## Compliance Requirements
- MIL-SPEC packaging if defense
- export control marking
- dangerous goods
- contract-specific packaging