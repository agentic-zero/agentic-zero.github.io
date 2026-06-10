# Integration Guide â€” gdp_distribution_compliance_agent
**Process:** Good Distribution Practice (GDP)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gdp_distribution_compliance_agent.py ./agents/
```

## Basic Usage
```python
from agents.gdp_distribution_compliance_agent import GdpDistributionComplianceAgentAgent

agent = GdpDistributionComplianceAgentAgent()
result = agent.execute({
    "product_specifications": your_product_specifications_data,
    "storage_requirements": your_storage_requirements_data,
    "distribution_routes": your_distribution_routes_data,
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
- IoT_sensor_API
- ERP_WMS_TMS_integration
- record_database
- qualification_registry

## Escalation
The agent automatically escalates to human when:
- unresolved temperature excursion after 48 hours
- missing Qualification_Record or Temperature_Record
- customer complaint requiring QA release decision