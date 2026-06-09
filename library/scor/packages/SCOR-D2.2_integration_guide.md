# Integration Guide — mto_order_validation_agent
**Process:** Receive, Configure, Enter and Validate MTO Order
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_order_validation_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_order_validation_agent import MtoOrderValidationAgentAgent

agent = MtoOrderValidationAgentAgent()
result = agent.execute({
    "customer_order": your_customer_order_data,
    "product_configurator": your_product_configurator_data,
    "capacity_data": your_capacity_data_data,
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
- crm_api
- product_configurator_api
- mes_capacity_api
- planning_leadtime_api
- erp_pricing_api

## Escalation
The agent automatically escalates to human when:
- invalid configuration options
- capacity overload detected
- validation cycle exceeds 4 hours