# SOP — Proceso OTC para empresa de transporte de distribucion. Un unico operador full-t
**Process ID:** CUSTOMER-ORDER-TO-CASH-OTC
**Framework:** CUSTOMER_FUNCTIONAL_ANALYSIS | **Domain:** transport_distribution
**Generated:** 2026-06-17

## Purpose
Proceso OTC para empresa de transporte de distribucion. Un unico operador full-time gestiona 50 ordenes diarias (ZEST x35 + ZURG x8 + ZINT x5 + ZDEV x2) combinando transacciones SAP ECC y un TMS externo para asignacion de rutas. Los puntos criticos son la validacion de credito (FD32), la disponibilidad de capacidad de transporte en el TMS (metros lineales), y la verificacion de precios de condicion (VK11). El 90pct de clientes son B2B con pago a credito 30-60 dias. El 10pct son nuevos clientes con pago anticipado.

## Triggers
- New customer_order received in SAP VBAK/VBAP with order_type_code ZEST/ZURG/ZINT/ZDEV

## Inputs Required
- customer_order
- order_type_code
- delivery_address
- time_window
- weight_kg
- linear_meters
- normalized_order
- mandatory_fields_list
- customer_id
- order_value
- material_transport
- quoted_price
- route_date
- order_type
- order_id

## Process Steps
1. IF overdue_days > 15 OR sap_credit_blocked THEN block_order and escalate_to_finance
2. IF price_discrepancy_pct > 1 THEN block_order with reason price_discrepancy and escalate_to_ops
3. IF NOT capacity_available THEN generate_draft_email with 2 alternative_slots and escalate_to_ops
4. IF order_type == ZINT AND NOT international_docs THEN escalate_to_ops for documentation
5. IF order_type == ZURG THEN assign highest TMS priority for next-day 10AM delivery
6. IF customer_new AND payment_anticipado THEN require bank_statement_match before release

## Expected Outputs
- normalized_order
- order_type_classified
- data_validation_result
- issues_list
- credit_status
- overdue_days
- credit_limit
- credit_used
- condition_price
- price_discrepancy_pct
- price_valid
- capacity_available
- route_id
- alternative_slots
- invoice_document

## Business Rules
- Credit overdue >15 days: never autonomous processing, always escalate
- Price tolerance exactly 1pct vs VK11 condition
- TMS capacity measured in linear_meters; ZURG has max priority
- 90pct B2B credit 30-60 days: auto VF01/VF04 after transport
- ZINT requires CMR and Packing List before proceeding
- All autonomous actions logged with AuditEntry including timestamp, rule, confidence

## Exception Handling
- Missing TMS capacity: draft email with alternatives, do not cancel
- Credit block or overdue: block and notify finance only
- Price discrepancy >1pct: block with reason and notify ops
- New prepay customer without confirmed statement: queue for operator match
- ZINT missing docs: block until docs provided
- TMS or SAP connection error: escalate with retry and notify

## Success Criteria
- Invoice_document created
- route_id assigned
- confirmation_sent timestamp recorded
- tasa_automatizacion_pct >= 80 and tiempo_ciclo_minutos < 5

## Compliance Requirements
- EU AI Act
- ISO/IEC 42001
- NIST AI RMF
- Identity & Access
- Real-time Audit Trails
- Escalation Pathways
- Human Accountability
- AI Risk Classification
- Explainability
- Model Monitoring
- Action Thresholds
- Fail-Safes