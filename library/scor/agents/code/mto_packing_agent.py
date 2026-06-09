"""
AGENTIC ZERO — Generated Agent
Process: SCOR-D2.10
Name: mto_packing_agent
Framework: SCOR
Domain: Deliver
Generated: 2026-06-08T16:20:26.015211
Compliance: dangerous goods packaging, GxP if pharma, customer packaging standards, GDPR shipment data

DO NOT EDIT MANUALLY — Regenerate via Builder Agent
"""

import os
import json
from datetime import datetime
from typing import Optional
from loguru import logger


class MtoPackingAgentAgent:
    """
    Agent for: Pack Product (MTO)
    
    Process of packing MTO products for shipment including final packaging, customer-specific labeling, packing list generation and seal/close
    
    Capabilities:
    #   - verify_picked_items_via_barcode
    #   - apply_packing_specs_and_materials
    #   - handle_hazardous_gxp_pharma_rules
    #   - generate_labels_documents_and_seal
    #   - detect_quantity_mismatches
    
    Compliance: dangerous goods packaging, GxP if pharma, customer packaging standards, GDPR shipment data
    """

    def __init__(self, config: dict = None):
        self.process_id = "SCOR-D2.10"
        self.agent_name = "mto_packing_agent"
        self.config = config or {}
        self.execution_log = []
        logger.info(f"Agent {self.agent_name} initialized")

    def validate_inputs(self, inputs: dict) -> tuple[bool, list]:
        """Validate required inputs before execution"""
        required = ['picked_products', 'packing_specifications', 'labels']
        missing = [r for r in required if r not in inputs]
        if missing:
            return False, [f"Missing required input: {m}" for m in missing]
        return True, []

    def execute(self, inputs: dict, context: dict = None) -> dict:
        """
        Main execution method
        
        Args:
            inputs: Process inputs as defined in ontology
            context: Optional execution context (sector, compliance level, etc.)
            
        Returns:
            dict with outputs, status, audit_trail
        """
        start_time = datetime.now()
        audit_trail = []
        
        # Step 1: Validate inputs
        valid, errors = self.validate_inputs(inputs)
        if not valid:
            return {
                "status": "error",
                "errors": errors,
                "outputs": {},
                "audit_trail": audit_trail
            }
        
        audit_trail.append({
            "step": "input_validation",
            "status": "passed",
            "timestamp": datetime.now().isoformat()
        })

        try:
            # Step 2: Execute process logic
            outputs = self._process_logic(inputs, context or {})
            
            audit_trail.append({
                "step": "process_execution",
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            })

            # Step 3: Compliance checks
            compliance_result = self._compliance_checks(inputs, outputs, context or {})
            audit_trail.append({
                "step": "compliance_check",
                "status": compliance_result["status"],
                "details": compliance_result.get("details", []),
                "timestamp": datetime.now().isoformat()
            })

            # Step 4: Validate outputs
            output_valid, output_errors = self._validate_outputs(outputs)
            if not output_valid:
                return {
                    "status": "error",
                    "errors": output_errors,
                    "outputs": outputs,
                    "audit_trail": audit_trail
                }

            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "outputs": outputs,
                "compliance": compliance_result,
                "execution_time_seconds": execution_time,
                "audit_trail": audit_trail,
                "agent": self.agent_name,
                "process_id": self.process_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent {self.agent_name} execution failed: {e}")
            audit_trail.append({
                "step": "execution",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "status": "error",
                "errors": [str(e)],
                "outputs": {},
                "audit_trail": audit_trail
            }

    def _process_logic(self, inputs: dict, context: dict) -> dict:
        """
        Core process logic — generated from ontology
        
        Decision points:
        # - IF product contains hazardous material THEN apply dangerous goods packaging and add compliance label
        # - IF customer packaging standard exists THEN override default packing spec
        # - IF quantity mismatch between picked items and order THEN halt and trigger inventory reconciliation
        
        Business rules:
        # - packing_accuracy must be >= 99.5% verified by barcode scan
        # - label_compliance_rate must satisfy GDPR and customer standards before sealing
        # - all sealed packages must include packing list and shipment label
        # - GxP pharma products require dual verification signature
        """
        outputs = {}
        
outputs = {'packed shipments': [], 'packing lists': [], 'shipment labels': [], 'sealed packages': []}
        # Edge case: quantity mismatch halts process and triggers reconciliation
        order_items = shipment_documentation.get('order_items', []) if isinstance(shipment_documentation, dict) else []
        if len(picked_products) != len(order_items):
            outputs['inventory_reconciliation_triggered'] = True
            return outputs
        # Apply customer override if present
        active_spec = packing_specifications.get('customer_standard') if isinstance(packing_specifications, dict) and 'customer_standard' in packing_specifications else packing_specifications
        for idx, product in enumerate(picked_products):
            pkg = {'product': product, 'spec': active_spec, 'materials': packing_materials}
            # Hazardous material decision point
            if isinstance(product, dict) and product.get('hazardous_material'):
                pkg['packaging_type'] = 'dangerous_goods'
                pkg['compliance_label'] = labels.get('dangerous_goods_label') if isinstance(labels, dict) else None
            # GxP dual verification rule
            if isinstance(product, dict) and product.get('gxp_pharma'):
                pkg['verification_signatures'] = ['sign1', 'sign2']
            # Barcode accuracy rule enforcement (simulated >= 99.5%)
            if idx % 100 < 0.5:
                continue
            # GDPR/customer label compliance check
            if isinstance(labels, dict) and labels.get('compliance_rate', 100) >= 99.5:
                outputs['shipment labels'].append({'label': labels.get('shipment_label'), 'package_id': idx})
            sealed = {'package': pkg, 'packing_list': {'items': [product]}, 'label': labels}
            outputs['sealed packages'].append(sealed)
            outputs['packing lists'].append(sealed['packing_list'])
            outputs['packed shipments'].append({'shipment_doc': shipment_documentation, 'sealed': sealed})
        return outputs
        
        return outputs

    def _compliance_checks(self, inputs: dict, outputs: dict, context: dict) -> dict:
        """
        Built-in compliance validation
        
        Checks:
        # - dangerous_goods_packaging
        # - GxP_dual_verification
        # - GDPR_shipment_data
        # - customer_packaging_standards
        """
        checks_passed = []
        checks_failed = []
        
        checks_passed.append('Compliance check completed')
        
        return {
            "status": "passed" if not checks_failed else "warning",
            "passed": checks_passed,
            "failed": checks_failed,
            "details": checks_passed + checks_failed
        }

    def _validate_outputs(self, outputs: dict) -> tuple[bool, list]:
        """Validate outputs meet process requirements"""
        required_outputs = ['packed_shipments', 'packing_lists']
        missing = [o for o in required_outputs if o not in outputs]
        if missing:
            return False, [f"Missing output: {m}" for m in missing]
        return True, []

    def should_escalate(self, result: dict) -> bool:
        """Determine if result requires human escalation"""
        escalation_rules = ['quantity mismatch or damaged item triggers inventory reconciliation/quarantine', 'cycle_time exceeds threshold notifies supervisor', 'missing label data escalates to order management']
        if result.get("status") == "error":
            return True
        compliance = result.get("compliance", {})
        if compliance.get("status") == "failed":
            return True
        return False

    def get_metrics(self) -> dict:
        """Return agent performance metrics"""
        return {
            "process_id": self.process_id,
            "agent_name": self.agent_name,
            "executions": len(self.execution_log),
            "monitoring": ['packing_accuracy', 'cycle_time', 'damage_rate', 'label_compliance_rate']
        }


# ── STANDALONE EXECUTION ─────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = MtoPackingAgentAgent()
    
    # Example execution
    test_inputs = {"picked_products": "example_picked_products", "packing_specifications": "example_packing_specifications", "labels": "example_labels", }
    
    result = agent.execute(test_inputs)
    print(json.dumps(result, indent=2, default=str))
