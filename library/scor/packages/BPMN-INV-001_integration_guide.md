# Integration Guide — inventory_replenishment_agent
**Process:** Inventory Management & Replenishment
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp inventory_replenishment_agent.py ./agents/
```

## Basic Usage
```python
from agents.inventory_replenishment_agent import InventoryReplenishmentAgentAgent

agent = InventoryReplenishmentAgentAgent()
result = agent.execute({
    "inventory_levels": your_inventory_levels_data,
    "demand_forecast": your_demand_forecast_data,
    "lead_times": your_lead_times_data,
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
- ERP_stock_api
- demand_forecasting_module
- supplier_management_system
- purchase_order_generator

## Escalation
The agent automatically escalates to human when:
- CriticalStock below safety threshold
- approval rejection or ERP timeout
- no preferred supplier available