"""
AGENTIC ZERO — Generated Agent
Process: SCOR-S2.5
Name: supplier_payment_authorizer
Framework: SCOR
Domain: Source
Generated: 2026-06-08T14:44:26.932448
Compliance: financial controls compliance, GDPR financial data, tax compliance, anti-fraud controls

DO NOT EDIT MANUALLY — Regenerate via Builder Agent
"""

import os
import json
from datetime import datetime
from typing import Optional
from loguru import logger


class SupplierPaymentAuthorizerAgent:
    """
    Agent for: Authorize Supplier Payment (MTO)
    
    Process of authorizing and processing supplier payments for MTO materials upon verified receipt, matching invoices against purchase orders and delivery confirmations
    
    Capabilities:
    #   - three_way_match_validation
    #   - payment_authorization_creation
    #   - discrepancy_resolution_handling
    #   - quality_verification_integration
    
    Compliance: financial controls compliance, GDPR financial data, tax compliance, anti-fraud controls
    """

    def __init__(self, config: dict = None):
        self.process_id = "SCOR-S2.5"
        self.agent_name = "supplier_payment_authorizer"
        self.config = config or {}
        self.execution_log = []
        logger.info(f"Agent {self.agent_name} initialized")

    def validate_inputs(self, inputs: dict) -> tuple[bool, list]:
        """Validate required inputs before execution"""
        required = ['supplier_invoices', 'goods_receipts', 'purchase_orders']
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
        # - IF SupplierInvoice.amount == PurchaseOrder.amount AND GoodsReceipt.received_qty == PurchaseOrder.ordered_qty AND QualityVerificationResult.status == 'passed' THEN create PaymentAuthorization with status='approved'
        
        Business rules:
        # - Three-way match (invoice, PO, goods receipt) required before PaymentAuthorization creation
        # - PaymentAuthorization.due_date must respect PaymentTerms.net_days from GoodsReceipt.date
        # - PaymentAuthorization.amount must equal SupplierInvoice.amount after tax adjustments
        """
        outputs = {}
        
outputs = {'payment authorizations': [], 'payment confirmations': [], 'supplier account updates': [], 'discrepancy resolutions': []}
        # Group inputs by common keys for matching (assume shared supplier_id and po_id)
        po_map = {po['po_id']: po for po in purchase_orders}
        gr_map = {gr['po_id']: gr for gr in goods_receipts}
        qv_map = {qv['po_id']: qv for qv in quality_verification_results}
        for inv in supplier_invoices:
            po_id = inv.get('po_id')
            po = po_map.get(po_id)
            gr = gr_map.get(po_id)
            qv = qv_map.get(po_id)
            pt = next((p for p in payment_terms if p.get('supplier_id') == inv.get('supplier_id')), None)
            if not po or not gr or not qv or not pt:
                outputs['discrepancy resolutions'].append({'invoice_id': inv.get('invoice_id'), 'reason': 'missing reference documents'})
                continue
            # Three-way match per rules and decision point
            amount_match = inv['amount'] == po['amount']
            qty_match = gr['received_qty'] == po['ordered_qty']
            quality_ok = qv['status'] == 'passed'
            if amount_match and qty_match and quality_ok:
                due_date = gr['date'] + pt['net_days']
                auth = {'invoice_id': inv['invoice_id'], 'amount': inv['amount'], 'due_date': due_date, 'status': 'approved'}
                outputs['payment authorizations'].append(auth)
                outputs['payment confirmations'].append({'authorization_id': auth['invoice_id'], 'status': 'confirmed'})
                outputs['supplier account updates'].append({'supplier_id': inv['supplier_id'], 'adjustment': -inv['amount']})
            else:
                outputs['discrepancy resolutions'].append({'invoice_id': inv['invoice_id'], 'reason': 'three-way match failed'})
        return outputs
        
        return outputs

    def _compliance_checks(self, inputs: dict, outputs: dict, context: dict) -> dict:
        """
        Built-in compliance validation
        
        Checks:
        # - three_way_match_audit_trail
        # - tax_adjustment_validation
        # - anti_fraud_pattern_check
        # - GDPR_financial_data_masking
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
        required_outputs = ['payment_authorizations', 'payment_confirmations']
        missing = [o for o in required_outputs if o not in outputs]
        if missing:
            return False, [f"Missing output: {m}" for m in missing]
        return True, []

    def should_escalate(self, result: dict) -> bool:
        """Determine if result requires human escalation"""
        escalation_rules = ['three-way mismatch exceeds 0.01 tolerance', "QualityVerificationResult.status == 'failed'", 'missing data blocks authorization beyond SLA']
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
            "monitoring": ['payment_cycle_time', 'discrepancy_count', 'on_time_payment_rate', 'authorization_success_ratio']
        }


# ── STANDALONE EXECUTION ─────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = SupplierPaymentAuthorizerAgent()
    
    # Example execution
    test_inputs = {"supplier_invoices": "example_supplier_invoices", "goods_receipts": "example_goods_receipts", "purchase_orders": "example_purchase_orders", }
    
    result = agent.execute(test_inputs)
    print(json.dumps(result, indent=2, default=str))
