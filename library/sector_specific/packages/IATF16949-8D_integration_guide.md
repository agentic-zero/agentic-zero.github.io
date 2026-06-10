# Integration Guide â€” iatf_8d_autonomous_solver
**Process:** 8D Problem Solving
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iatf_8d_autonomous_solver.py ./agents/
```

## Basic Usage
```python
from agents.iatf_8d_autonomous_solver import Iatf8DAutonomousSolverAgent

agent = Iatf8DAutonomousSolverAgent()
result = agent.execute({
    "customer_complaint": your_customer_complaint_data,
    "defect_data": your_defect_data_data,
    "process_data": your_process_data_data,
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
- CRM_complaint_api
- MES_defect_data_query
- ERP_user_assignment
- quality_database_recurrence_calc
- document_management_system

## Escalation
The agent automatically escalates to human when:
- root_cause unidentified after two analysis cycles
- containment_effectiveness < 100% after scope expansion
- missing defect samples logged as exception beyond 24h
- cycle_time approaching KPI limit without closure