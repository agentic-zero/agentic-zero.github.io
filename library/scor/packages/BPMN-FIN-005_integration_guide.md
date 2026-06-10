# Integration Guide — trade_finance_lc_orchestrator
**Process:** Trade Finance & Letters of Credit
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp trade_finance_lc_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.trade_finance_lc_orchestrator import TradeFinanceLcOrchestratorAgent

agent = TradeFinanceLcOrchestratorAgent()
result = agent.execute({
    "sales_contract": your_sales_contract_data,
    "lc_terms": your_lc_terms_data,
    "shipping_documents": your_shipping_documents_data,
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
- ERP_system
- logistics_api
- customs_api
- banking_api
- aml_screening_tool

## Escalation
The agent automatically escalates to human when:
- unresolved document discrepancy after 5 days
- LC rejection by ImporterBank
- payment delay >14 days
- AML flag requiring override