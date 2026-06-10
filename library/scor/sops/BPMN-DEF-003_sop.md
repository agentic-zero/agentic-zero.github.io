# SOP — Configuration Management
**Process ID:** BPMN-DEF-003
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
Configuration management process for complex products including baseline establishment, change control, status accounting and configuration audits

## Triggers
- Configuration Baseline Established event from product design release

## Inputs Required
- product design
- BOM
- drawings
- specifications
- change requests

## Process Steps
1. IF ChangeAuthorized == true THEN execute ControlChanges ELSE reject ChangeRequest
2. IF BaselineImpact == true THEN update ConfigurationBaseline ELSE record status only
3. IF AuditPassed == true THEN end with AuditComplete ELSE initiate corrective action
4. IF DocumentationComplete == true THEN UpdateDocumentation ELSE return to Engineering lane

## Expected Outputs
- configuration baseline
- as-built records
- configuration status
- audit reports

## Business Rules
- All ConfigurationItem must have unique identifier and version per MIL-HDBK-61B
- ChangeRequest requires approval from Customer/Authority lane before baseline update
- Configuration accuracy rate must be >= 99% for defense sector
- Every baseline change must produce ConfigurationStatusRecord within 24 hours

## Exception Handling
- If audit fails, route to Engineering lane for rework and re-audit within 5 business days
- If unauthorized change detected, freeze baseline and notify Quality lane immediately

## Success Criteria
- ConfigurationUpdated end event reached with configuration accuracy rate >= 99% and documentation completeness == 100%
- AuditComplete end event reached with AuditPassed == true

## Compliance Requirements
- MIL-HDBK-61B
- AS9100 configuration management
- CMII standards
- export control