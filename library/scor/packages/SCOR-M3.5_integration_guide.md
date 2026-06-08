# Integration Guide — eto_stage_product_agent
**Process:** Stage Product (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_stage_product_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_stage_product_agent import EtoStageProductAgentAgent

agent = EtoStageProductAgentAgent()
result = agent.execute({
    "packaged_eto_products": your_packaged_eto_products_data,
    "data_packages": your_data_packages_data,
    "export_licenses": your_export_licenses_data,
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
- government_export_portal
- customer_ERP_connector
- regulatory_compliance_db
- internal_audit_logger

## Escalation
The agent automatically escalates to human when:
- ExportLicense invalid or ITAR violation (24h compliance officer)
- CustomerInspectionPassRate < 100% after rework limit
- documentation_completeness < 100% requiring manual entry