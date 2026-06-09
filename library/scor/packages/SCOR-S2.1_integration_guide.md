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
- ERP_production_orders_API
- TMS_transportation_API
- Supplier_master_data_API
- MRP_material_requirements

## Escalation
The agent automatically escalates to human when:
- Missing SupplierConfirmation 48h prior
- lead_time_variance > 2 days
- data_quality alert on absent inputs