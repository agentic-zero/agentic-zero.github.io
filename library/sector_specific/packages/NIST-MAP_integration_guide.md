# Integration Guide â€” nist_map_risk_context_mapper
**Process:** MAP — AI Risk Context and Categorization
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp nist_map_risk_context_mapper.py ./agents/
```

## Basic Usage
```python
from agents.nist_map_risk_context_mapper import NistMapRiskContextMapperAgent

agent = NistMapRiskContextMapperAgent()
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
- nist_rmf_schema_validator
- stakeholder_interview_workflow
- impact_scoring_engine
- eu_ai_act_classifier

## Escalation
The agent automatically escalates to human when:
- risk_categorization_coverage < 0.9
- stakeholder_mapping_completeness < 1.0
- impact_assessment_accuracy < 0.85
- zero automation_potential