# Integration Guide â€” eto_production_schedule_agent
**Process:** Schedule Engineer-to-Order Production Activities
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_production_schedule_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_production_schedule_agent import EtoProductionScheduleAgentAgent

agent = EtoProductionScheduleAgentAgent()
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
- project_management_software
- resource_planning_tool
- compliance_checker

## Escalation
The agent automatically escalates to human when:
- ITAR flag active with non-US subcontractor
- design change frequency >3 per week
- schedule_adherence_pct <80% or milestone delay >10 days