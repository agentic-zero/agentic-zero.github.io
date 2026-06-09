# Integration Guide — supply_chain_hr_automator
**Process:** Manage Supply Chain Human Resources
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_hr_automator.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_hr_automator import SupplyChainHrAutomatorAgent

agent = SupplyChainHrAutomatorAgent()
result = agent.execute({
    "workforce_data": your_workforce_data_data,
    "skills_requirements": your_skills_requirements_data,
    "training_plans": your_training_plans_data,
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
- HRIS_API
- ERP_data_connector
- compliance_checker
- org_chart_parser

## Escalation
The agent automatically escalates to human when:
- EU_AI_Act_Art14 human oversight required for automated assessments
- missing workforce data after 48h
- non-compliant training plan detected