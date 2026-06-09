# SOP — Non-Conformance & CAPA Management
**Process ID:** BPMN-QMS-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Non-conformance detection through CAPA closure process including detection, containment, root cause analysis, corrective action implementation and effectiveness verification

## Triggers
- Non-Conformance Detected event from product data or customer complaints

## Inputs Required
- non-conformance report
- product data
- process data
- regulatory requirements
- customer complaints

## Process Steps
1. IF SafetyIssue == true THEN escalate to Management lane
2. IF RootCauseFound == false THEN loop to RootCauseAnalysis
3. IF ActionsEffective == false THEN return to DefineCorrectiveActions
4. IF RegulatoryReportable == true THEN create RegulatoryNotification within 24h

## Expected Outputs
- CAPA record
- containment actions
- corrective actions
- effectiveness data
- regulatory notifications

## Business Rules
- CAPA must close only after EffectivenessVerification passes
- All pharma sector CAPAs require GxP compliance flag
- Regulatory notifications must meet FDA 21 CFR and EU GMP timelines
- Recurrence rate KPI must be calculated per product batch

## Exception Handling
- Escalate to Management if SafetyIssue detected or CAPA cycle time exceeds 90 days
- If RootCauseAnalysis fails after 3 iterations, auto-create Management review task

## Success Criteria
- CAPA status == Closed AND effectiveness_score >= 0.8 AND recurrence_rate == 0 within 180 days

## Compliance Requirements
- GxP CAPA if pharma
- ISO 9001 corrective action
- FDA 21 CFR
- EU GMP
- IATF 16949 automotive