# Integration Guide — mto_shipment_router
**Process:** Route Shipments (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_shipment_router.py ./agents/
```

## Basic Usage
```python
from agents.mto_shipment_router import MtoShipmentRouterAgent

agent = MtoShipmentRouterAgent()
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
- load_plan_api
- carrier_booking_system
- customs_clearance_db
- optimization_engine
- export_control_checker

## Escalation
The agent automatically escalates to human when:
- export control restriction detected
- customs_clearance_rate < 0.95
- no valid CarrierOption within CostConstraint