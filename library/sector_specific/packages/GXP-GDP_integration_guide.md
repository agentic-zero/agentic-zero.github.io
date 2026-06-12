# Integration Guide â€” gdp_compliance_hybrid_agent
**Process:** Good Distribution Practice (GDP)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gdp_compliance_hybrid_agent.py ./agents/
```

## Basic Usage
```python
from agents.gdp_compliance_hybrid_agent import GdpComplianceHybridAgentAgent

agent = GdpComplianceHybridAgentAgent()
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
- IoT_sensor_api
- WMS_integration
- CRM_qualification_api
- document_management_system

## Escalation
The agent automatically escalates to human when:
- excursion >30 min without QA approval
- unqualified customer without documented deviation
- complaint not investigated within 24 h