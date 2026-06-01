# SOP — Determine Supply Chain Transportation Policy
**Process ID:** SCOR-P1.4
**Framework:** SCOR | **Domain:** Plan
**Generated:** 2026-06-01

## Purpose
Process of determining transportation policy to meet demand and minimize costs

## Triggers
- schedule: transportation policy review and update on a quarterly basis
- event: changes to demand plan or supply chain requirements
- threshold: transportation cost or on-time delivery rate exceeds predefined thresholds

## Inputs Required
- demand plan
- supply chain requirements
- transportation data

## Process Steps
1. IF demand plan changes THEN re-evaluate transportation policy
2. IF supply chain requirements change THEN update transportation policy
3. IF transportation data indicates carrier underperformance THEN consider alternative carriers

## Expected Outputs
- transportation policy
- carrier selection

## Business Rules
- rule1: transportation policy must meet supply chain requirements
- rule2: carrier selection must be based on transportation data and supply chain requirements
- rule3: transportation policy must be reviewed and updated regularly to ensure compliance with sector-specific regulations (e.g. GxP, GDP)

## Exception Handling
- exception1: if transportation data is incomplete or inaccurate, use historical data or industry benchmarks as a fallback
- exception2: if carrier selection is constrained by supply chain requirements, prioritize compliance over cost or efficiency considerations

## Success Criteria
- transportation cost is within 5% of budget
- on-time delivery rate exceeds 95%
- carrier selection meets supply chain requirements and transportation policy

## Compliance Requirements
- GxP if pharma
- GDP if distribution