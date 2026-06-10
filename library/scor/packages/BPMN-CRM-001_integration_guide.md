# Integration Guide — complaint_lifecycle_orchestrator
**Process:** Customer Complaint Management
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp complaint_lifecycle_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.complaint_lifecycle_orchestrator import ComplaintLifecycleOrchestratorAgent

agent = ComplaintLifecycleOrchestratorAgent()
result = agent.execute({
    "customer_complaint": your_customer_complaint_data,
    "order_data": your_order_data_data,
    "product_data": your_product_data_data,
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
- complaint_db_api
- customer_comms_service
- capa_system
- regulatory_submission_api
- audit_logger

## Escalation
The agent automatically escalates to human when:
- SafetyIssue or RegulatoryReportable true
- ResolutionAccepted false after 2 attempts
- cycle_time > 25 days