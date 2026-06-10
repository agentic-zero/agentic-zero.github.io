# SOP — Risk Management System for High-Risk AI
**Process ID:** EUAIA-ART9
**Framework:** EU AI Act 2024 | **Domain:** EU AI Act
**Generated:** 2026-06-10

## Purpose
Mandatory risk management system for high-risk AI systems including risk identification, estimation, evaluation, mitigation and residual risk assessment throughout the AI lifecycle

## Triggers
- new HighRiskAISystem registration in AI inventory
- major design change or new foreseeable misuse identified

## Inputs Required
- AI system design
- intended use
- foreseeable misuse
- risk assessment data
- mitigation measures

## Process Steps
1. IF residual_risk_level > 0.3 THEN require additional MitigationControl before deployment
2. IF risk_identification_completeness < 0.95 THEN trigger re-assessment before lifecycle stage gate

## Expected Outputs
- risk management plan
- risk assessment report
- residual risk acceptance
- mitigation controls
- risk monitoring plan

## Business Rules
- EU_AI_Act_Art9: risk management must cover identification, estimation, evaluation, mitigation and residual risk for entire AI lifecycle
- residual_risk must be explicitly accepted by accountable role before release

## Exception Handling
- non-high-risk AI systems: skip mandatory Art9 process and log exemption justification in compliance registry

## Success Criteria
- risk_identification_completeness >= 0.95
- mitigation_effectiveness >= 0.8
- residual_risk_level <= 0.3
- review_frequency >= quarterly

## Compliance Requirements
- EU AI Act Art.9 mandatory
- ISO 31000 risk management
- NIST AI RMF
- sector-specific risk standards