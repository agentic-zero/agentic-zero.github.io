# Integration Guide — authorize_defective_product_return_agent
**Process:** Authorize Defective Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp authorize_defective_product_return_agent.py ./agents/
```

## Basic Usage
```python
from agents.authorize_defective_product_return_agent import AuthorizeDefectiveProductReturnAgentAgent

agent = AuthorizeDefectiveProductReturnAgentAgent()
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
- warranty_database_api
- return_policy_service
- fraud_detection_system
- rma_generator
- compliance_audit_logger

## Escalation
The agent automatically escalates to human when:
- fraud flag detected
- pharma GxP compliance review required
- incomplete evidence after 72h pause