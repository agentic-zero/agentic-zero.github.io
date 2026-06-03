# Integration Guide — production_order_release_agent
**Process:** Release Production
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp production_order_release_agent.py ./agents/
```

## Basic Usage
```python
from agents.production_order_release_agent import ProductionOrderReleaseAgentAgent

agent = ProductionOrderReleaseAgentAgent()
result = agent.execute({
    "production_schedules": your_production_schedules_data,
    "work_orders": your_work_orders_data,
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
- ERP system API
- production scheduling software
- inventory management system

## Escalation
The agent automatically escalates to human when:
- if production schedule is delayed by more than 24 hours
- if material requirement cannot be fulfilled within 48 hours
- if inventory levels are outside acceptable ranges