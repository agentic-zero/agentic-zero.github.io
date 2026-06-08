# Integration Guide — mto_order_consolidation_agent
**Process:** Consolidate Orders (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_order_consolidation_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_order_consolidation_agent import MtoOrderConsolidationAgentAgent

agent = MtoOrderConsolidationAgentAgent()
result = agent.execute({
    "confirmed_orders": your_confirmed_orders_data,
    "delivery_schedules": your_delivery_schedules_data,
    "customer_shipping_preferences": your_customer_shipping_preferences_data,
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
- order_management_api
- delivery_schedule_service
- logistics_cost_calculator
- notification_gateway
- customs_regulation_checker

## Escalation
The agent automatically escalates to human when:
- customs consolidation regulations violated
- dangerous goods without hazmat certification
- mismatched delivery windows >48h