# Integration Guide — mto_shipment_routing_agent
**Process:** Route Shipments (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_shipment_routing_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_shipment_routing_agent import MtoShipmentRoutingAgentAgent

agent = MtoShipmentRoutingAgentAgent()
result = agent.execute({
    "load_plans": your_load_plans_data,
    "delivery_requirements": your_delivery_requirements_data,
    "carrier_options": your_carrier_options_data,
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
- carrier_booking_api
- customs_compliance_system
- routing_optimization_engine
- load_plan_listener

## Escalation
The agent automatically escalates to human when:
- Carrier booking accuracy drops below 98%
- Customs clearance rate falls below 90%