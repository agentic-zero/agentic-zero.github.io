# Integration Guide â€” iso9001_support_agent
**Process:** Support — Resources, Competence and Communication
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iso9001_support_agent.py ./agents/
```

## Basic Usage
```python
from agents.iso9001_support_agent import Iso9001SupportAgentAgent

agent = Iso9001SupportAgentAgent()
result = agent.execute({
    "resource_requirements": your_resource_requirements_data,
    "competence_needs": your_competence_needs_data,
    "infrastructure_inventory": your_infrastructure_inventory_data,
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
- ERP_API
- LMS_export
- HRIS_connector
- DMS_access
- email_log_parser

## Escalation
The agent automatically escalates to human when:
- competence_coverage_rate < 0.95
- ControlledDocument version mismatch
- infrastructure_availability < 0.95
- training overdue >90 days