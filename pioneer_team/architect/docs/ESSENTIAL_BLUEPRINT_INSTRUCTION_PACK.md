# AGENTIC ZERO — Essential Blueprint Instruction Pack

## Purpose

Defines the standard output contract for every Essential customer package.

Pipeline:

AUDIT ZERO / Fast Track → Functional Translator → SIOP Generator → SIOP Validator → Architect SIOP Bridge → Builder / Agent Developer → Packager → Guardian → Auditor → Essential Client Package

The objective is to make every customer output look like the Inmaculada package, but adapted to the specific company, process, sector, ERP, data, rules, exceptions and autonomy level.

## Standard Essential Package Output

Every Essential package must generate:

1. Functional Analysis JSON
2. SIOP Internal JSON
3. SIOP Validation JSON
4. Architect Blueprint JSON
5. Agent Runtime Python
6. SOP Markdown
7. Integration Guide Markdown
8. Dashboard HTML
9. ROI Calculator HTML
10. Escalation Policy Markdown
11. Guardian Certificate TXT/JSON
12. Auditor Decision JSON
13. Delivery Manifest JSON
14. Client Executive Summary Markdown

## Required Client Inputs

```json
{
  "company": "",
  "contact_name": "",
  "role": "",
  "sector": "",
  "erp": "",
  "process_name": "",
  "domains": [],
  "subprocesses": [],
  "volume": "",
  "team_size": "",
  "manual_time_per_transaction_min": "",
  "business_rules": [],
  "critical_exceptions": [],
  "data_used": [],
  "systems_involved": [],
  "process_map_uploaded": false,
  "documentation_score": 0,
  "recommended_route": ""
}
```

## Essential Gates

### Gate 1 — Functional Readiness

Valid when business context, process context, steps, systems, data, rules and exceptions exist.

### Gate 2 — SIOP Readiness

Valid when the eight core SIOP sections exist:

1. Executive Summary
2. Business Context
3. Process Flow
4. Data Requirements
5. Business Rules
6. Compliance
7. Autonomy Design
8. Acceptance Criteria

Learning Hooks must also be included.

### Gate 3 — Blueprint Readiness

Valid when blueprint contains:

- process_id
- agent_class_name
- steps
- connectors
- escalations
- shield_requirements
- learning_hooks
- acceptance_tests
- builder_prompt

### Gate 4 — Build Readiness

Valid when agent contains:

- executable runtime
- dry-run mode
- input/output validation
- audit trail
- escalation handling
- connector placeholders or live connectors
- dashboard events
- env configuration

### Gate 5 — Delivery Readiness

Deliver only when:

- Guardian has certified or conditionally certified
- Auditor decision is AUTO_APPROVE or APPROVE_WITH_CONDITIONS
- Delivery Manifest is complete
- Escalation Policy exists
- ROI Calculator is parameterized
- Dashboard is customer-specific

## Folder Contract

```text
clients/{client_slug}/{process_slug}/essential_package/
├── 01_functional_analysis/functional_analysis.json
├── 02_siop/siop_internal.json
├── 02_siop/siop_validation.json
├── 03_blueprint/architect_blueprint.json
├── 04_agent/agent_runtime.py
├── 04_agent/connectors/
├── 04_agent/tests/
├── 04_agent/.env.example
├── 05_delivery/sop.md
├── 05_delivery/integration_guide.md
├── 05_delivery/escalation_policy.md
├── 05_delivery/client_executive_summary.md
├── 05_delivery/dashboard.html
├── 05_delivery/roi_calculator.html
├── 06_compliance/guardian_certificate.txt
├── 06_compliance/guardian_result.json
├── 06_compliance/auditor_decision.json
└── delivery_manifest.json
```

## Product Rule

The package must never look generic. Every artifact must include customer-specific company, process, sector, ERP, volume, rules, exceptions, data objects, autonomy boundaries, escalation path, ROI assumptions and compliance profile.

## Living Enterprise Rule

Every generated package must include observation points, learning hooks, failure patterns, KPI deviation signals, feedback targets and improvement loop.

## Final Output Decision

One of:

- DELIVERABLE
- DELIVERABLE_WITH_CONDITIONS
- BLOCKED_MISSING_INFORMATION
- BLOCKED_COMPLIANCE
- BLOCKED_BUILD_FAILURE

## Mantra

Does this make it feel like a living enterprise?
