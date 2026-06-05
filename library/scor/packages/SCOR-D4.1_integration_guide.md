# Integration Guide — return_request_manager
**Process:** Manage Delivery Returns
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp return_request_manager.py ./agents/
```

## Basic Usage
```python
from agents.return_request_manager import ReturnRequestManagerAgent

agent = ReturnRequestManagerAgent()
result = agent.execute({
    "return_requests": your_return_requests_data,
    "return_policies": your_return_policies_data,
    "inventory_data": your_inventory_data_data,
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
- customer_database_API
- inventory_management_system_API
- company_database_API
- email_notification_tool

## Escalation
The agent automatically escalates to human when:
- invalid or missing return request information
- product safety concerns
- customer complaints or disputes