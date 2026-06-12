# Integration Guide â€” iso9001_context_monitor
**Process:** Context of the Organization
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp iso9001_context_monitor.py ./agents/
```

## Basic Usage
```python
from agents.iso9001_context_monitor import Iso9001ContextMonitorAgent

agent = Iso9001ContextMonitorAgent()
result = agent.execute({
    "strategic_direction": your_strategic_direction_data,
    "internal_issues": your_internal_issues_data,
    "external_issues": your_external_issues_data,
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
- regulatory_api
- document_management_system
- stakeholder_db
- leadership_minutes_parser

## Escalation
The agent automatically escalates to human when:
- null fields in ContextAnalysis after 30 days
- stakeholder_coverage < 0.90 or scope_completeness < 0.95
- new regulatory requirement not processed within 30 days