# SOP — Receive Product from Source or Make (MTO)
**Process ID:** SCOR-D2.8
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-10

## Purpose
Process of receiving MTO finished goods from manufacturing or source operations into the deliver staging area with quality verification and inventory update

## Triggers
- ProductionCompletionNotice received from manufacturing
- QualityRelease signal from quality control

## Inputs Required
- production completion notice
- quality release
- finished goods
- packaging verification
- delivery documentation

## Process Steps
1. IF QualityRelease is valid AND PackagingVerification passes THEN proceed to inventory update ELSE quarantine goods
2. IF all inputs present THEN execute quality verification ELSE hold for missing documentation

## Expected Outputs
- received finished goods
- deliver inventory update
- quality acceptance
- staging confirmation

## Business Rules
- Quality verification must complete before DeliverInventory update
- Receive accuracy KPI must be calculated on every receipt transaction
- GDPR compliance required if DeliveryDocumentation contains personal data

## Exception Handling
- Missing QualityRelease: route to exception queue and notify source process SCOR-M2.5
- Failed quality check: reject goods and trigger return to source or rework

## Success Criteria
- StagingConfirmation generated AND DeliverInventory updated AND receive_accuracy >= 99%

## Compliance Requirements
- GxP if pharma
- quality release compliance
- GDPR if personal data