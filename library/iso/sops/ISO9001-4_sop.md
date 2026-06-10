# SOP — Context of the Organization
**Process ID:** ISO9001-4
**Framework:** ISO 9001:2015 | **Domain:** ISO 9001
**Generated:** 2026-06-10

## Purpose
Understanding the organization and its context, interested parties, scope of QMS and the QMS itself including processes and their interactions

## Triggers
- scheduled annual review date reached
- major organizational change event logged
- new regulatory requirement published
- customer or certification body request received

## Inputs Required
- strategic direction
- internal issues
- external issues
- stakeholder needs
- regulatory requirements

## Process Steps
1. IF new regulatory requirement identified THEN update ContextAnalysis within 30 days
2. IF stakeholder need impacts QMS scope THEN include in InterestedPartyRegister
3. IF internal issue affects process interactions THEN revise ProcessMap

## Expected Outputs
- QMS scope
- process map
- interested party register
- context analysis

## Business Rules
- All four inputs (strategic direction, internal issues, external issues, stakeholder needs, regulatory requirements) must be documented before ContextAnalysis is approved
- Context review frequency must be at least annually
- QMSScope must explicitly list all exclusions and boundaries

## Exception Handling
- If no regulatory requirements exist, record explicit statement of absence with date and approver
- If organization is startup with <10 employees, stakeholder register may be limited to top 5 parties

## Success Criteria
- QMSScope, ProcessMap, InterestedPartyRegister and ContextAnalysis all generated with non-null values
- scope_completeness >= 0.95
- stakeholder_coverage >= 0.90
- context_review_frequency <= 365 days

## Compliance Requirements
- ISO 9001:2015 Clause 4
- GDPR context analysis
- regulatory landscape