# Integration Guide — ibp_autonomous_planner
**Process:** Integrated Business Planning (IBP)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp ibp_autonomous_planner.py ./agents/
```

## Basic Usage
```python
from agents.ibp_autonomous_planner import IbpAutonomousPlannerAgent

agent = IbpAutonomousPlannerAgent()
result = agent.execute({
    "strategic_plan": your_strategic_plan_data,
    "portfolio_data": your_portfolio_data_data,
    "market_intelligence": your_market_intelligence_data,
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
- SAP_IBP_API
- Kinaxis_connector
- o9_data_sync
- GDPR_compliance_filter
- SCOR_metric_calculator

## Escalation
The agent automatically escalates to human when:
- Gateway deadlock >5 business days
- Regulatory constraint violation
- Executive Business Review rejection twice
- Missing capacity constraints at Supply Network Planning