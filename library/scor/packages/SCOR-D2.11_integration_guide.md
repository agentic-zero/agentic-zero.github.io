# Integration Guide — load_vehicle_generate_shipping_docs_agent
**Process:** Load Vehicle and Generate Shipping Docs (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp load_vehicle_generate_shipping_docs_agent.py ./agents/
```

## Basic Usage
```python
from agents.load_vehicle_generate_shipping_docs_agent import LoadVehicleGenerateShippingDocsAgentAgent

agent = LoadVehicleGenerateShippingDocsAgentAgent()
result = agent.execute({
    "packed_shipments": your_packed_shipments_data,
    "load_plan": your_load_plan_data,
    "carrier_vehicle": your_carrier_vehicle_data,
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
- warehouse_system_api
- planning_system
- compliance_database
- documentation_module
- carrier_system

## Escalation
The agent automatically escalates to human when:
- documentation incomplete
- capacity exceeded
- loading accuracy < 100%