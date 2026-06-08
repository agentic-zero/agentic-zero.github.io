# Integration Guide — mro_return_shipment_scheduler
**Process:** Schedule MRO Return Shipment
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mro_return_shipment_scheduler.py ./agents/
```

## Basic Usage
```python
from agents.mro_return_shipment_scheduler import MroReturnShipmentSchedulerAgent

agent = MroReturnShipmentSchedulerAgent()
result = agent.execute({
    "mro_return_authorization": your_mro_return_authorization_data,
    "item_quantity_and_weight": your_item_quantity_and_weight_data,
    "supplier_location": your_supplier_location_data,
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
- logistics_api
- carrier_booking_api
- documentation_generation_tool

## Escalation
The agent automatically escalates to human when:
- No carrier options are available
- Incomplete return documentation
- MRO return authorization is not approved