# SOP — 8D Problem Solving
**Process ID:** IATF16949-8D
**Framework:** IATF 16949:2016 | **Domain:** IATF 16949
**Generated:** 2026-06-10

## Purpose
8 Disciplines problem solving methodology for automotive quality issues from team formation through root cause identification, corrective actions, verification and prevention of recurrence

## Triggers
- customer complaint received
- internal defect data threshold exceeded
- historical incident recurrence detected

## Inputs Required
- customer complaint
- defect data
- process data
- product samples
- historical incidents

## Process Steps
1. IF root cause verified by data analysis THEN proceed to CorrectiveAction design
2. IF verification shows recurrence rate > 0 THEN return to RootCause analysis
3. IF containment effectiveness < 100% THEN escalate containment scope

## Expected Outputs
- 8D report
- containment actions
- root cause analysis
- corrective actions
- preventive actions
- lessons learned

## Business Rules
- 8DReport must be completed within KPI cycle time target
- Every RootCause must have at least one data-backed verification method
- CorrectiveAction must include owner, due date and effectiveness metric before closure
- LessonLearned must be linked to at least one related_process

## Exception Handling
- Customer complaint lacks defect samples: log exception and use historical incidents for initial analysis within 24 hours
- Root cause not identifiable after two analysis cycles: escalate to cross-functional review board and extend timeline with documented approval

## Success Criteria
- 8D cycle time <= target KPI
- recurrence rate = 0 for 90 days post-closure
- VerificationResult confirms corrective_action_effectiveness >= 95%

## Compliance Requirements
- IATF 16949:2016
- customer 8D requirements
- VDA problem solving
- AIAG CQI standards