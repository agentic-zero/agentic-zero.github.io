# SOP — Verify Product (MTO)
**Process ID:** SCOR-S2.3
**Framework:** SCOR | **Domain:** Source
**Generated:** 2026-06-08

## Purpose
Process of verifying MTO received materials against specifications including dimensional checks, material certificates, compliance documentation and batch traceability

## Triggers
- SCOR-S2.2 signals material receipt for MTO order

## Inputs Required
- received materials
- specifications
- material certificates
- compliance requirements
- test equipment

## Process Steps
1. IF dimensional checks pass AND material certificates valid AND compliance requirements met THEN set AcceptanceDecision=accepted ELSE set AcceptanceDecision=rejected

## Expected Outputs
- verification report
- acceptance decision
- certificate of conformance
- traceability records

## Business Rules
- batch_traceability must be recorded for every ReceivedMaterial
- CertificateOfConformance must be generated only when AcceptanceDecision=accepted
- compliance_flags must be checked based on sector_applicability before finalizing VerificationReport

## Exception Handling
- If MaterialCertificate missing then quarantine ReceivedMaterial and trigger supplier notification
- If first-pass acceptance fails then log KPI deviation and route to SCOR-S2.4

## Success Criteria
- AcceptanceDecision=accepted AND TraceabilityRecord complete AND verification cycle time under KPI threshold

## Compliance Requirements
- GxP material verification if pharma
- AS9100 if aerospace
- ISO 9001
- REACH chemical compliance