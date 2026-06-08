# Integration Guide — material_verification_agent
**Process:** Verify Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp material_verification_agent.py ./agents/
```

## Basic Usage
```python
from agents.material_verification_agent import MaterialVerificationAgentAgent

agent = MaterialVerificationAgentAgent()
result = agent.execute({
    "received_materials": your_received_materials_data,
    "specifications": your_specifications_data,
    "material_certificates": your_material_certificates_data,
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
- ERP_goods_receipt_listener
- test_equipment_api
- certificate_validator
- compliance_engine

## Escalation
The agent automatically escalates to human when:
- Missing certificates after 24h
- Traceability <100% on AS9100 lots
- Expired test equipment calibration