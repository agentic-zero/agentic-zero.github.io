# Integration Guide — eco_lifecycle_orchestrator
**Process:** Engineering Change Order (ECO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eco_lifecycle_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.eco_lifecycle_orchestrator import EcoLifecycleOrchestratorAgent

agent = EcoLifecycleOrchestratorAgent()
result = agent.execute({
    "change_request": your_change_request_data,
    "engineering_drawings": your_engineering_drawings_data,
    "bom": your_bom_data,
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
- erp_event_listener
- plm_api
- finance_cost_engine
- compliance_db_checker
- production_scheduler

## Escalation
The agent automatically escalates to human when:
- DesignFeasible==false or CostApproved==false
- HighReworkRate detected
- cycle_time_KPI breach or missing approvals