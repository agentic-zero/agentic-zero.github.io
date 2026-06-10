# Integration Guide â€” transfer_eto_product_agent
**Process:** Transfer Engineer-to-Order Product
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp transfer_eto_product_agent.py ./agents/
```

## Basic Usage
```python
from agents.transfer_eto_product_agent import TransferEtoProductAgentAgent

agent = TransferEtoProductAgentAgent()
result = agent.execute({
    "verified_eto_components": your_verified_eto_components_data,
    "project_work_orders": your_project_work_orders_data,
    "configuration_management_data": your_configuration_management_data_data,
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
- configuration_management_system
- compliance_checker
- inventory_update_service

## Escalation
The agent automatically escalates to human when:
- Missing configuration data: notify configuration manager and hold transfer
- Export control flag active: require dual authorization before staging