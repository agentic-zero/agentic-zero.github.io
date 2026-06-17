# Integration Guide â€” otc_transport_autonomous_agent
**Process:** Proceso OTC para empresa de transporte de distribucion. Un unico operador full-t
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp otc_transport_autonomous_agent.py ./agents/
```

## Basic Usage
```python
from agents.otc_transport_autonomous_agent import OtcTransportAutonomousAgentAgent

agent = OtcTransportAutonomousAgentAgent()
result = agent.execute({
    "customer_order": your_customer_order_data,
    "order_type_code": your_order_type_code_data,
    "delivery_address": your_delivery_address_data,
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
- SAP_VBAK_VBAP_BAPI
- TMS_Capacity_API
- Email_Draft_Service
- Audit_Logger

## Escalation
The agent automatically escalates to human when:
- overdue_days > 15 or sap_credit_blocked
- price_discrepancy_pct > 1
- capacity_available false
- ZINT missing docs
- TMS/SAP connection error
- new prepay without statement match