# Integration Guide — mto_stage_product_agent
**Process:** Stage Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_stage_product_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_stage_product_agent import MtoStageProductAgentAgent

agent = MtoStageProductAgentAgent()
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
- ERP_delivery_schedule
- barcode_scan_interface
- compliance_master_data_service

## Escalation
The agent automatically escalates to human when:
- Missing dangerous_goods_documentation or GxP release
- StagingArea capacity exceeded after overflow attempt
- staging_accuracy < 99.5% or cycle_time breach