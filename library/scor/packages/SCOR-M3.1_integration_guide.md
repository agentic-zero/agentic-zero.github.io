# Integration Guide — eto_production_scheduler
**Process:** Schedule Engineer-to-Order Production Activities
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_production_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.eto_production_scheduler import EtoProductionSchedulerAgent

agent = EtoProductionSchedulerAgent()
result = agent.execute({
    "engineering_releases": your_engineering_releases_data,
    "project_schedules": your_project_schedules_data,
    "resource_plans": your_resource_plans_data,
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
- engineering_system_api
- plm_source_connector
- erp_resource_module
- project_schedule_integration

## Escalation
The agent automatically escalates to human when:
- unresolved design change after 48 hours
- schedule adherence KPI < 0.9
- design change impact KPI exceeds threshold