# Integration Guide — mro_work_order_agent
**Process:** Maintenance Work Order Management (MRO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mro_work_order_agent.py ./agents/
```

## Basic Usage
```python
from agents.mro_work_order_agent import MroWorkOrderAgentAgent

agent = MroWorkOrderAgentAgent()
result = agent.execute({
    "breakdown_alert": your_breakdown_alert_data,
    "pm_schedule": your_pm_schedule_data,
    "equipment_history": your_equipment_history_data,
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
- cmms_api
- asset_registry
- procurement_system
- sensor_event_bus

## Escalation
The agent automatically escalates to human when:
- repair not feasible -> EquipmentDecommissioned
- parts unavailable after 3 attempts -> engineering review
- missing GxP flag on pharma equipment