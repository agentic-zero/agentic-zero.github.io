# SOP — 8D Problem Solving
**Process ID:** IATF16949-8D
**Framework:** IATF 16949:2016 | **Domain:** IATF 16949
**Generated:** 2026-06-10

## Purpose
8 Disciplines problem solving methodology for automotive quality issues from team formation through root cause identification, corrective actions, verification and prevention of recurrence

## Triggers
- CustomerComplaint received
- DefectData exceeds control limits
- Recurrence detected from KPI_RecurrenceRate

## Inputs Required
- customer complaint
- defect data
- process data
- product samples
- historical incidents

## Process Steps
1. IF root cause identification rate < 0.9 THEN extend RootCauseAnalysis
2. IF corrective action effectiveness < 0.95 THEN trigger new 8D cycle
3. IF recurrence rate > 0.02 THEN escalate to related process IATF16949-APQP

## Expected Outputs
- 8D report
- containment actions
- root cause analysis
- corrective actions
- preventive actions
- lessons learned

## Business Rules
- Team must be formed within 24 hours of CustomerComplaint receipt
- All outputs must be logged in EightDReport before closure
- CorrectiveAction must reduce recurrence rate below KPI threshold
- Compliance with IATF 16949:2016 and customer 8D requirements mandatory

## Exception Handling
- Missing ProductSample: proceed with DefectData and ProcessData only and flag data gap in EightDReport
- HistoricalIncident unavailable: skip and document in LessonsLearned

## Success Criteria
- EightDReport status = closed
- KPI_8D_CycleTime <= target
- KPI_RootCauseRate >= 0.95
- KPI_RecurrenceRate <= 0.01 for 90 days

## Compliance Requirements
- IATF 16949:2016
- customer 8D requirements
- VDA problem solving
- AIAG CQI standards