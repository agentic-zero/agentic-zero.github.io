# Integration Guide — mto_delivery_verification_agent
**Process:** Receive and Verify Product by Customer (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_delivery_verification_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_delivery_verification_agent import MtoDeliveryVerificationAgentAgent

agent = MtoDeliveryVerificationAgentAgent()
result = agent.execute({
    "shipment_tracking_data": your_shipment_tracking_data_data,
    "proof_of_delivery": your_proof_of_delivery_data,
    "customer_acceptance_criteria": your_customer_acceptance_criteria_data,
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
- carrier_api
- document_hash_verifier
- customer_acceptance_interface
- invoice_system_trigger
- gdpr_consent_manager

## Escalation
The agent automatically escalates to human when:
- No ProofOfDelivery within 24h
- AcceptanceCriteria failure requiring return authorization
- SLA breach on InvoiceTrigger