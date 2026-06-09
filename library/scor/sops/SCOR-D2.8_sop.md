# SOP — Receive Product from Source or Make (MTO)
**Process ID:** SCOR-D2.8
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-08

## Purpose
Process of receiving MTO finished goods from manufacturing or source operations into the deliver staging area with quality verification and inventory update

## Triggers
- ProductionCompletionNotice received AND FinishedGoods physically arrive at deliver staging area

## Inputs Required
- production completion notice
- quality release
- finished goods
- packaging verification
- delivery documentation

## Process Steps
1. IF QualityRelease.status == 'approved' AND PackagingVerification.result == 'pass' THEN proceed to QualityAcceptance ELSE hold for exception handling
2. IF DeliveryDocumentation.complete == true THEN update DeliverInventory ELSE request missing docs

## Expected Outputs
- received finished goods
- deliver inventory update
- quality acceptance
- staging confirmation

## Business Rules
- QualityRelease must be present before QualityAcceptance is issued
- DeliverInventory.accuracy must be verified within receive_cycle_time SLA
- All FinishedGoods must have packaging_verification before staging_confirmation

## Exception Handling
- PackagingVerification fails: reject FinishedGoods, log defect, notify source process SCOR-M2.5
- Missing QualityRelease: place goods in quality_hold status and trigger compliance alert

## Success Criteria
- QualityAcceptance issued
- DeliverInventory updated with 100% accuracy
- StagingConfirmation timestamp recorded
- All KPIs (receive_accuracy, quality_acceptance_rate) exceed threshold

## Compliance Requirements
- GxP if pharma
- quality release compliance
- GDPR if personal data