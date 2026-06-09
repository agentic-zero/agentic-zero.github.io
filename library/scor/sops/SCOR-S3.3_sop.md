# SOP — Verify Engineer-to-Order Product
**Process ID:** SCOR-S3.3
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of verifying custom-engineered parts against engineering drawings, specifications and contractual requirements including dimensional inspection, material testing and functional validation

## Triggers
- Receipt of ETO_Component with attached Engineering_Drawing and Contractual_Requirement

## Inputs Required
- ETO components
- engineering drawings
- specifications
- test procedures
- contractual requirements

## Process Steps
1. IF dimensional_tolerance_check == pass AND material_test == pass AND functional_validation == pass THEN Acceptance_Decision = accept ELSE Non_Conformance_Report

## Expected Outputs
- verification report
- first article inspection results
- acceptance decision
- non-conformance reports

## Business Rules
- compliance_rate >= 0.98 for AS9100 first article
- inspection_cycle_time <= 48 hours
- NADCAP certification required if sector == aerospace

## Exception Handling
- IF personal_data_detected THEN apply GDPR redaction before storing Verification_Report

## Success Criteria
- Acceptance_Decision == accept AND first_article_acceptance_rate >= 0.95 AND non_conformance_rate <= 0.02

## Compliance Requirements
- AS9100 first article inspection
- defense acquisition
- NADCAP if aerospace
- GDPR if personal data