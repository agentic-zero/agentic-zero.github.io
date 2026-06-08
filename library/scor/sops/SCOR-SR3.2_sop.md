# SOP — Disposition Excess Product
**Process ID:** SCOR-SR3.2
**Framework:** SCOR | **Domain:** Return
**Generated:** 2026-06-07

## Purpose
Process of determining optimal disposition for excess inventory including return to supplier, liquidation, donation or write-off

## Triggers
- Excess Inventory threshold exceeded
- Product nearing expiry or end of shelf life
- Supplier return terms change

## Inputs Required
- excess inventory list
- product condition
- market value
- supplier return terms
- liquidation options

## Process Steps
1. IF Product Condition is good AND Market Value is high THEN consider liquidation
2. IF Supplier Return Terms are favorable THEN consider return to supplier
3. IF Product Condition is poor THEN consider write-off or donation

## Expected Outputs
- disposition decision
- financial impact assessment
- action plan

## Business Rules
- rule1: Disposition Decision must be made within a reasonable timeframe to minimize losses
- rule2: Financial Impact Assessment must consider recovery value rate, disposition cycle time, and write-off reduction
- rule3: Action Plan must comply with expiry and shelf life compliance, financial write-off policy, and environmental regulations if disposal

## Exception Handling
- IF Product is hazardous THEN handle disposal according to environmental regulations
- IF Supplier Return Terms are unclear THEN escalate to supplier management
- IF Disposition Decision is disputed THEN escalate to senior management

## Success Criteria
- Disposition Decision is made and implemented within a reasonable timeframe
- Financial Impact Assessment is completed and recovery value rate is optimized
- Action Plan is executed and write-off reduction is achieved

## Compliance Requirements
- expiry and shelf life compliance
- financial write-off policy
- environmental if disposal