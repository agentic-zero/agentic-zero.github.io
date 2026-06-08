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
- ERP_CustomerOrder_API
- APS_CapacityPlan
- MRP_MaterialAvailability
- PLM_RoutingData
- ISO_Approval_Workflow
- GxP_Batch_Record_System

## Escalation
The agent automatically escalates to human when:
- material data missing causing loop
- post-release EquipmentSchedule conflict
- pharma sector without GxP record
- capacity_utilization > 0.95