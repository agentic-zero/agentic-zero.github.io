# Integration Guide — deviation_oos_investigation_agent
**Process:** Deviation & OOS Investigation
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp deviation_oos_investigation_agent.py ./agents/
```

## Basic Usage
```python
from agents.deviation_oos_investigation_agent import DeviationOosInvestigationAgentAgent

agent = DeviationOosInvestigationAgentAgent()
result = agent.execute({
    "deviation_report": your_deviation_report_data,
    "batch_data": your_batch_data_data,
    "oos_result": your_oos_result_data,
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
- LIMS_API
- Veeva_Vault_connector
- SAP_QM_event_listener
- regulatory_filing_system
- CAPA_tracker

## Escalation
The agent automatically escalates to human when:
- investigation_cycle_time > 30 days
- root_cause unidentified after Phase2
- regulatory deadline missed
- ProductImpact confirmed with unknown cause