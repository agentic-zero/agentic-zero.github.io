# Integration Guide â€” gdpr_article5_compliance_agent
**Process:** GDPR Data Processing Principles
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gdpr_article5_compliance_agent.py ./agents/
```

## Basic Usage
```python
from agents.gdpr_article5_compliance_agent import GdprArticle5ComplianceAgentAgent

agent = GdprArticle5ComplianceAgentAgent()
result = agent.execute({
    "personal_data_inventory": your_personal_data_inventory_data,
    "processing_purposes": your_processing_purposes_data,
    "lawful_basis_assessment": your_lawful_basis_assessment_data,
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
- personal_data_inventory_api
- legal_basis_evaluator
- automated_deletion_scheduler
- dpia_generator

## Escalation
The agent automatically escalates to human when:
- Missing lawful basis documentation
- Special category processing without documented exception or DPIA
- Retention schedule expiry without deletion confirmation