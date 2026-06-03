# SOP — Conduct Supplier Audits and Assessments
**Process ID:** SCOR-S1.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-03

## Purpose
Process of conducting supplier audits and assessments to ensure compliance and quality

## Triggers
- Scheduled Audit date is reached
- New Supplier is onboarded

## Inputs Required
- supplier information
- audit schedules
- assessment criteria

## Process Steps
1. IF Audit Report indicates non-compliance THEN trigger corrective action
2. IF Assessment Result indicates low quality THEN trigger supplier development

## Expected Outputs
- audit reports
- assessment results

## Business Rules
- rule1: Audit must be conducted according to schedule
- rule2: Assessment must be based on predefined criteria
- rule3: Audit Report and Assessment Result must be documented and stored

## Exception Handling
- IF Supplier is not available for Audit THEN reschedule Audit
- IF Assessment Criteria are not defined THEN use industry standard criteria

## Success Criteria
- Audit completion rate is above 90%
- Assessment score is above 80%

## Compliance Requirements
- GxP if pharma
- GDP if distribution