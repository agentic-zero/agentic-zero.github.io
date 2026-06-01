# SOP — Determine Supply Chain Inventory Policy
**Process ID:** SCOR-P1.3
**Framework:** SCOR | **Domain:** Plan
**Generated:** 2026-06-01

## Purpose
Process of determining inventory policy to meet demand and minimize costs

## Triggers
- new demand plan is released
- supply chain requirements are updated
- inventory levels fall below reorder points

## Inputs Required
- demand plan
- supply chain requirements
- inventory data

## Process Steps
1. IF demand exceeds supply THEN adjust Inventory Policy
2. IF inventory levels are low THEN trigger reorder
3. IF stockout rate is high THEN reevaluate Inventory Policy

## Expected Outputs
- inventory policy
- reorder points

## Business Rules
- rule1: Inventory Policy must balance demand and supply
- rule2: Reorder Points must be based on historical demand and lead time
- rule3: Inventory Turnover must be optimized to minimize costs

## Exception Handling
- IF supply chain disruption occurs THEN manually adjust Inventory Policy
- IF demand forecast is inaccurate THEN reevaluate Inventory Policy
- IF inventory data is incomplete THEN use alternative data sources

## Success Criteria
- inventory turnover is within target range
- stockout rate is below threshold
- reorder points are accurately set

## Compliance Requirements
- GxP if pharma
- GDP if distribution