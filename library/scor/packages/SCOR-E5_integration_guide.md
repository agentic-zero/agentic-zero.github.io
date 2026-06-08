# Integration Guide — supply_chain_asset_manager
**Process:** Manage Supply Chain Assets
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_asset_manager.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_asset_manager import SupplyChainAssetManagerAgent

agent = SupplyChainAssetManagerAgent()
result = agent.execute({
    "asset_registry": your_asset_registry_data,
    "maintenance_schedules": your_maintenance_schedules_data,
    "asset_performance_data": your_asset_performance_data_data,
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
- asset_database_api
- iot_scada_stream
- maintenance_scheduler
- capital_plan_store
- kpi_configuration_store

## Escalation
The agent automatically escalates to human when:
- maintenance_compliance_rate < 0.98
- CapitalPlan budget exceeded
- IoT offline > 24h or EU AI Act/safety non-compliance detected