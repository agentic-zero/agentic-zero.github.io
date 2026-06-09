# Integration Guide — shelf_stocking_agent
**Process:** Stock Shelf
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp shelf_stocking_agent.py ./agents/
```

## Basic Usage
```python
from agents.shelf_stocking_agent import ShelfStockingAgentAgent

agent = ShelfStockingAgentAgent()
result = agent.execute({
    "received_products": your_received_products_data,
    "planogram_data": your_planogram_data_data,
    "shelf_capacity": your_shelf_capacity_data,
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
- planogram_api
- pricing_erp_interface
- inventory_receiving_system
- shelf_sensors

## Escalation
The agent automatically escalates to human when:
- damaged product received
- pricing data mismatch
- missing planogram data
- fifo violation detected