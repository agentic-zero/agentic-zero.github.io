# Integration Guide — supply_chain_optimizer_agent
**Process:** Identify, Prioritize and Aggregate Supply Chain Requirements
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_optimizer_agent.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_optimizer_agent import SupplyChainOptimizerAgentAgent

agent = SupplyChainOptimizerAgentAgent()
result = agent.execute({
    "demand_signals": your_demand_signals_data,
    "inventory_data": your_inventory_data_data,
    "capacity_data": your_capacity_data_data,
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
- demand_forecasting_system_api
- inventory_management_system_api
- capacity_planning_system_api

## Escalation
The agent automatically escalates to human when:
- when forecast accuracy is not within acceptable limits
- when demand signals exceed capacity data