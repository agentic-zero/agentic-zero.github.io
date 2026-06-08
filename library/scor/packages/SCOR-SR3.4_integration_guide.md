# Integration Guide — excess_return_shipment_scheduler
**Process:** Schedule Excess Product Return Shipment
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_return_shipment_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.excess_return_shipment_scheduler import ExcessReturnShipmentSchedulerAgent

agent = ExcessReturnShipmentSchedulerAgent()
result = agent.execute({
    "excess_return_authorization": your_excess_return_authorization_data,
    "product_quantity": your_product_quantity_data,
    "storage_location": your_storage_location_data,
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
- inventory_storage_system
- compliance_validation_engine

## Escalation
The agent automatically escalates to human when:
- no valid CarrierOption available
- expiry date within 7 days
- cross-border customs mismatch