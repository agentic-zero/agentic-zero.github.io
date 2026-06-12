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
- external_risk_feeds_api
- risk_database
- calculation_engine

## Escalation
The agent automatically escalates to human when:
- likelihood * consequence > 12
- control effectiveness < 0.6
- incomplete inputs or stale controls detected