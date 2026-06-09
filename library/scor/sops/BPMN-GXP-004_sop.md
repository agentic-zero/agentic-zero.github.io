# SOP — Validation & Qualification (CSV/Equipment)
**Process ID:** BPMN-GXP-004
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Computer system validation and equipment qualification process from validation planning through IQ/OQ/PQ execution to validation report and periodic review

## Triggers
- ValidationRequest event received from Management or Users lane

## Inputs Required
- user requirements
- risk assessment
- validation protocols
- test scripts
- system documentation

## Process Steps
1. IF RiskLevel == HIGH THEN execute full DQ/IQ/OQ/PQ ELSE reduced scope
2. IF IQPassed == false THEN route to ValidationFailed and trigger deviation
3. IF OQPassed == false THEN route to ValidationFailed and trigger deviation
4. IF PQPassed == false THEN route to ValidationFailed and trigger deviation
5. IF all qualifications passed AND QA approved THEN SystemValidated

## Expected Outputs
- validation plan
- IQ/OQ/PQ reports
- validation summary report
- validated system

## Business Rules
- All protocols must be approved by QualityAssurance_Lane before execution
- Test scripts must be 21 CFR Part 11 and EU Annex 11 compliant
- RiskAssessment must be documented per GAMP 5 and ICH Q10
- First-time pass rate KPI must be recorded after each qualification
- Validation cycle time must be logged from ValidationRequest to ValidationReport

## Exception Handling
- Any protocol deviation during IQ/OQ/PQ routes to ValidationFailed and requires CAPA before re-execution
- Missing UserRequirementsSpecification blocks progression past RiskAssessment
- ERP integration failure with Veeva Vault or MasterControl requires manual fallback and audit log entry

## Success Criteria
- All gateways (IQPassed, OQPassed, PQPassed) evaluate true
- ValidationReport approved by QualityAssurance and Management
- SystemValidated end event reached with no open deviations

## Compliance Requirements
- 21 CFR Part 11
- EU Annex 11
- GAMP 5
- ICH Q10
- ISO 13485