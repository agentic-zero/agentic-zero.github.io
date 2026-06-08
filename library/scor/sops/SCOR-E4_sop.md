# SOP — Manage Supply Chain Human Resources
**Process ID:** SCOR-E4
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-08

## Purpose
Process of managing supply chain workforce including skills development, capacity planning, performance management and knowledge transfer to support autonomous operations

## Triggers
- new workforce_data received from HRIS
- quarterly skills_requirements update published
- performance_data batch available from ERP

## Inputs Required
- workforce data
- skills requirements
- training plans
- performance data
- organizational structure

## Process Steps
1. IF skills_coverage_rate < 0.85 THEN create new TrainingProgram
2. IF training_completion_rate < 0.9 THEN escalate to capacity replanning
3. IF GDPR employee data flag = true THEN anonymize before storage

## Expected Outputs
- skills inventory
- training programs
- capacity plans
- performance assessments
- knowledge base

## Business Rules
- labor_law_compliance: validate all capacity plans against local working hour limits before approval
- EU_AI_Act_Art14: require human oversight sign-off on any automated performance assessment
- health_safety_regulations: block deployment of workforce to tasks without valid certification

## Exception Handling
- missing workforce data: pause process and request update from HR source within 48 hours
- non-compliant training plan: reject and route to compliance review before execution

## Success Criteria
- skills_coverage_rate >= 0.9
- training_completion_rate >= 0.95
- knowledge_retention_rate >= 0.85 measured at 90 days

## Compliance Requirements
- GDPR employee data
- labor law compliance
- EU AI Act Art.14 human oversight
- health and safety regulations