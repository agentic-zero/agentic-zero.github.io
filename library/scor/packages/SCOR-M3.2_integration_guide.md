# Integration Guide â€” eto_issue_processor
**Process:** Issue In-Process Product (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_issue_processor.py ./agents/
```

## Basic Usage
```python
from agents.eto_issue_processor import EtoIssueProcessorAgent

agent = EtoIssueProcessorAgent()
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
- ECM_API
- MES_API
- ComplianceEngine

## Escalation
The agent automatically escalates to human when:
- BOM accuracy < 1.0
- defense sector with exportControl flag requiring dual authorization
- configuration mismatch detected