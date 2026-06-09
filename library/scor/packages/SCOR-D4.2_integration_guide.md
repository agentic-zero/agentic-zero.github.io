# Integration Guide — store_product_receiving_agent
**Process:** Receive Product at Store
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp store_product_receiving_agent.py ./agents/
```

## Basic Usage
```python
from agents.store_product_receiving_agent import StoreProductReceivingAgentAgent

agent = StoreProductReceivingAgentAgent()
result = agent.execute({
    "delivery_schedule": your_delivery_schedule_data,
    "purchase_orders": your_purchase_orders_data,
    "delivered_products": your_delivered_products_data,
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
- handheld_scanner_api
- temperature_sensor
- edi_delivery_schedule
- erp_purchase_order
- store_inventory_system

## Escalation
The agent automatically escalates to human when:
- quantity mismatch >5%
- failed quality inspection
- cold chain violation
- barcode scan failure requiring supervisor override