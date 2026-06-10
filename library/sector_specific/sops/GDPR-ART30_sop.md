# SOP — Records of Processing Activities (ROPA)
**Process ID:** GDPR-ART30
**Framework:** GDPR (EU) 2016/679 | **Domain:** GDPR
**Generated:** 2026-06-10

## Purpose
Maintenance of records of processing activities including controller and processor obligations, mandatory ROPA content and management of processing records as accountability evidence

## Triggers
- new processing activity registered in data inventory
- annual compliance review date reached
- DPA audit notification received
- material change to processing purpose or transfer

## Inputs Required
- processing activities
- data categories
- purposes
- retention periods
- security measures
- transfers

## Process Steps
1. IF data is transferred to third country THEN require adequacy decision or SCC documentation
2. IF organization has >250 employees OR processing is high-risk THEN mandatory full ROPA required

## Expected Outputs
- ROPA document
- processing activity records
- transfer mapping
- security measure documentation

## Business Rules
- ROPA must contain name/contact of controller, purposes, data categories, recipients, transfers, retention, security measures
- ROPA must be kept in writing including electronic form
- ROPA must be updated without undue delay when processing changes
- ROPA must be made available to supervisory authority on request

## Exception Handling
- Organizations with <250 employees exempt from ROPA unless processing is likely to result in risk to rights and freedoms or involves special categories

## Success Criteria
- ROPA completeness score >= 95% of mandatory fields populated
- last_updated timestamp <= 90 days
- all cross-border transfers have documented legal basis

## Compliance Requirements
- GDPR Art.30 mandatory
- DPA audit readiness
- accountability principle