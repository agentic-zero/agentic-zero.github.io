# Integration Guide — eto_product_transfer_agent
**Process:** Transfer Engineer-to-Order Product
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_product_transfer_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_product_transfer_agent import EtoProductTransferAgentAgent

agent = EtoProductTransferAgentAgent()
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
- configuration_management_api
- export_control_checker
- traceability_logger
- inventory_system_api
- staging_plan_validator

## Escalation
The agent automatically escalates to human when:
- export_control_violation_or_hold
- missing_verified_eto_status
- traceability_loss_or_mismatch
- gdpr_personal_data_without_consent