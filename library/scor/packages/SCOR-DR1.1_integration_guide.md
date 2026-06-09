# Integration Guide — defective_return_rma_authorizer
**Process:** Authorize Defective Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp defective_return_rma_authorizer.py ./agents/
```

## Basic Usage
```python
from agents.defective_return_rma_authorizer import DefectiveReturnRmaAuthorizerAgent

agent = DefectiveReturnRmaAuthorizerAgent()
result = agent.execute({
    "customer_return_request": your_customer_return_request_data,
    "defect_evidence": your_defect_evidence_data,
    "product_warranty_data": your_product_warranty_data_data,
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
- customer_request_api
- warranty_db
- return_policy_engine
- rma_generator
- notification_service

## Escalation
The agent automatically escalates to human when:
- no DefectEvidence provided
- warranty expired
- authorizationCycleTime exceeds 48h