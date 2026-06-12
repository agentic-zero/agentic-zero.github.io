# SOP — Records of Processing Activities (ROPA)
**Process ID:** GDPR-ART30
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-12

## Purpose
Maintenance of records of processing activities including controller and processor obligations, mandatory ROPA content and management of processing records as accountability evidence

## Triggers
- new ProcessingActivity registered
- quarterly compliance review scheduled
- DPA audit notification received

## Inputs Required
- processing activities
- data categories
- purposes
- retention periods
- security measures
- transfers

## Process Steps
1. IF ProcessingActivity involves transfers THEN create TransferMapping
2. IF ROPA completeness KPI < 1.0 THEN trigger update process

## Expected Outputs
- ROPA document
- processing activity records
- transfer mapping
- security measure documentation

## Business Rules
- ROPA_Document must contain all inputs: processing activities, data categories, purposes, retention periods, security measures, transfers
- Update frequency must be logged and >= 1 per quarter for audit readiness
- ROPA must be maintained as accountability evidence per GDPR Art.30

## Exception Handling
- SME with <250 employees and low-risk processing: omit full retention and security details if DPIA not required

## Success Criteria
- ROPA completeness KPI == 1.0
- transfer coverage == 100%
- ROPA_Document exported and timestamped within last 90 days

## Compliance Requirements
- GDPR Art.30 mandatory
- DPA audit readiness
- accountability principle