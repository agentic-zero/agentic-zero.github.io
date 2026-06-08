# Integration Guide — mto_delivery_scheduler
**Process:** Schedule Product Deliveries (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_delivery_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.mto_delivery_scheduler import MtoDeliverySchedulerAgent

agent = MtoDeliverySchedulerAgent()
result = agent.execute({
    "production_orders": your_production_orders_data,
    "supplier_lead_times": your_supplier_lead_times_data,
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
- ERP_production_order_API
- supplier_portal_capacity_API
- MES_production_start_API
- logistics_transport_schedule_API

## Escalation
The agent automatically escalates to human when:
- Missing production_order data flagged for planner
- Lead time variance >10% or ExpediteAlert volume exceeds threshold
- Transportation delay >4h after automated reschedule attempt