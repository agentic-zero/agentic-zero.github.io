# SOP — GOVERN — AI Risk Culture and Accountability
**Process ID:** NIST-GOVERN
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Establishing organizational practices for AI risk management including policies, processes, accountability structures and culture that enable trustworthy AI development and deployment

## Triggers
- organizational_ai_strategy update event
- new regulatory_context addition
- quarterly KPI review schedule

## Inputs Required
- organizational AI strategy
- risk appetite
- stakeholder requirements
- regulatory context
- ethical principles

## Process Steps
1. IF Regulatory_Context changes THEN trigger AI_Policy update and recompute Policy_Adherence_Rate
2. IF Accountability_Coverage < 1.0 THEN require new Role_Responsibility assignment

## Expected Outputs
- AI risk governance framework
- accountability structures
- AI policies
- roles and responsibilities
- AI culture indicators

## Business Rules
- GOVERN_Process must produce AI_Risk_Governance_Framework before any MAP process execution
- All AI_Policy must reference at least one Ethical_Principle
- Governance_Maturity_Score must be recalculated quarterly using defined KPIs

## Exception Handling
- Low-risk AI systems may use reduced Accountability_Structure with documented justification and approval from Risk_Appetite owner

## Success Criteria
- Governance_Maturity_Score >= 0.8
- Accountability_Coverage == 1.0
- Policy_Adherence_Rate >= 0.95

## Compliance Requirements
- NIST AI RMF 1.0 GOVERN
- ISO 42001 alignment
- EU AI Act governance