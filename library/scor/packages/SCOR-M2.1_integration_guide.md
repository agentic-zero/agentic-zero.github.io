# Integration Guide — mto_production_scheduler
**Process:** Schedule Make-to-Order Production Activities
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_production_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.mto_production_scheduler import MtoProductionSchedulerAgent

agent = MtoProductionSchedulerAgent()
result = agent.execute({
    "customer_orders": your_customer_orders_data,
    "capacity_plans": your_capacity_plans_data,
    "material_availability": your_material_availability_data,
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
- ERP_API
- WMS_API
- PLM_API
- MES_API

## Escalation
The agent automatically escalates to human when:
- material shortage hold and escalate to procurement
- rush priority=1 order requires documented capacity override approval
- equipment downtime >2h triggers reschedule within 4h