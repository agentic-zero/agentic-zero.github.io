# Integration Guide — mto_packaging_agent
**Process:** Package (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_packaging_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_packaging_agent import MtoPackagingAgentAgent

agent = MtoPackagingAgentAgent()
result = agent.execute({
    "finished_products": your_finished_products_data,
    "customer_packaging_specifications": your_customer_packaging_specifications_data,
    "labeling_requirements": your_labeling_requirements_data,
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
- inventory_api
- labeling_system
- compliance_engine
- packaging_execution_interface
- record_repository

## Escalation
The agent automatically escalates to human when:
- Missing customer packaging specifications
- Insufficient packaging materials after procurement trigger