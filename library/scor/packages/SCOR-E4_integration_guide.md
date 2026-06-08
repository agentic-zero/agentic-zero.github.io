# Integration Guide — supply_chain_workforce_manager
**Process:** Manage Supply Chain Human Resources
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_workforce_manager.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_workforce_manager import SupplyChainWorkforceManagerAgent

agent = SupplyChainWorkforceManagerAgent()
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
- ERP_performance_connector
- planning_system_interface
- GDPR_anonymizer
- human_oversight_approval_gateway

## Escalation
The agent automatically escalates to human when:
- health_and_safety violation detected
- EU AI Act Art.14 human oversight required on CapacityPlan
- related_process SCOR-E1 unavailable