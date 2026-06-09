# SOP — Receive Engineer-to-Order Product
**Process ID:** SCOR-S3.2
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of receiving custom-engineered components and materials with full engineering documentation, test reports and compliance certificates for ETO production

## Triggers
- Physical arrival of ETO_Delivery at receiving dock with ASN notification

## Inputs Required
- ETO delivery
- engineering drawings
- test reports
- certificates
- receiving inspection plan

## Process Steps
1. IF all inputs present and certificates valid THEN execute receiving inspection
2. IF first-pass inspection passes THEN generate Engineering_Acceptance_Report ELSE trigger rejection workflow

## Expected Outputs
- received ETO components
- engineering acceptance report
- inventory update
- project BOM update

## Business Rules
- rule1: All ETO_Delivery must include engineering drawings, test reports and certificates before inspection starts
- rule2: Receiving cycle time must be logged for ETO_Receiving_Accuracy_KPI calculation
- rule3: Compliance flags (AS9100, export control) must be checked prior to acceptance

## Exception Handling
- Missing certificates: hold material in quarantine and notify engineering within 4 hours
- Failed inspection: create non-conformance report and route to SCOR-S3.3 for disposition

## Success Criteria
- Engineering_Acceptance_Report generated with first-pass acceptance = true
- Inventory_Update and Project_BOM_Update completed within receiving cycle time SLA

## Compliance Requirements
- defense acquisition standards
- AS9100 aerospace
- GDPR if personal data
- export control compliance