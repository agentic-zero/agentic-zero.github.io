# Integration Guide â€” transport_management_agent
**Process:** Transport Management
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp transport_management_agent.py ./agents/
```

## Basic Usage
```python
from agents.transport_management_agent import TransportManagementAgentAgent

agent = TransportManagementAgentAgent()
result = agent.execute({
    "shipment_orders": your_shipment_orders_data,
    "carrier_contracts": your_carrier_contracts_data,
    "route_data": your_route_data_data,
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
- ERP_event_listener
- carrier_booking_API
- route_tracking_service
- compliance_engine

## Escalation
The agent automatically escalates to human when:
- no carrier after 3 attempts
- invoice mismatch >2%
- GDPR breach or customs hold detected