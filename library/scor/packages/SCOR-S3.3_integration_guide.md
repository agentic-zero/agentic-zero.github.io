# Integration Guide — eto_product_verification_agent
**Process:** Verify Engineer-to-Order Product
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_product_verification_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_product_verification_agent import EtoProductVerificationAgentAgent

agent = EtoProductVerificationAgentAgent()
result = agent.execute({
    "eto_components": your_eto_components_data,
    "engineering_drawings": your_engineering_drawings_data,
    "specifications": your_specifications_data,
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
- CMM_data_reader
- material_cert_validator
- test_procedure_executor
- GDPR_redaction_tool

## Escalation
The agent automatically escalates to human when:
- missing material_cert
- non_conformance_rate exceeds threshold
- personal_data handling required