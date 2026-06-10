# Integration Guide â€” eto_delivery_scheduler
**Process:** Schedule Engineer-to-Order Product Deliveries
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_delivery_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.eto_delivery_scheduler import EtoDeliverySchedulerAgent

agent = EtoDeliverySchedulerAgent()
result = agent.execute({
    "project_schedules": your_project_schedules_data,
    "engineering_boms": your_engineering_boms_data,
    "supplier_engineering_lead_times": your_supplier_engineering_lead_times_data,
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
- project_management_system_api
- plm_system_api
- supplier_portal
- erp_system

## Escalation
The agent automatically escalates to human when:
- Missing SupplierEngineeringLeadTime after 48h
- ITAR/EAR restricted item detected
- schedule_variance >10% unresolvable automatically