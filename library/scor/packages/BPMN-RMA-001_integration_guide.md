# Integration Guide â€” rma_autonomous_agent
**Process:** Returns Management (RMA)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp rma_autonomous_agent.py ./agents/
```

## Basic Usage
```python
from agents.rma_autonomous_agent import RmaAutonomousAgentAgent

agent = RmaAutonomousAgentAgent()
result = agent.execute({
    "return_request": your_return_request_data,
    "order_history": your_order_history_data,
    "return_policy": your_return_policy_data,
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
- erp_system_api
- customer_portal_event_bus
- quality_inspection_system
- finance_credit_api
- inventory_update_service

## Escalation
The agent automatically escalates to human when:
- ReturnRequest outside policy or inspection timeout
- ERP sync failure after retry queue
- manual review required for quality criteria failure