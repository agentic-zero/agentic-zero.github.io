# Integration Guide — supply_chain_risk_manager
**Process:** Manage Supply Chain Risk
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_risk_manager.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_risk_manager import SupplyChainRiskManagerAgent

agent = SupplyChainRiskManagerAgent()
result = agent.execute({
    "risk_signals": your_risk_signals_data,
    "operational_data": your_operational_data_data,
    "market_intelligence": your_market_intelligence_data,
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
- risk_signal_api
- supplier_erp_connector
- geopolitical_data_api
- iso31000_audit_logger
- eu_ai_act_checker

## Escalation
The agent automatically escalates to human when:
- mitigation_effectiveness < 0.8
- defense sector risk detected
- open compliance violations after validation
- stale data detected in KPI calculation