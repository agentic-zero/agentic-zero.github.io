# Integration Guide — verify_product_mto_agent
**Process:** Verify Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp verify_product_mto_agent.py ./agents/
```

## Basic Usage
```python
from agents.verify_product_mto_agent import VerifyProductMtoAgentAgent

agent = VerifyProductMtoAgentAgent()
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
- material_database_api
- certificate_validator
- compliance_engine
- test_equipment_interface
- supplier_notification_service

## Escalation
The agent automatically escalates to human when:
- Missing MaterialCertificate triggers quarantine and supplier notification
- First-pass failure logs KPI deviation and routes to SCOR-S2.4