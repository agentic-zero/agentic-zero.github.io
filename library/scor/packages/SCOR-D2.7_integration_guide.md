# Integration Guide — carrier_selector_and_shipment_rater
**Process:** Select Carriers and Rate Shipments (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp carrier_selector_and_shipment_rater.py ./agents/
```

## Basic Usage
```python
from agents.carrier_selector_and_shipment_rater import CarrierSelectorAndShipmentRaterAgent

agent = CarrierSelectorAndShipmentRaterAgent()
result = agent.execute({
    "routing_plans": your_routing_plans_data,
    "carrier_rate_cards": your_carrier_rate_cards_data,
    "service_requirements": your_service_requirements_data,
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
- routing_plan_ingest
- carrier_rate_card_db
- performance_scorecard_api
- erp_budget_feed

## Escalation
The agent automatically escalates to human when:
- no carrier meets budget_constraint
- customs_broker_regulations violated