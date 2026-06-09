# Integration Guide — eto_component_issue_agent
**Process:** Issue In-Process Product (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_component_issue_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_component_issue_agent import EtoComponentIssueAgentAgent

agent = EtoComponentIssueAgentAgent()
result = agent.execute({
    "engineering_boms": your_engineering_boms_data,
    "configuration_documents": your_configuration_documents_data,
    "eto_components": your_eto_components_data,
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
- PLM_API
- ERP_API
- MES_API
- Audit_Log_System

## Escalation
The agent automatically escalates to human when:
- BOM version mismatch or missing Configuration_Document
- traceability_completeness < 100%
- export_control or AS9100 flag violation