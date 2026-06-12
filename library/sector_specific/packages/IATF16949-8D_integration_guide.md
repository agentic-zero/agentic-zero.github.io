# Integration Guide â€” iatf16949_8d_automation_agent
**Process:** 8D Problem Solving
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iatf16949_8d_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.iatf16949_8d_automation_agent import Iatf169498DAutomationAgentAgent

agent = Iatf169498DAutomationAgentAgent()
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
- CRM_API
- MES_defect_API
- SCADA_process_feed
- ERP_change_order
- KPI_dashboard
- fishbone_5why_engine

## Escalation
The agent automatically escalates to human when:
- team_formation_exceeds_24h
- root_cause_rate_below_0.9_after_extension
- recurrence_rate_above_0.02
- missing_critical_data_without_exception_flag