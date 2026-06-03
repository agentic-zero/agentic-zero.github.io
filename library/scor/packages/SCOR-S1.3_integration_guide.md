# Integration Guide — supplier_information_manager
**Process:** Manage Supplier Information and Performance
**Version:** 1.0.0

## Prerequisites
- Python 3.10+
- Agentic Zero runtime installed
- API credentials configured in .env

## Installation
```bash
# Copy agent to your project
cp supplier_information_manager.py ./agents/
```

## Basic Usage
```python
from agents.supplier_information_manager import SupplierInformationManagerAgent

agent = SupplierInformationManagerAgent()
result = agent.execute({
    "supplier_information": your_supplier_information_data,
    "performance_data": your_performance_data_data,
    "quality_metrics": your_quality_metrics_data,
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
- supplier_registration_api
- internal_logistics_system_api
- quality_control_system_api
- customer_feedback_api

## Escalation
The agent automatically escalates to human when:
- supplier_quality_rating_below_threshold
- supplier_delivery_performance_below_threshold
- discrepancy_in_performance_data_or_quality_metrics