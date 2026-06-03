# Integration Guide — supplier_audit_agent
**Process:** Conduct Supplier Audits and Assessments
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supplier_audit_agent.py ./agents/
```

## Basic Usage
```python
from agents.supplier_audit_agent import SupplierAuditAgentAgent

agent = SupplierAuditAgentAgent()
result = agent.execute({
    "supplier_information": your_supplier_information_data,
    "audit_schedules": your_audit_schedules_data,
    "assessment_criteria": your_assessment_criteria_data,
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
- audit_tool
- assessment_tool
- supplier_database
- quality_control_manual

## Escalation
The agent automatically escalates to human when:
- non-compliance indicated in audit report
- low quality indicated in assessment result
- incomplete or missing supplier information