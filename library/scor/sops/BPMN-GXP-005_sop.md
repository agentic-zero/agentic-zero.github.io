# SOP — Regulatory Submission Management
**Process ID:** BPMN-GXP-005
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Regulatory submission preparation and lifecycle management from dossier compilation to agency approval including variations, renewals and post-approval changes

## Triggers
- Submission Triggered event received from regulatory planning system with submission_type and target_agency

## Inputs Required
- clinical data
- quality data
- manufacturing data
- regulatory guidelines
- submission templates

## Process Steps
1. IF Complete? == true THEN proceed to Prepare Submission ELSE return to Compile Dossier
2. IF Agency Query? == true THEN execute Respond to Queries ELSE Track Status
3. IF Approved? == true THEN Implement Approval ELSE handle Submission Rejected

## Expected Outputs
- regulatory dossier
- agency submission
- approval certificate
- label update

## Business Rules
- Dossier must conform to ICH CTD format before Submit to Agency
- All submissions require 21 CFR Part 11 compliant electronic signatures
- Query response time must not exceed KPI threshold of 10 business days
- GDPR consent flags must be validated on all clinical data inputs

## Exception Handling
- IF Submission Rejected THEN log rejection reason and trigger Major Variation review within 5 days
- IF dossier quality score < 85 THEN route back to Quality Review with mandatory Medical Affairs sign-off

## Success Criteria
- Approval Received end event fired with approval_certificate attached and label_update published to ERP

## Compliance Requirements
- ICH CTD format
- FDA 21 CFR
- EMA regulations
- GDPR clinical data