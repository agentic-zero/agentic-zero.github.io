# Integration Guide — supply_chain_procurement_manager
**Process:** Manage Supply Chain Procurement
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_procurement_manager.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_procurement_manager import SupplyChainProcurementManagerAgent

agent = SupplyChainProcurementManagerAgent()
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
- erp_spend_data_connector
- supplier_market_data_api
- analytics_engine
- compliance_validation_service

## Escalation
The agent automatically escalates to human when:
- anti-corruption flag raised
- SpendUnderManagement < 0.7 or savings target missed requiring audit
- SupplierMarketData missing or >90 days old
- GDPR/EU AI Act/ESG non-compliance detected