# Integration Guide — supply_chain_procurement_agent
**Process:** Manage Supply Chain Procurement
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_procurement_agent.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_procurement_agent import SupplyChainProcurementAgentAgent

agent = SupplyChainProcurementAgentAgent()
result = agent.execute({
    "spend_data": your_spend_data_data,
    "supplier_market_data": your_supplier_market_data_data,
    "category_strategies": your_category_strategies_data,
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
- erp_spend_data_api
- supplier_market_data_feed
- strategy_repository
- compliance_audit_tool

## Escalation
The agent automatically escalates to human when:
- Trade compliance violation: halt and escalate to legal with audit log
- Missing BusinessRequirement: default to prior strategy and flag for review
- ESG or regulatory breach detected