# Integration Guide — excess_product_return_agent
**Process:** Identify Excess Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_product_return_agent.py ./agents/
```

## Basic Usage
```python
from agents.excess_product_return_agent import ExcessProductReturnAgentAgent

agent = ExcessProductReturnAgentAgent()
result = agent.execute({
    "inventory_aging_reports": your_inventory_aging_reports_data,
    "demand_forecasts": your_demand_forecasts_data,
    "supplier_return_policies": your_supplier_return_policies_data,
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
- ERP_system_API
- forecasting_tool_API
- supplier_contract_database

## Escalation
The agent automatically escalates to human when:
- if no valid return policy is found
- if excess inventory is perishable and near expiry
- if personal data is involved in return process