# Integration Guide — supply_chain_performance_manager
**Process:** Manage Supply Chain Performance
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supply_chain_performance_manager.py ./agents/
```

## Basic Usage
```python
from agents.supply_chain_performance_manager import SupplyChainPerformanceManagerAgent

agent = SupplyChainPerformanceManagerAgent()
result = agent.execute({
    "operational_data": your_operational_data_data,
    "kpi_targets": your_kpi_targets_data,
    "benchmark_data": your_benchmark_data_data,
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
- erp_mes_connector
- apics_benchmark_api
- planning_module_interface
- audit_log_system

## Escalation
The agent automatically escalates to human when:
- Missing OperationalData after validation
- ImprovementPlan completion <0.85 after 30 days
- Compliance violation or schema drift detected