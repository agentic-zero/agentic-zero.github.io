# Integration Guide — production_confirmation_agent
**Process:** Confirm Production
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp production_confirmation_agent.py ./agents/
```

## Basic Usage
```python
from agents.production_confirmation_agent import ProductionConfirmationAgentAgent

agent = ProductionConfirmationAgentAgent()
result = agent.execute({
    "production_orders": your_production_orders_data,
    "material_requirements": your_material_requirements_data,
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
- ERP_System_API
- Inventory_Management_System_API
- Quality_Control_System_API

## Escalation
The agent automatically escalates to human when:
- Production order is incomplete
- Material requirements are not met
- Inventory records update fails