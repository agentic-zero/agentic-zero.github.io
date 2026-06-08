# SOP — Manage Supply Chain Procurement
**Process ID:** SCOR-E10
**Framework:** SCOR | **Domain:** Enable
**Generated:** 2026-06-08

## Purpose
Process of managing strategic procurement activities including category management, supplier development, spend analysis and procurement policy governance that enables all Source domain processes

## Triggers
- New or updated BusinessRequirement received
- Quarterly scheduled review of SpendUnderManagement KPI
- Related process SCOR-S1.1 or SCOR-E6 completion event

## Inputs Required
- spend data
- supplier market data
- category strategies
- procurement policies
- business requirements

## Process Steps
1. IF SpendUnderManagement < 0.7 THEN initiate category expansion review
2. IF SupplierDevelopmentScore < 60 THEN create SupplierDevelopmentPlan
3. IF savings achieved < target THEN trigger spend analysis audit

## Expected Outputs
- category strategies
- supplier development plans
- spend analytics
- procurement policies
- savings reports

## Business Rules
- ProcurementPolicy must enforce GDPR supplier data handling and anti-corruption checks before any SupplierDevelopmentPlan approval
- All CategoryStrategy outputs require documented compliance with ESG procurement standards and trade compliance
- SavingsReport must be generated from SpendAnalytics with traceable source data

## Exception Handling
- Handle missing SupplierMarketData by falling back to last 12-month historical averages and flagging for manual review within 5 business days
- If anti-corruption flag is raised, pause all related CategoryStrategy approvals until compliance sign-off

## Success Criteria
- Savings achieved >= 8% of baseline spend
- Procurement cycle time <= 30 days
- SpendUnderManagement >= 85%

## Compliance Requirements
- GDPR supplier data
- anti-corruption regulations
- EU AI Act procurement AI
- trade compliance
- ESG procurement standards