# Integration Guide — gxp_csv_validation_orchestrator
**Process:** Validation & Qualification (CSV/Equipment)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gxp_csv_validation_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.gxp_csv_validation_orchestrator import GxpCsvValidationOrchestratorAgent

agent = GxpCsvValidationOrchestratorAgent()
result = agent.execute({
    "user_requirements": your_user_requirements_data,
    "risk_assessment": your_risk_assessment_data,
    "validation_protocols": your_validation_protocols_data,
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
- veeva_vault_api
- mastercontrol_connector
- e_signature_service
- risk_assessment_engine
- test_script_executor
- erp_fallback_logger

## Escalation
The agent automatically escalates to human when:
- qualification gateway failure
- missing UserRequirementsSpecification
- protocol deviation or overdue PeriodicReview
- ERP integration failure requiring manual audit entry