# Integration Guide — in_store_picking_agent
**Process:** Pick Product in Store
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp in_store_picking_agent.py ./agents/
```

## Basic Usage
```python
from agents.in_store_picking_agent import InStorePickingAgentAgent

agent = InStorePickingAgentAgent()
result = agent.execute({
    "replenishment_signals": your_replenishment_signals_data,
    "customer_orders": your_customer_orders_data,
    "store_inventory": your_store_inventory_data,
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
- ERP_replenishment_api
- OMS_order_connector
- store_inventory_db
- planogram_service
- mobile_scan_device
- fulfillment_notifier

## Escalation
The agent automatically escalates to human when:
- out_of_stock exception after substitution check
- pick_cycle_time exceeds 30 minutes
- wrong_item detected by scan validation