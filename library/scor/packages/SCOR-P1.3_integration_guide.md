# Integration Guide — supply_chain_inventory_manager
**Process:** Determine Supply Chain Inventory Policy
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_inventory_manager.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_inventory_manager import SupplyChainInventoryManagerAgent

agent = SupplyChainInventoryManagerAgent()
result = agent.execute({
    "demand_plan": your_demand_plan_data,
    "supply_chain_requirements": your_supply_chain_requirements_data,
    "inventory_data": your_inventory_data_data,
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
- warehouse_management_system_api
- sales_forecast_api
- supplier_contract_parser

## Escalation
The agent automatically escalates to human when:
- inventory_turnover_exceeds_target_range
- stockout_rate_exceeds_threshold
- supply_chain_disruption_detected