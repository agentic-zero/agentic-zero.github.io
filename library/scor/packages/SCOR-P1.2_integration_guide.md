# Integration Guide — supply_chain_analyzer
**Process:** Analyze Supply Chain Capabilities and Capacity
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_analyzer.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_analyzer import SupplyChainAnalyzerAgent

agent = SupplyChainAnalyzerAgent()
result = agent.execute({
    "supply_chain_requirements": your_supply_chain_requirements_data,
    "capacity_data": your_capacity_data_data,
    "supplier_data": your_supplier_data_data,
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
- supply_chain_management_system
- data_analytics_api

## Escalation
The agent automatically escalates to human when:
- insufficient_capacity
- supplier_failure
- inaccurate_capacity_plan