# Integration Guide — month_end_financial_close_orchestrator
**Process:** Month-End Financial Close
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp month_end_financial_close_orchestrator.py ./agents/
```

## Basic Usage
```python
from agents.month_end_financial_close_orchestrator import MonthEndFinancialCloseOrchestratorAgent

agent = MonthEndFinancialCloseOrchestratorAgent()
result = agent.execute({
    "transaction_data": your_transaction_data_data,
    "accrual_schedules": your_accrual_schedules_data,
    "reconciliation_templates": your_reconciliation_templates_data,
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
- ERP_journal_api
- reconciliation_engine
- variance_analysis_tool
- sox_audit_logger

## Escalation
The agent automatically escalates to human when:
- AllEntriesPosted false after 3 retries
- IntercompanyReconciliation failure
- VarianceExplained false after 2 cycles
- Approved false after max review cycles