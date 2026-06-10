# SOP — Support — Resources, Competence and Communication
**Process ID:** ISO9001-7
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Management of resources including people, infrastructure, environment, monitoring resources, organizational knowledge, competence, awareness, communication and documented information

## Triggers
- new ResourceRequirement submitted via ERP API
- scheduled quarterly competence review
- infrastructure inventory update event

## Inputs Required
- resource requirements
- competence needs
- infrastructure inventory
- communication needs
- document control requirements

## Process Steps
1. IF competence_gap > 0 THEN create TrainingRecord
2. IF infrastructure_availability < 0.95 THEN trigger ResourceAllocation
3. IF document_control_compliance == false THEN block ControlledDocument release

## Expected Outputs
- resource allocation
- training records
- competence assessments
- controlled documents
- communication plans

## Business Rules
- competence_coverage_rate >= 0.9 required for process sign-off
- all TrainingRecord entries must include completion_date and assessor_id
- ControlledDocument must retain version history and retention_period per GDPR
- infrastructure_availability must be logged daily

## Exception Handling
- IF sector == 'pharma' THEN add additional validation_signature to TrainingRecord
- IF GDPR_employee_data_flag == true THEN anonymize personal fields in CompetenceAssessment before storage

## Success Criteria
- competence_coverage_rate >= 0.9
- training_completion_rate >= 0.95
- document_control_compliance == true
- infrastructure_availability >= 0.98

## Compliance Requirements
- ISO 9001:2015 Clause 7
- GDPR employee data
- document retention requirements