# Integration Guide — mto_product_staging_agent
**Process:** Stage Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_product_staging_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_product_staging_agent import MtoProductStagingAgentAgent

agent = MtoProductStagingAgentAgent()
result = agent.execute({
    "packaged_products": your_packaged_products_data,
    "delivery_schedules": your_delivery_schedules_data,
    "documentation_requirements": your_documentation_requirements_data,
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
- WMS_API
- document_validation_service
- inventory_transaction_logger
- capacity_monitoring_sensor
- compliance_rule_engine

## Escalation
The agent automatically escalates to human when:
- dangerous_goods_documentation missing
- staging_accuracy below 0.99 after retry
- inventory_update timeout or mismatch
- staging_area full with no alternate route