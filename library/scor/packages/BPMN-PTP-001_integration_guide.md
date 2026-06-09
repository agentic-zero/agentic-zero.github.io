# Integration Guide — ptp_hybrid_orchestrator
**Process:** Purchase-to-Pay
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp ptp_hybrid_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.ptp_hybrid_orchestrator import PtpHybridOrchestratorAgent

agent = PtpHybridOrchestratorAgent()
result = agent.execute({
    "purchase_requisition": your_purchase_requisition_data,
    "supplier_catalog": your_supplier_catalog_data,
    "budget_data": your_budget_data_data,
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
- ERP_API
- ApprovalWorkflowEngine
- SupplierCatalogService
- InvoiceIngestionAPI
- ComplianceAuditLogger

## Escalation
The agent automatically escalates to human when:
- Approval timeout > 48h auto-escalate
- 3-WayMatch fails > 2 times create ExceptionCase
- Goods inspection rejects > 10% flag non-compliant supplier
- ApprovalRequired loops > 3 terminate as CANCELLED