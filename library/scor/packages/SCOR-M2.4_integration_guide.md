# Integration Guide — mto_packaging_execution_agent
**Process:** Package (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_packaging_execution_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_packaging_execution_agent import MtoPackagingExecutionAgentAgent

agent = MtoPackagingExecutionAgentAgent()
result = agent.execute({
    "finished_products": your_finished_products_data,
    "customer_packaging_specifications": your_customer_packaging_specifications_data,
    "labeling_requirements": your_labeling_requirements_data,
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
- inventory_system_api
- crm_spec_retriever
- wms_batch_tracker
- mes_timestamp_logger
- label_printer_compliance_scanner
- dangerous_goods_regulation_checker

## Escalation
The agent automatically escalates to human when:
- missing customer specs or adherence < 1.0
- material shortage without documented approval
- scan mismatch or damage detected