# Integration Guide — mto_shipment_dispatch_agent
**Process:** Ship Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_shipment_dispatch_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_shipment_dispatch_agent import MtoShipmentDispatchAgentAgent

agent = MtoShipmentDispatchAgentAgent()
result = agent.execute({
    "loaded_vehicle": your_loaded_vehicle_data,
    "shipping_documents": your_shipping_documents_data,
    "tracking_systems": your_tracking_systems_data,
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
- carrier_api
- tracking_system
- notification_service
- compliance_engine
- order_system

## Escalation
The agent automatically escalates to human when:
- customs_export_compliance failure to compliance_officer
- secondary_carrier handover failure within 2h
- notification_failure from invalid customer_email