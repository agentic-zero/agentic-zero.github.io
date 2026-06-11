# SOP — MEASURE — AI Risk Analysis and Metrics
**Process ID:** NIST-MEASURE
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Analyzing and assessing AI risks using quantitative and qualitative methods including trustworthiness metrics, bias measurement, robustness testing and performance benchmarking

## Triggers
- New AI_System_Output batch received
- Scheduled quarterly robustness testing
- EU AI Act performance metrics request

## Inputs Required
- AI system outputs
- test datasets
- performance benchmarks
- bias indicators
- robustness test results

## Process Steps
1. IF bias_measurement > 0.15 THEN generate compliance_flag
2. IF measurement_coverage < 0.8 THEN request additional Test_Dataset
3. IF metric_reliability < 0.9 THEN rerun Robustness_Test_Result

## Expected Outputs
- risk metrics
- trustworthiness scores
- bias measurements
- robustness reports
- performance benchmarks

## Business Rules
- All outputs must include NIST AI RMF 1.0 MEASURE compliance_flag
- Compute at least 4 KPIs per process execution
- Map every input to at least one output entity

## Exception Handling
- Missing Test_Dataset: skip Bias_Measurement and log warning
- Automation_potential < 0.5: require human review before producing Risk_Metric

## Success Criteria
- All 4 KPIs exceed defined thresholds
- Risk_Metric and Trustworthiness_Score generated for 100% of inputs
- Robustness_Report produced within SLA

## Compliance Requirements
- NIST AI RMF 1.0 MEASURE
- EU AI Act performance metrics
- ISO 42001 evaluation