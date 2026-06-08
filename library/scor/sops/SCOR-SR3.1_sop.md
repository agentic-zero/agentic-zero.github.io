# SOP — Identify Excess Product Return
**Process ID:** SCOR-SR3.1
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of identifying excess or obsolete inventory that can be returned to supplier for credit or exchange

## Triggers
- scheduled inventory review
- receipt of new inventory shipment
- changes in demand forecast

## Inputs Required
- inventory aging reports
- demand forecasts
- supplier return policies
- inventory carrying costs

## Process Steps
1. IF Excess Inventory is identified THEN initiate Return Opportunity Assessment
2. IF Return Opportunity value is above threshold THEN add to Return Priority List
3. IF Inventory Carrying Costs are high THEN prioritize Excess Inventory identification

## Expected Outputs
- excess inventory identification
- return opportunity assessment
- return priority list

## Business Rules
- rule1: Excess Inventory must be identified within a specified timeframe
- rule2: Return Opportunity value must be calculated based on Supplier Return Policy
- rule3: Return Priority List must be updated regularly to reflect changes in Inventory and Demand Forecast

## Exception Handling
- IF no valid Return Policy is found THEN notify Supplier and pause Return Opportunity Assessment
- IF Excess Inventory is perishable and near expiry THEN expedite Return Opportunity Assessment and prioritize return
- IF personal data is involved in Return Process THEN ensure GDPR compliance

## Success Criteria
- excess inventory identification rate is above target
- return opportunity value is above target
- inventory turnover improvement is above target

## Compliance Requirements
- expiry compliance if perishable
- GDPR if personal data
- financial reporting compliance