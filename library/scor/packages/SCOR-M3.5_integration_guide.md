# Integration Guide — eto_product_staging_agent
**Process:** Stage Product (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_product_staging_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_product_staging_agent import EtoProductStagingAgentAgent

agent = EtoProductStagingAgentAgent()
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
- export_license_verifier
- documentation_completeness_checker
- inspection_scheduler_api
- kpi_calculator
- timestamp_logger

## Escalation
The agent automatically escalates to human when:
- Export license expires mid-process (24h SLA to compliance officer)
- Customer inspection fails (route back to M3.4)