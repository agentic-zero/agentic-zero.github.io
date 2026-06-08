# SOP — Verify Engineer-to-Order Product
**Process ID:** SCOR-S3.3
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of verifying custom-engineered parts against engineering drawings, specifications and contractual requirements including dimensional inspection, material testing and functional validation

## Triggers
- Receipt of ETO_Component lot with complete engineering package in ERP

## Inputs Required
- ETO components
- engineering drawings
- specifications
- test procedures
- contractual requirements

## Process Steps
1. IF all dimensional measurements within tolerance THEN proceed to material testing ELSE create Non_Conformance_Report
2. IF material test results match Specification THEN proceed to functional validation ELSE create Non_Conformance_Report
3. IF functional validation passes contractual requirements THEN set Acceptance_Decision=accepted ELSE set Acceptance_Decision=rejected

## Expected Outputs
- verification report
- first article inspection results
- acceptance decision
- non-conformance reports

## Business Rules
- All ETO_Components must complete dimensional inspection before material testing
- First_Article_Inspection_Result must be generated for every new ETO part per AS9100
- Non_Conformance_Report must include root cause and disposition within 24 hours of detection

## Exception Handling
- Missing engineering drawings: halt process and request from engineering within 4 hours
- NADCAP-required test fails: escalate to quality manager and pause lot acceptance

## Success Criteria
- Acceptance_Decision=accepted
- engineering_specification_compliance_rate >= 98 percent
- inspection_cycle_time <= target_hours

## Compliance Requirements
- AS9100 first article inspection
- defense acquisition
- NADCAP if aerospace
- GDPR if personal data