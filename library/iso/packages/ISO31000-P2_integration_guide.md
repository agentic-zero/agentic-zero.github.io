# Integration Guide â€” iso31000_risk_assessment_agent
**Process:** Risk Assessment Process
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iso31000_risk_assessment_agent.py ./agents/
```

## Basic Usage
```python
from agents.iso31000_risk_assessment_agent import Iso31000RiskAssessmentAgentAgent

agent = Iso31000RiskAssessmentAgentAgent()
result = agent.execute({
    "risk_sources": your_risk_sources_data,
    "event_data": your_event_data_data,
    "consequence_data": your_consequence_data_data,
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
- risk_database_api
- event_listener_service
- control_inventory_api
- scheduler_service

## Escalation
The agent automatically escalates to human when:
- Update delay exceeds 24-hour rule
- Missing likelihood/consequence after expert default attempt
- Empty controls inventory detected