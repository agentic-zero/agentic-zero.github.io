# Integration Guide â€” gmp_annex11_compliance_agent
**Process:** Good Manufacturing Practice (GMP) — EU Annex 11
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp gmp_annex11_compliance_agent.py ./agents/
```

## Basic Usage
```python
from agents.gmp_annex11_compliance_agent import GmpAnnex11ComplianceAgentAgent

agent = GmpAnnex11ComplianceAgentAgent()
result = agent.execute({
    "manufacturing_procedures": your_manufacturing_procedures_data,
    "validation_documentation": your_validation_documentation_data,
    "batch_records": your_batch_records_data,
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
- batch_record_repository
- validation_documentation_store
- audit_trail_logger
- kpi_calculator
- capa_tracker

## Escalation
The agent automatically escalates to human when:
- Critical GMPAuditFinding detected
- ALCOA+ violation post-release
- Legacy system partial coverage without risk assessment