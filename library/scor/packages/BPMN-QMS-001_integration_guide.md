# Integration Guide — capa_lifecycle_orchestrator
**Process:** Non-Conformance & CAPA Management
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp capa_lifecycle_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.capa_lifecycle_orchestrator import CapaLifecycleOrchestratorAgent

agent = CapaLifecycleOrchestratorAgent()
result = agent.execute({
    "non-conformance_report": your_non-conformance_report_data,
    "product_data": your_product_data_data,
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
- nonconformance_event_listener
- regulatory_timeline_api
- root_cause_analyzer
- effectiveness_verification_db
- kpi_calculator

## Escalation
The agent automatically escalates to human when:
- SafetyIssue detected or CAPA cycle >90 days
- RootCauseAnalysis fails after 3 iterations
- RegulatoryNotification missed within 24h window