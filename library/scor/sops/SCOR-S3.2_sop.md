# SOP — Receive Engineer-to-Order Product
**Process ID:** SCOR-S3.2
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of receiving custom-engineered components and materials with full engineering documentation, test reports and compliance certificates for ETO production

## Triggers
- Physical arrival of ETO_Delivery at receiving dock
- Electronic notification of ETO_Delivery with attached documents

## Inputs Required
- ETO delivery
- engineering drawings
- test reports
- certificates
- receiving inspection plan

## Process Steps
1. IF all certificates present and valid THEN proceed to inspection ELSE quarantine and request missing documents
2. IF first-pass inspection passes THEN generate Engineering_Acceptance_Report ELSE trigger rework or rejection workflow

## Expected Outputs
- received ETO components
- engineering acceptance report
- inventory update
- project BOM update

## Business Rules
- All ETO_Delivery items require matching engineering drawings, test reports and certificates before acceptance
- Receiving cycle time must be logged with timestamp at each step for KPI calculation
- Export control compliance flag must be checked for defense and aerospace sector_applicability

## Exception Handling
- Missing certificates: hold item in quarantine and notify engineering within 4 hours
- Documentation mismatch: reject delivery and create exception report linked to supplier

## Success Criteria
- ETO receiving accuracy equals 100 percent
- engineering documentation completeness equals 100 percent
- first-pass acceptance rate meets or exceeds target KPI

## Compliance Requirements
- defense acquisition standards
- AS9100 aerospace
- GDPR if personal data
- export control compliance