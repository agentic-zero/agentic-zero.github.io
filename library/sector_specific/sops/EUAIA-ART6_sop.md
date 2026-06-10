# SOP — High-Risk AI System Classification
**Process ID:** EUAIA-ART6
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Classification rules for high-risk AI systems including Annex I (safety components) and Annex III (high-risk use cases) covering supply chain, employment, critical infrastructure and other regulated domains

## Triggers
- New AI system description submitted for classification
- Update to use_case_definition or sector_classification received

## Inputs Required
- AI system description
- use case definition
- sector classification
- intended purpose
- Annex III criteria

## Process Steps
1. IF AI_System matches Annex_I safety component OR Annex_III use case THEN set High_Risk_Determination=true
2. IF sector in ['pharma','defense','manufacturing','chemical','food','automotive','distribution'] AND intended_purpose matches regulated domain THEN trigger full Annex_III evaluation
3. IF High_Risk_Determination=true THEN output Compliance_Pathway and Documentation_Requirements else output low-risk classification

## Expected Outputs
- risk classification decision
- high-risk determination
- compliance pathway
- documentation requirements

## Business Rules
- rule1: Every input AI_System must provide use_case_definition and intended_purpose before classification
- rule2: Classification must evaluate all Annex_III criteria for high-risk use cases
- rule3: Output must include risk_classification_decision and compliance_flags for EU AI Act Art.6
- rule4: Review cycle time KPI must be logged for every classification

## Exception Handling
- Exception: AI system explicitly excluded under EU AI Act Art.2(2) - bypass classification and return non-high-risk with legal reference
- Exception: Incomplete Annex_III criteria provided - return 'insufficient data' and request missing fields before proceeding

## Success Criteria
- High_Risk_Determination is boolean and risk_classification_decision is non-null
- Compliance_Pathway and Documentation_Requirements are populated when high-risk=true
- classification_accuracy KPI >= 0.95 on audit sample

## Compliance Requirements
- EU AI Act Art.6
- Annex I safety components
- Annex III high-risk use cases