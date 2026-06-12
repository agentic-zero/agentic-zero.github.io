# Integration Guide â€” nonconformity_improvement_agent
**Process:** Improvement — Nonconformity and Continual Improvement
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp nonconformity_improvement_agent.py ./agents/
```

## Basic Usage
```python
from agents.nonconformity_improvement_agent import NonconformityImprovementAgentAgent

agent = NonconformityImprovementAgentAgent()
result = agent.execute({
    "nonconformance_reports": your_nonconformance_reports_data,
    "audit_findings": your_audit_findings_data,
    "customer_complaints": your_customer_complaints_data,
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
- QMS database API
- KPI monitoring service
- notification and escalation bus
- document management system

## Escalation
The agent automatically escalates to human when:
- recurrence rate >5% or critical audit finding
- safety-related customer complaint
- CAPA closure attempted without root cause