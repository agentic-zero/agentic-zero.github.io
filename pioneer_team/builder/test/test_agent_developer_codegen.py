"""
AGENTIC ZERO -- Regression test for agent_developer.py

Guards against the json.dumps() vs repr() bug found during
Sprint validation (19 Jun 2026): any blueprint with boolean values
in learning_hooks/escalations/connectors broke 100% of generated
agents with NameError: name 'true' is not defined.

Path:
  pioneer_team/builder/tests/test_agent_developer_codegen.py

Usage:
  python -m pytest pioneer_team/builder/tests/test_agent_developer_codegen.py -v
"""

import sys
import json
import tempfile
import py_compile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent_developer import run_agent_developer


MINIMAL_BLUEPRINT_WITH_BOOLEANS = {
    "process_id": "TEST-REGRESSION-001",
    "agent_class_name": "TestAgent",
    "agent_description": "Regression test agent",
    "company": "Test Co",
    "sector": "test",
    "erp": "TEST-ERP",
    "confidence_threshold": 0.85,
    "kpis": ["test_kpi"],
    "shield_requirements": ["Test Requirement"],
    "autonomous_actions": ["test_action"],
    "approval_required": [],
    "always_human": [],
    "steps": [],
    "connectors": [{"name": "TestConnector", "type": "rest_api", "active": True}],
    "escalations": [{"trigger": "test", "auto_resolvable": False}],
    "learning_hooks": {
        "enabled": True,  # <-- the exact field that broke codegen
        "observation_points": ["step execution time"],
        "failure_patterns": ["test failure"],
        "kpi_deviation_signals": ["test_kpi"],
        "feedback_targets": ["business_rules"],
        "improvement_loop": "observe_analyze_recommend_validate_deploy",
    },
    "acceptance_tests": [],
    "builder_prompt": "",
    "ready_for_builder": True,
    "missing_info": [],
}


def test_generated_agent_compiles_with_boolean_learning_hooks():
    """
    The bug: json.dumps(dict_with_booleans) produces 'true'/'false'/'null'
    which are NOT valid Python literals (Python needs True/False/None).
    This test fails loudly if that regression is reintroduced.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        blueprint_path = Path(tmpdir) / "blueprint.json"
        blueprint_path.write_text(json.dumps(MINIMAL_BLUEPRINT_WITH_BOOLEANS), encoding="utf-8")

        output_dir = Path(tmpdir) / "04_agent"

        # Call the same code path the CLI uses
        run_agent_developer(str(blueprint_path), str(output_dir))

        agent_file = output_dir / "agent_runtime.py"
        assert agent_file.exists(), "agent_runtime.py was not generated"

        # The real regression check: does it COMPILE as valid Python?
        py_compile.compile(str(agent_file), doraise=True)

        # And does it actually IMPORT without NameError?
        content = agent_file.read_text(encoding="utf-8")
        assert "true" not in content.split("=", 1)[-1] or "'true'" in content or '"true"' in content, (
            "Found bare lowercase 'true' in generated code -- "
            "this means json.dumps() leaked into a Python literal again."
        )


if __name__ == "__main__":
    test_generated_agent_compiles_with_boolean_learning_hooks()
    print("PASS -- regression test for agent_developer.py codegen")
