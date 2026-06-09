# Integration Guide — order_to_cash_autonomous_agent
**Process:** Order-to-Cash
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp order_to_cash_autonomous_agent.py ./agents/
```

## Basic Usage
```python
from agents.order_to_cash_autonomous_agent import OrderToCashAutonomousAgentAgent

agent = OrderToCashAutonomousAgentAgent()
result = agent.execute({
    "customer_order": your_customer_order_data,
    "inventory_data": your_inventory_data_data,
    "credit_data": your_credit_data_data,
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
- CRM_API
- ERP_inventory_API
- credit_scoring_service
- payment_gateway
- shipping_API
- invoice_generator

## Escalation
The agent automatically escalates to human when:
- any decision point false or task exceeds 48h
- automation_complexity exceeds LOW or FTE > 5