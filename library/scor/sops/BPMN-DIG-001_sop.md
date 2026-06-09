# SOP — AI-Powered Demand Sensing & Forecasting
**Process ID:** BPMN-DIG-001
**Framework:**  | **Domain:** BPMN
**Generated:** 2026-06-09

## Purpose
AI-powered demand sensing process from signal ingestion to forecast publication including ML model execution, consensus override and automated plan update

## Triggers
- NewDataAvailable event with timestamp and data_batch_id

## Inputs Required
- POS data
- orders
- market signals
- social data
- weather data
- promotions
- historical sales

## Process Steps
1. IF DataQualityOK == false THEN re-execute CleanseAndValidateData
2. IF ModelConfidence >= 0.85 THEN proceed to GenerateStatisticalForecast ELSE trigger ManualOverride
3. IF OverrideRequired == true THEN route to ConsensusReview
4. IF Approved == true THEN execute PublishToPlanningSystems ELSE return to ApplyMarketIntelligence

## Expected Outputs
- AI demand forecast
- confidence intervals
- bias report
- planning system update

## Business Rules
- GDPR_Art22: require human review for automated decisions affecting individuals
- EU_AI_Act: log model confidence and bias for every forecast
- ForecastAccuracyMAPE must be computed on last 13 weeks holdout
- ConsensusCycleTime must be under 48 hours

## Exception Handling
- ModelConfidence < 0.7: force manual override and log exception code EX-MC-LOW
- DataQualityOK == false after 3 retries: halt process and alert data engineering team
- ConsensusReview timeout > 72 hours: auto-approve with flag EX-CONS-TIMEOUT

## Success Criteria
- ForecastPublished status == true
- MAPE <= 0.18 on validation set
- PlanningSystemUpdate timestamp recorded within 4 hours of approval

## Compliance Requirements
- GDPR AI automated decisions Art.22
- EU AI Act transparency
- data privacy