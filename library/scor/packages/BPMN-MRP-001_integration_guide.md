# Integration Guide — mrp_autonomous_planner
**Process:** Material Requirements Planning
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp mrp_autonomous_planner.py ./agents/
```

## Basic Usage
```python
from agents.mrp_autonomous_planner import MrpAutonomousPlannerAgent

agent = MrpAutonomousPlannerAgent()
result = agent.execute({
    "demand_forecast": your_demand_forecast_data,
    "sales_orders": your_sales_orders_data,
    "bom": your_bom_data,
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
- erp_api
- plm_bom_query
- warehouse_db
- supplier_lead_time_service
- compliance_flagger

## Escalation
The agent automatically escalates to human when:
- CapacityAvailable == false or ApprovePlan == false
- unresolved MaterialShortageAlert
- exception_rate > 0.05