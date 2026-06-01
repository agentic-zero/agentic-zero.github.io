# SOP — Identify, Prioritize and Aggregate Supply Chain Requirements
**Process ID:** SCOR-P1.1
**Framework:** SCOR | **Domain:** Plan
**Generated:** 2026-06-01

## Purpose
Process of collecting and prioritizing demand signals across the supply chain

## Triggers
- new demand signals are received
- inventory data is updated
- capacity data is updated

## Inputs Required
- demand signals
- inventory data
- capacity data

## Process Steps
1. IF demand signals exceed capacity data THEN prioritize demand signals
2. IF inventory data is low THEN adjust demand plan

## Expected Outputs
- supply chain requirements
- demand plan

## Business Rules
- rule1: supply chain requirements must be aggregated across the supply chain
- rule2: demand plan must be updated based on forecast accuracy
- rule3: planning cycle time must be minimized

## Exception Handling
- exception1: if demand signals are missing, use historical data as a fallback
- exception2: if capacity data is unavailable, use alternative capacity planning methods

## Success Criteria
- supply chain requirements are accurately identified and prioritized
- demand plan is generated and updated successfully
- forecast accuracy is within acceptable limits

## Compliance Requirements
- GxP if pharma
- GDP if distribution