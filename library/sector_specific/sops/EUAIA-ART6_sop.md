# SOP — High-Risk AI System Classification
**Process ID:** EUAIA-ART6
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Classification rules for high-risk AI systems including Annex I (safety components) and Annex III (high-risk use cases) covering supply chain, employment, critical infrastructure and other regulated domains

## Triggers
- New AI system description and use case submitted via EUAIA-ART6 endpoint

## Inputs Required
- AI system description
- use case definition
- sector classification
- intended purpose
- Annex III criteria

## Process Steps
1. IF AI_System matches Annex_I safety component OR Annex_III criteria THEN SET high_risk=true
2. IF sector in ['pharma','defense','automotive'] AND intended_purpose involves critical infrastructure THEN escalate to L2 review

## Expected Outputs
- risk classification decision
- high-risk determination
- compliance pathway
- documentation requirements

## Business Rules
- Must evaluate all Annex_III criteria before final classification
- High-risk determination requires explicit documentation of Annex reference
- Classification accuracy KPI must exceed 0.95 per review cycle

## Exception Handling
- If AI system is explicitly excluded under Art.6(3) then bypass high-risk label and log exclusion reason

## Success Criteria
- Risk classification decision output with high_risk boolean and compliance_pathway string
- Review cycle time under 4 hours
- Appeals rate below 5%

## Compliance Requirements
- EU AI Act Art.6
- Annex I safety components
- Annex III high-risk use cases