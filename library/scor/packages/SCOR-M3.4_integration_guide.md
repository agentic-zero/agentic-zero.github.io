# Integration Guide — eto_packaging_agent
**Process:** Package (ETO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp eto_packaging_agent.py ./agents/
```

## Basic Usage
```python
from agents.eto_packaging_agent import EtoPackagingAgentAgent

agent = EtoPackagingAgentAgent()
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
- contract_validation_api
- compliance_rule_engine
- documentation_generator
- packaging_equipment_interface
- export_regulation_db

## Escalation
The agent automatically escalates to human when:
- missing_contract_packaging_requirements
- unclassified_dangerous_goods
- MIL-SPEC_or_export_noncompliance