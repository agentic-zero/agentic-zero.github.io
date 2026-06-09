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
- erp_mes_api
- apics_benchmark_db
- kpi_calculator
- compliance_logger

## Escalation
The agent automatically escalates to human when:
- reporting cycle time >24 hours to SCOR-E1
- missing compliance metadata on PerformanceReport