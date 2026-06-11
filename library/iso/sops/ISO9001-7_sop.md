# SOP — Support — Resources, Competence and Communication
**Process ID:** ISO9001-7
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Management of resources including people, infrastructure, environment, monitoring resources, organizational knowledge, competence, awareness, communication and documented information

## Triggers
- new ResourceRequirement submitted
- annual competence review date reached
- document retention policy expiry
- infrastructure maintenance ticket created

## Inputs Required
- resource requirements
- competence needs
- infrastructure inventory
- communication needs
- document control requirements

## Process Steps
1. IF competence_gap > 0 THEN create TrainingRecord and schedule training
2. IF document_version != latest THEN enforce ControlledDocument update before release
3. IF infrastructure_availability < 0.95 THEN trigger ResourceAllocation review

## Expected Outputs
- resource allocation
- training records
- competence assessments
- controlled documents
- communication plans

## Business Rules
- TrainingRecord.completion_date must be <= 90 days from CompetenceAssessment.date
- ControlledDocument must retain revision history for minimum 7 years per ISO 9001
- CommunicationPlan must log recipient, timestamp and acknowledgment for GDPR traceability
- Competence_coverage_rate = (assessed_employees / total_employees) must be >= 0.95

## Exception Handling
- IF sector == 'pharma' THEN add 21 CFR Part 11 electronic signature validation to ControlledDocument
- IF GDPR_employee_data == true THEN anonymize TrainingRecord.personal_data after 3 years retention

## Success Criteria
- competence_coverage_rate >= 0.95
- training_completion_rate >= 0.98
- document_control_compliance == 100%
- infrastructure_availability >= 0.99

## Compliance Requirements
- ISO 9001:2015 Clause 7
- GDPR employee data
- document retention requirements