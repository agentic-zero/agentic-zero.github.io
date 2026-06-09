# Integration Guide — gxp_change_control_agent
**Process:** Change Control Management
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gxp_change_control_agent.py ./agents/
```

## Basic Usage
```python
from agents.gxp_change_control_agent import GxpChangeControlAgentAgent

agent = GxpChangeControlAgentAgent()
result = agent.execute({
    "change_request": your_change_request_data,
    "risk_data": your_risk_data_data,
    "regulatory_requirements": your_regulatory_requirements_data,
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
- Veeva_Vault_API
- SAP_QM_API
- ERP_change_record_sync
- electronic_signature_service
- GxP_audit_logger

## Escalation
The agent automatically escalates to human when:
- required lane approval missing after timeout
- RegulatoryImpactAssessment identifies filing need without output
- ValidationReport fails after ImplementChange
- EffectivenessCheck == false after rework limit