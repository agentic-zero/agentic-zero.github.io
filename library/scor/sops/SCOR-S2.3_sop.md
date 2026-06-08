# SOP — Verify Product (MTO)
**Process ID:** SCOR-S2.3
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-07

## Purpose
Process of verifying MTO received materials against specifications including dimensional checks, material certificates, compliance documentation and batch traceability

## Triggers
- ERP goods receipt event for MTO purchase order line item
- TestEquipment scan of ReceivedMaterial batch_id

## Inputs Required
- received materials
- specifications
- material certificates
- compliance requirements
- test equipment

## Process Steps
1. IF dimensional checks pass AND material certificates match THEN set AcceptanceDecision=ACCEPT
2. IF compliance_requirements unmet THEN set AcceptanceDecision=REJECT and trigger quarantine
3. IF traceability completeness < 100% THEN request additional batch records before finalizing VerificationReport

## Expected Outputs
- verification report
- acceptance decision
- certificate of conformance
- traceability records

## Business Rules
- All ReceivedMaterial must have matching material certificates before verification starts
- Verification cycle time must be logged for every batch
- CertificateOfConformance requires signature and timestamp for ISO 9001 compliance
- GxP material verification mandatory if sector=pharma

## Exception Handling
- Missing material certificates: pause process and request supplier documents within 24h
- Dimensional deviation within tolerance: log as conditional accept with engineering sign-off
- AS9100 aerospace lot: enforce 100% traceability or escalate to SCOR-S2.4

## Success Criteria
- AcceptanceDecision=ACCEPT
- first-pass acceptance rate >= 95%
- traceability completeness = 100%
- VerificationReport generated and CertificateOfConformance issued within KPI cycle time

## Compliance Requirements
- GxP material verification if pharma
- AS9100 if aerospace
- ISO 9001
- REACH chemical compliance