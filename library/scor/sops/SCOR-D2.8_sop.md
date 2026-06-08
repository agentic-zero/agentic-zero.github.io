# SOP — Receive Product from Source or Make (MTO)
**Process ID:** SCOR-D2.8
**Framework:** SCOR | **Domain:** Deliver
**Generated:** 2026-06-07

## Purpose
Process of receiving MTO finished goods from manufacturing or source operations into the deliver staging area with quality verification and inventory update

## Triggers
- Receipt of ProductionCompletionNotice with matching finished goods physical arrival

## Inputs Required
- production completion notice
- quality release
- finished goods
- packaging verification
- delivery documentation

## Process Steps
1. IF QualityRelease.status == 'valid' AND PackagingVerification.result == 'pass' THEN generate QualityAcceptance ELSE route to hold queue

## Expected Outputs
- received finished goods
- deliver inventory update
- quality acceptance
- staging confirmation

## Business Rules
- All inputs (production completion notice, quality release, packaging verification, delivery documentation) must be present and non-null before staging confirmation
- QualityAcceptance must be issued before DeliverInventory update is committed

## Exception Handling
- PackagingVerification fails: reject shipment and create exception record with failure code
- Missing QualityRelease: hold goods in quarantine and notify source process SCOR-M2.5

## Success Criteria
- QualityAcceptance issued
- DeliverInventory updated with 100% accuracy
- StagingConfirmation generated within receive cycle time KPI

## Compliance Requirements
- GxP if pharma
- quality release compliance
- GDPR if personal data