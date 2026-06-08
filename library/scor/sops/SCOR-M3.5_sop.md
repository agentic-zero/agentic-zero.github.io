# SOP — Stage Product (ETO)
**Process ID:** SCOR-M3.5
**Framework:** SCOR | **Domain:** Make
**Generated:** 2026-06-07

## Purpose
Process of staging ETO products for delivery including final government/customer inspection, data package completion, export licensing and handover to deliver operations

## Triggers
- receipt of PackagedETOProduct and DataPackage from SCOR-M3.4
- availability of ExportLicense and CustomerInspectionSchedule

## Inputs Required
- packaged ETO products
- data packages
- export licenses
- customer inspection schedule
- delivery documentation

## Process Steps
1. IF export_license.status == 'valid' AND ITAR_compliance == true THEN proceed_to_staging ELSE hold_for_compliance_review
2. IF customer_inspection.result == 'pass' THEN generate DeliveryReadinessConfirmation ELSE initiate_rework

## Expected Outputs
- staged ETO products
- approved data packages
- export clearance
- delivery readiness confirmation

## Business Rules
- export_control: all ExportLicense must validate against ITAR/EAR before ExportClearance issuance
- documentation: DataPackage must contain 100% required fields per government property regulations
- staging: PackagedETOProduct must complete final inspection within staging_cycle_time <= KPI threshold

## Exception Handling
- inspection_failure: if CustomerInspectionPassRate < 100% then route to M3.4 rework and log failure in DeliveryDocumentation
- license_rejection: if ExportLicense invalid then pause process and notify compliance officer with 24h escalation

## Success Criteria
- all outputs produced: StagedETOProduct, ApprovedDataPackage, ExportClearance, DeliveryReadinessConfirmation
- KPIs met: staging_cycle_time <= target, documentation_completeness == 100%, export_compliance_rate >= 99%, customer_inspection_pass_rate >= 95%

## Compliance Requirements
- export control ITAR/EAR
- government property regulations
- defense acquisition
- customs compliance