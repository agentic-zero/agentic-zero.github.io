# Integration Guide — production_scheduler_agent
**Process:** Schedule Production
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp production_scheduler_agent.py ./agents/
```

## Basic Usage
```python
from agents.production_scheduler_agent import ProductionSchedulerAgentAgent

agent = ProductionSchedulerAgentAgent()
result = agent.execute({
    "production_plans": your_production_plans_data,
    "inventory_data": your_inventory_data_data,
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
- ERP system API
- inventory management system API
- production planning system API
- CRM system API

## Escalation
The agent automatically escalates to human when:
- equipment failure
- material shortages
- insufficient production capacity