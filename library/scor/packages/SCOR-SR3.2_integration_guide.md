# Integration Guide — excess_product_disposition_agent
**Process:** Disposition Excess Product
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp excess_product_disposition_agent.py ./agents/
```

## Basic Usage
```python
from agents.excess_product_disposition_agent import ExcessProductDispositionAgentAgent

agent = ExcessProductDispositionAgentAgent()
result = agent.execute({
    "excess_inventory_list": your_excess_inventory_list_data,
    "product_condition": your_product_condition_data,
    "market_value": your_market_value_data,
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
- inventory_management_system_api
- market_research_api
- supplier_contract_database

## Escalation
The agent automatically escalates to human when:
- if product is hazardous
- if supplier return terms are unclear
- if disposition decision is disputed