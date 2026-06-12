# Integration Guide â€” eu_ai_act_risk_classifier
**Process:** High-Risk AI System Classification
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eu_ai_act_risk_classifier.py ./agents/
```

## Basic Usage
```python
from agents.eu_ai_act_risk_classifier import EuAiActRiskClassifierAgent

agent = EuAiActRiskClassifierAgent()
result = agent.execute({
    "ai_system_description": your_ai_system_description_data,
    "use_case_definition": your_use_case_definition_data,
    "sector_classification": your_sector_classification_data,
})
print(result['outputs'])
```

## Supported Systems
- SAP ECC
- SAP S/4HANA
- SAP EWM
- Oracle ERP Cloud
- Oracle JDE

## Tools Required
- annex_criteria_checker
- sector_intent_validator
- legal_reference_api

## Escalation
The agent automatically escalates to human when:
- sector in pharma/defense/automotive with critical infrastructure
- annex_iii_match incomplete
- classification confidence below threshold