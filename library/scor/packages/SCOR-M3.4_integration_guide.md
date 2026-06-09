# Integration Guide — eto_packaging_compliance_agent
**Process:** Package (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_packaging_compliance_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_packaging_compliance_agent import EtoPackagingComplianceAgentAgent

agent = EtoPackagingComplianceAgentAgent()
result = agent.execute({
    "eto_finished_products": your_eto_finished_products_data,
    "contract_packaging_requirements": your_contract_packaging_requirements_data,
    "export_requirements": your_export_requirements_data,
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
- packaging_workflow_api
- compliance_rule_engine
- documentation_generator
- test_equipment_interface
- export_control_db

## Escalation
The agent automatically escalates to human when:
- missing contract packaging requirements
- preservation test failure
- export control mismatch detected