# SOP — Receive Product from Source or Make (MTO)
**Process ID:** SCOR-D2.8
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-10

## Purpose
Process of receiving MTO finished goods from manufacturing or source operations into the deliver staging area with quality verification and inventory update

## Triggers
- ProductionCompletionNotice received
- QualityRelease issued

## Inputs Required
- production completion notice
- quality release
- finished goods
- packaging verification
- delivery documentation

## Process Steps
1. IF QualityRelease.status == 'approved' AND PackagingVerification.passed == true THEN create QualityAcceptance ELSE route to quality hold

## Expected Outputs
- received finished goods
- deliver inventory update
- quality acceptance
- staging confirmation

## Business Rules
- inventory_accuracy must be >= 99.5%
- receive_cycle_time must be <= 4 hours
- quality_acceptance_rate must be >= 98%
- apply GxP audit trail if sector == 'pharma'

## Exception Handling
- IF FinishedGoods.quantity != expected_quantity THEN create discrepancy record and hold staging
- IF GDPR applies and personal_data present THEN anonymize before DeliverInventoryUpdate

## Success Criteria
- DeliverInventoryUpdate committed with inventory_accuracy >= 99.5%
- StagingConfirmation timestamp recorded within receive_cycle_time SLA
- QualityAcceptance issued

## Compliance Requirements
- GxP if pharma
- quality release compliance
- GDPR if personal data