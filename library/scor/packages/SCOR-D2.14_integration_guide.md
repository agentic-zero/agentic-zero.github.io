# Integration Guide — mto_product_installation_agent
**Process:** Install Product (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mto_product_installation_agent.py ./agents/
```

## Basic Usage
```python
from agents.mto_product_installation_agent import MtoProductInstallationAgentAgent

agent = MtoProductInstallationAgentAgent()
result = agent.execute({
    "delivered_product": your_delivered_product_data,
    "installation_instructions": your_installation_instructions_data,
    "site_readiness_data": your_site_readiness_data_data,
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
- inventory_system
- site_assessment_api
- scheduling_system
- process_repository
- kpi_tracker

## Escalation
The agent automatically escalates to human when:
- site not ready after reschedule attempt
- missing GDPR consent record
- missing installation instructions
- commissioning failure requiring SCOR-D2.15