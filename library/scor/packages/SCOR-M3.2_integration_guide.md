# Integration Guide — eto_issue_automation_agent
**Process:** Issue In-Process Product (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_issue_automation_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_issue_automation_agent import EtoIssueAutomationAgentAgent

agent = EtoIssueAutomationAgentAgent()
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
- PLM_system_api
- MES_workpackage_interface
- inventory_master_query
- sha256_generator
- compliance_signature_checker

## Escalation
The agent automatically escalates to human when:
- Missing configuration signature routes to compliance queue
- BOM mismatch auto-creates discrepancy and notifies engineering within 4 hours
- Traceability break from override requires quality sign-off