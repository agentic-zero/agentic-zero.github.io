# Integration Guide — eto_resource_reservation_agent
**Process:** Reserve Resources and Determine Delivery Date (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_resource_reservation_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_resource_reservation_agent import EtoResourceReservationAgentAgent

agent = EtoResourceReservationAgentAgent()
result = agent.execute({
    "project_proposal": your_project_proposal_data,
    "resource_availability": your_resource_availability_data,
    "engineering_capacity": your_engineering_capacity_data,
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
- ERP_resource_api
- planning_system
- subcontractor_db

## Escalation
The agent automatically escalates to human when:
- ResourceAvailability remains insufficient after buffer increase
- GDPR flag active without anonymization possible
- Utilization KPI projected below 0.7