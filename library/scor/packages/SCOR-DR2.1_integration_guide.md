# Integration Guide — authorize_mro_product_return_agent
**Process:** Authorize MRO Product Return
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp authorize_mro_product_return_agent.py ./agents/
```

## Basic Usage
```python
from agents.authorize_mro_product_return_agent import AuthorizeMroProductReturnAgentAgent

agent = AuthorizeMroProductReturnAgentAgent()
result = agent.execute({
    "mro_return_request": your_mro_return_request_data,
    "purchase_history": your_purchase_history_data,
    "product_condition_assessment": your_product_condition_assessment_data,
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
- MROReturnRequest_API
- PurchaseHistory_DB
- ReturnPolicyEngine
- ProductConditionAssessmentService
- ComplianceChecker

## Escalation
The agent automatically escalates to human when:
- Missing required fields route to manual review queue
- Pharma or defense sector requires additional regulatory approval
- Hazardous MRO without environmental compliance check