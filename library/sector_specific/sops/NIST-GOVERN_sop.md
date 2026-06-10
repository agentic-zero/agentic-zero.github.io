# SOP — GOVERN — AI Risk Culture and Accountability
**Process ID:** NIST-GOVERN
**Framework:** NIST AI RMF 1.0 | **Domain:** NIST AI RMF
**Generated:** 2026-06-10

## Purpose
Establishing organizational practices for AI risk management including policies, processes, accountability structures and culture that enable trustworthy AI development and deployment

## Triggers
- new organizational_ai_strategy published
- regulatory_context updated
- annual governance review date reached

## Inputs Required
- organizational AI strategy
- risk appetite
- stakeholder requirements
- regulatory context
- ethical principles

## Process Steps
1. IF RegulatoryContext contains EU_AI_Act THEN add EU_AI_Act_governance compliance flag to AIPolicies
2. IF automation_potential < 0.5 THEN require manual review of AccountabilityStructures

## Expected Outputs
- AI risk governance framework
- accountability structures
- AI policies
- roles and responsibilities
- AI culture indicators

## Business Rules
- PolicyAdherenceRate must be calculated quarterly from audit logs
- AccountabilityCoverage must map every AIPolicy to at least one named role
- GovernanceMaturityScore must be updated after each policy change

## Exception Handling
- If sector_applicability excludes defense then skip defense-specific accountability structures
- If source confidence < 0.9 then flag output for human validation before publishing AIRiskGovernanceFramework

## Success Criteria
- GovernanceMaturityScore >= 0.8
- PolicyAdherenceRate >= 0.95
- all roles mapped to at least one AIPolicy

## Compliance Requirements
- NIST AI RMF 1.0 GOVERN
- ISO 42001 alignment
- EU AI Act governance