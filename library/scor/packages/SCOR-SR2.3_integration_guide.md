# Integration Guide — mro_return_authorization_agent
**Process:** Request MRO Return Authorization
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mro_return_authorization_agent.py ./agents/
```

## Basic Usage
```python
from agents.mro_return_authorization_agent import MroReturnAuthorizationAgentAgent

agent = MroReturnAuthorizationAgentAgent()
result = agent.execute({
    "disposition_decision": your_disposition_decision_data,
    "mro_item_data": your_mro_item_data_data,
    "supplier_contact": your_supplier_contact_data,
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
- procurement_database_api
- supplier_database_api
- quality_control_database_api

## Escalation
The agent automatically escalates to human when:
- if supplier denies return authorization
- if credit terms agreement negotiation fails