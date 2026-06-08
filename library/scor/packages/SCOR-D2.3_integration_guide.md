# Integration Guide — mto_resource_reservation_agent
**Process:** Reserve Resources and Determine Delivery Date (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_resource_reservation_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_resource_reservation_agent import MtoResourceReservationAgentAgent

agent = MtoResourceReservationAgentAgent()
result = agent.execute({
    "validated_order": your_validated_order_data,
    "capacity_availability": your_capacity_availability_data,
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
- capacity_management_api
- inventory_system
- routing_engine
- logistics_scheduler

## Escalation
The agent automatically escalates to human when:
- material shortage escalate to SCOR-S2.1
- capacity conflict with SCOR-M2.1 prioritize by commitment_reliability
- input validation failure or overcommitment risk