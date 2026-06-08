# Integration Guide — carrier_selection_and_shipment_rating_agent
**Process:** Select Carriers and Rate Shipments (MTO)
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp carrier_selection_and_shipment_rating_agent.py ./agents/
```

## Basic Usage
```python
from agents.carrier_selection_and_shipment_rating_agent import CarrierSelectionAndShipmentRatingAgentAgent

agent = CarrierSelectionAndShipmentRatingAgentAgent()
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
- carrier_rate_api
- performance_scorecard_db
- compliance_checker
- routing_plan_interface

## Escalation
The agent automatically escalates to human when:
- no_carrier_meets_requirements escalate to manual review
- rate_card_expired trigger refresh and pause