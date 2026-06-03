# SOP — Conduct Supplier Audits and Assessments
**Process ID:** SCOR-S1.5
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-03

## Purpose
Process of conducting supplier audits and assessments to ensure compliance and quality

## Triggers
- scheduled audit date
- supplier information update
- assessment criteria change

## Inputs Required
- supplier information
- audit schedules
- assessment criteria

## Process Steps
1. IF Audit Report indicates non-compliance THEN trigger corrective action
2. IF Assessment Result indicates low quality THEN trigger supplier evaluation

## Expected Outputs
- audit reports
- assessment results

## Business Rules
- rule1: Supplier must comply with GxP regulations if in pharma sector
- rule2: Supplier must comply with GDP regulations if in distribution sector
- rule3: Audit must be conducted according to scheduled timeline

## Exception Handling
- exception1: Supplier is unable to provide required documentation, THEN request additional information
- exception2: Audit Report is incomplete, THEN trigger audit re-evaluation

## Success Criteria
- Audit Report indicates compliance
- Assessment Result indicates high quality
- Audit completion rate meets target

## Compliance Requirements
- GxP if pharma
- GDP if distribution