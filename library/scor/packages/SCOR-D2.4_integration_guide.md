# Integration Guide — consolidate_orders_mto_agent
**Process:** Consolidate Orders (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp consolidate_orders_mto_agent.py ./agents/
```

## Basic Usage
```python
from agents.consolidate_orders_mto_agent import ConsolidateOrdersMtoAgentAgent

agent = ConsolidateOrdersMtoAgentAgent()
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
- ERP_order_feed
- logistics_API
- carrier_delivery_feed
- GDPR_compliance_checker

## Escalation
The agent automatically escalates to human when:
- customs regulations violated
- conflicting delivery dates
- missing cost data