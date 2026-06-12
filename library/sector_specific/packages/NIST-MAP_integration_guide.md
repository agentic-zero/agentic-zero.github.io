# Integration Guide â€” ai_risk_context_mapper
**Process:** MAP — AI Risk Context and Categorization
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp ai_risk_context_mapper.py ./agents/
```

## Basic Usage
```python
from agents.ai_risk_context_mapper import AiRiskContextMapperAgent

agent = AiRiskContextMapperAgent()
result = agent.execute({
    "ai_use_case_descriptions": your_ai_use_case_descriptions_data,
    "stakeholder_map": your_stakeholder_map_data,
    "impact_categories": your_impact_categories_data,
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
- ontology_engine
- risk_database_api
- compliance_validator

## Escalation
The agent automatically escalates to human when:
- automation_potential < 0.6 requires manual approval on ImpactAssessment
- source confidence < 0.9 invalidates AIRiskCategory assignments