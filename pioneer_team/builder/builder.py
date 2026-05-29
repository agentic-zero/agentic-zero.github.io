"""
AGENTIC ZERO — PIONEER TEAM
Agent 3: BUILDER
Role: Convert validated processes into functional agents (IBM Bob pattern)
Input: Validated ProcessEntry from Architect
Output: Functional agent code + ontology + tests

IBM Bob Pattern:
  Process Description → SOP (Standard Operating Procedure)
  SOP → Ontology (entities, relationships, rules)
  Ontology → Agent (executable, testable, deployable)

Architecture: API-first, queue-ready, zero-cost (Groq free tier)
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from loguru import logger
import litellm

load_dotenv()

# ── LOGGING ───────────────────────────────────────────────────────────────────
logger.add(
    "logs/builder_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class ProcessOntology(BaseModel):
    """Ontology extracted from a process — the structured knowledge layer"""

    process_id: str
    entities: list[str]  # Key entities involved
    relationships: list[str]  # How entities relate
    decision_points: list[str]  # Where decisions are made
    rules: list[str]  # Business rules and constraints
    exceptions: list[str]  # Exception cases to handle
    data_requirements: list[str]  # Data needed to execute
    triggers: list[str]  # What starts the process
    success_criteria: list[str]  # How to know it succeeded
    failure_modes: list[str]  # How it can fail


class AgentSpec(BaseModel):
    """Specification for the generated agent"""

    process_id: str
    agent_name: str
    agent_type: str  # reactive / proactive / hybrid
    capabilities: list[str]  # What the agent can do
    tools_required: list[str]  # External tools/APIs needed
    decision_logic: str  # How the agent makes decisions
    escalation_rules: list[str]  # When to escalate to human
    monitoring_metrics: list[str]  # What to track at runtime
    compliance_checks: list[str]  # Compliance validations built-in


class BuilderResult(BaseModel):
    """Complete output from Builder for a process"""

    process_id: str
    builder_timestamp: str
    ontology: ProcessOntology
    agent_spec: AgentSpec
    agent_code: str  # Python code for the agent
    sop: str  # Standard Operating Procedure
    test_cases: list[str]  # Test scenarios
    deployment_notes: str
    ready_for_packager: bool
    estimated_token_cost: float  # Estimated cost per execution


# ── BUILDER CONFIGURATION ────────────────────────────────────────────────────
BUILDER_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 6000,
    "temperature": 0.2,
    "rate_limit_rpm": 1,
    "rate_limit_rpd": 1400,
}

# ── AGENT TEMPLATES ───────────────────────────────────────────────────────────
AGENT_BASE_TEMPLATE = '''"""
AGENTIC ZERO — Generated Agent
Process: {process_id}
Name: {agent_name}
Framework: {framework}
Domain: {domain}
Generated: {timestamp}
Compliance: {compliance}

DO NOT EDIT MANUALLY — Regenerate via Builder Agent
"""

import os
import json
from datetime import datetime
from typing import Optional
from loguru import logger


class {class_name}:
    """
    Agent for: {process_name}
    
    {description}
    
    Capabilities:
{capabilities}
    
    Compliance: {compliance}
    """

    def __init__(self, config: dict = None):
        self.process_id = "{process_id}"
        self.agent_name = "{agent_name}"
        self.config = config or {{}}
        self.execution_log = []
        logger.info(f"Agent {{self.agent_name}} initialized")

    def validate_inputs(self, inputs: dict) -> tuple[bool, list]:
        """Validate required inputs before execution"""
        required = {required_inputs}
        missing = [r for r in required if r not in inputs]
        if missing:
            return False, [f"Missing required input: {{m}}" for m in missing]
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
            return {{
                "status": "error",
                "errors": errors,
                "outputs": {{}},
                "audit_trail": audit_trail
            }}
        
        audit_trail.append({{
            "step": "input_validation",
            "status": "passed",
            "timestamp": datetime.now().isoformat()
        }})

        try:
            # Step 2: Execute process logic
            outputs = self._process_logic(inputs, context or {{}})
            
            audit_trail.append({{
                "step": "process_execution",
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }})

            # Step 3: Compliance checks
            compliance_result = self._compliance_checks(inputs, outputs, context or {{}})
            audit_trail.append({{
                "step": "compliance_check",
                "status": compliance_result["status"],
                "details": compliance_result.get("details", []),
                "timestamp": datetime.now().isoformat()
            }})

            # Step 4: Validate outputs
            output_valid, output_errors = self._validate_outputs(outputs)
            if not output_valid:
                return {{
                    "status": "error",
                    "errors": output_errors,
                    "outputs": outputs,
                    "audit_trail": audit_trail
                }}

            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {{
                "status": "success",
                "outputs": outputs,
                "compliance": compliance_result,
                "execution_time_seconds": execution_time,
                "audit_trail": audit_trail,
                "agent": self.agent_name,
                "process_id": self.process_id,
                "timestamp": datetime.now().isoformat()
            }}

        except Exception as e:
            logger.error(f"Agent {{self.agent_name}} execution failed: {{e}}")
            audit_trail.append({{
                "step": "execution",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }})
            return {{
                "status": "error",
                "errors": [str(e)],
                "outputs": {{}},
                "audit_trail": audit_trail
            }}

    def _process_logic(self, inputs: dict, context: dict) -> dict:
        """
        Core process logic — generated from ontology
        
        Decision points:
{decision_points}
        
        Business rules:
{rules}
        """
        outputs = {{}}
        
{process_logic}
        
        return outputs

    def _compliance_checks(self, inputs: dict, outputs: dict, context: dict) -> dict:
        """
        Built-in compliance validation
        
        Checks:
{compliance_checks}
        """
        checks_passed = []
        checks_failed = []
        
{compliance_logic}
        
        return {{
            "status": "passed" if not checks_failed else "warning",
            "passed": checks_passed,
            "failed": checks_failed,
            "details": checks_passed + checks_failed
        }}

    def _validate_outputs(self, outputs: dict) -> tuple[bool, list]:
        """Validate outputs meet process requirements"""
        required_outputs = {required_outputs}
        missing = [o for o in required_outputs if o not in outputs]
        if missing:
            return False, [f"Missing output: {{m}}" for m in missing]
        return True, []

    def should_escalate(self, result: dict) -> bool:
        """Determine if result requires human escalation"""
        escalation_rules = {escalation_rules}
        if result.get("status") == "error":
            return True
        compliance = result.get("compliance", {{}})
        if compliance.get("status") == "failed":
            return True
        return False

    def get_metrics(self) -> dict:
        """Return agent performance metrics"""
        return {{
            "process_id": self.process_id,
            "agent_name": self.agent_name,
            "executions": len(self.execution_log),
            "monitoring": {monitoring_metrics}
        }}


# ── STANDALONE EXECUTION ─────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = {class_name}()
    
    # Example execution
    test_inputs = {test_inputs}
    
    result = agent.execute(test_inputs)
    print(json.dumps(result, indent=2, default=str))
'''


# ── RATE LIMITER ──────────────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, rpm: int = 1):
        self.rpm = rpm
        self.min_interval = 60.0 / rpm
        self.last_call = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.debug(f"Rate limiter: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        self.last_call = time.time()


rate_limiter = RateLimiter(rpm=BUILDER_CONFIG["rate_limit_rpm"])


# ── LLM CALLER ────────────────────────────────────────────────────────────────
def call_llm(prompt: str, expect_json: bool = True) -> str:
    rate_limiter.wait()
    try:
        response = litellm.completion(
            model=BUILDER_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=BUILDER_CONFIG["max_tokens"],
            temperature=BUILDER_CONFIG["temperature"],
            api_key=os.getenv("GROQ_API_KEY"),
        )
        content = response.choices[0].message.content.strip()
        if expect_json and content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        return content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ── PROMPTS ───────────────────────────────────────────────────────────────────
def build_ontology_prompt(process: dict) -> str:
    return f"""You are a knowledge engineer building an ontology for an AI agent.

PROCESS:
{json.dumps(process, indent=2)}

Extract the ontology for this process. Return ONLY a JSON object:
{{
  "entities": ["entity1", "entity2"],
  "relationships": ["entity1 has entity2", "entity1 triggers entity2"],
  "decision_points": ["IF condition THEN action"],
  "rules": ["rule1: constraint or requirement"],
  "exceptions": ["exception case and how to handle it"],
  "data_requirements": ["data field: type and source"],
  "triggers": ["what starts this process"],
  "success_criteria": ["how to know the process succeeded"],
  "failure_modes": ["how and why this process can fail"]
}}

Be specific and actionable. Each item should be implementable in code."""


def build_agent_spec_prompt(process: dict, ontology: dict) -> str:
    return f"""You are an AI agent architect designing an autonomous agent.

PROCESS: {process.get("name")}
ONTOLOGY: {json.dumps(ontology, indent=2)}
COMPLIANCE: {", ".join(process.get("compliance_flags", []))}

Design the agent specification. Return ONLY a JSON object:
{{
  "agent_name": "descriptive_snake_case_name",
  "agent_type": "reactive/proactive/hybrid",
  "capabilities": ["capability1", "capability2"],
  "tools_required": ["tool or API needed"],
  "decision_logic": "brief description of how agent decides",
  "escalation_rules": ["when to escalate to human"],
  "monitoring_metrics": ["metric to track at runtime"],
  "compliance_checks": ["compliance validation to run"]
}}

Agent type guide:
- reactive: responds to events/requests
- proactive: monitors and acts autonomously
- hybrid: both reactive and proactive"""


def build_process_logic_prompt(process: dict, ontology: dict, agent_spec: dict) -> str:
    return f"""You are a Python developer implementing an AI agent.

PROCESS: {process.get("name")}
INPUTS: {process.get("inputs", [])}
OUTPUTS: {process.get("outputs", [])}
DECISION POINTS: {ontology.get("decision_points", [])}
RULES: {ontology.get("rules", [])}

Write the Python implementation for these two methods.
Return ONLY a JSON object with the code as strings:
{{
  "process_logic": "Python code for _process_logic method body (indented with 8 spaces)",
  "compliance_logic": "Python code for _compliance_checks method body (indented with 8 spaces)"
}}

Rules:
- Use only standard Python (no external imports)
- outputs dict must contain: {process.get("outputs", [])}
- Add comments explaining each step
- Handle edge cases
- Keep it practical and executable"""


def build_test_cases_prompt(process: dict, agent_spec: dict) -> str:
    return f"""You are a QA engineer writing test cases for an AI agent.

AGENT: {agent_spec.get("agent_name")}
PROCESS: {process.get("name")}
INPUTS: {process.get("inputs", [])}
OUTPUTS: {process.get("outputs", [])}
FAILURE MODES: []

Write 5 test scenarios. Return ONLY a JSON array of strings:
["Test 1: description of happy path test",
 "Test 2: description of edge case",
 "Test 3: description of failure case",
 "Test 4: description of compliance check",
 "Test 5: description of escalation scenario"]"""


# ── CODE GENERATOR ────────────────────────────────────────────────────────────
def generate_agent_code(
    process: dict, ontology: dict, agent_spec: dict, logic: dict
) -> str:
    """Generate Python agent code from template"""
    process_id = process.get("process_id", "UNKNOWN")
    agent_name = agent_spec.get("agent_name", "generic_agent")
    class_name = "".join(w.capitalize() for w in agent_name.split("_")) + "Agent"

    # Format decision points and rules for docstring
    decision_points = "\n".join(
        [f"        # - {dp}" for dp in ontology.get("decision_points", [])]
    )
    rules = "\n".join([f"        # - {r}" for r in ontology.get("rules", [])])
    compliance_checks_doc = "\n".join(
        [f"        # - {c}" for c in agent_spec.get("compliance_checks", [])]
    )
    capabilities = "\n".join(
        [f"    #   - {c}" for c in agent_spec.get("capabilities", [])]
    )
    monitoring_metrics = str(agent_spec.get("monitoring_metrics", []))
    escalation_rules = str(agent_spec.get("escalation_rules", []))

    # Required inputs/outputs
    required_inputs = str(
        [i.replace(" ", "_").lower() for i in process.get("inputs", [])[:3]]
    )
    required_outputs = str(
        [o.replace(" ", "_").lower() for o in process.get("outputs", [])[:2]]
    )

    # Test inputs example
    test_inputs = "{"
    for inp in process.get("inputs", [])[:3]:
        key = inp.replace(" ", "_").lower()
        test_inputs += f'"{key}": "example_{key}", '
    test_inputs += "}"

    # Process logic from LLM
    process_logic = logic.get(
        "process_logic",
        "        # TODO: implement process logic\n        outputs['result'] = 'processed'",
    )
    compliance_logic = logic.get(
        "compliance_logic",
        "        checks_passed.append('No compliance checks defined')",
    )

    code = AGENT_BASE_TEMPLATE.format(
        process_id=process_id,
        agent_name=agent_name,
        class_name=class_name,
        framework=process.get("framework", "SCOR"),
        domain=process.get("domain", ""),
        timestamp=datetime.now().isoformat(),
        compliance=", ".join(process.get("compliance_flags", ["none"])),
        process_name=process.get("name", ""),
        description=process.get("description", ""),
        capabilities=capabilities,
        required_inputs=required_inputs,
        required_outputs=required_outputs,
        decision_points=decision_points,
        rules=rules,
        process_logic=process_logic,
        compliance_checks=compliance_checks_doc,
        compliance_logic=compliance_logic,
        escalation_rules=escalation_rules,
        monitoring_metrics=monitoring_metrics,
        test_inputs=test_inputs,
    )

    return code


def build_sop(process: dict, ontology: dict) -> str:
    """Generate Standard Operating Procedure document"""
    lines = [
        f"# SOP — {process.get('name', 'Unknown Process')}",
        f"**Process ID:** {process.get('process_id', 'UNKNOWN')}",
        f"**Framework:** {process.get('framework', '')} | **Domain:** {process.get('domain', '')}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Purpose",
        process.get("description", ""),
        "",
        "## Triggers",
    ]
    for t in ontology.get("triggers", []):
        lines.append(f"- {t}")
    lines += ["", "## Inputs Required"]
    for i in process.get("inputs", []):
        lines.append(f"- {i}")
    lines += ["", "## Process Steps"]
    for j, dp in enumerate(ontology.get("decision_points", []), 1):
        lines.append(f"{j}. {dp}")
    lines += ["", "## Expected Outputs"]
    for o in process.get("outputs", []):
        lines.append(f"- {o}")
    lines += ["", "## Business Rules"]
    for r in ontology.get("rules", []):
        lines.append(f"- {r}")
    lines += ["", "## Exception Handling"]
    for e in ontology.get("exceptions", []):
        lines.append(f"- {e}")
    lines += ["", "## Success Criteria"]
    for s in ontology.get("success_criteria", []):
        lines.append(f"- {s}")
    lines += ["", "## Compliance Requirements"]
    for c in process.get("compliance_flags", []):
        lines.append(f"- {c}")
    return "\n".join(lines)


# ── LIBRARY LOADER / WRITER ───────────────────────────────────────────────────
def load_process(process_id: str) -> Optional[dict]:
    """Load a specific process from library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        proc_file = library_path / folder / "processes" / f"{process_id}.json"
        if proc_file.exists():
            with open(proc_file, "r", encoding="utf-8") as f:
                return json.load(f)
    logger.error(f"Process not found in library: {process_id}")
    return None


def save_builder_result(result: BuilderResult, process: dict):
    """Save Builder results to library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    framework = process.get("framework", "scor").lower()

    if "scor" in framework:
        folder = library_path / "scor"
    elif "iso" in framework:
        folder = library_path / "iso"
    else:
        folder = library_path / "sector_specific"

    # Save full result JSON
    agents_folder = folder / "agents"
    agents_folder.mkdir(exist_ok=True)
    result_file = agents_folder / f"{result.process_id}_builder.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    # Save agent Python file
    code_folder = folder / "agents" / "code"
    code_folder.mkdir(exist_ok=True)
    agent_name = result.agent_spec.agent_name
    code_file = code_folder / f"{agent_name}.py"
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(result.agent_code)

    # Save SOP as markdown
    sop_folder = folder / "sops"
    sop_folder.mkdir(exist_ok=True)
    sop_file = sop_folder / f"{result.process_id}_sop.md"
    with open(sop_file, "w", encoding="utf-8") as f:
        f.write(result.sop)

    logger.info(f"Builder result saved: {result_file}")
    logger.info(f"Agent code saved: {code_file}")
    logger.info(f"SOP saved: {sop_file}")
    return result_file


# ── MAIN BUILDER FUNCTION ─────────────────────────────────────────────────────
def build_agent(process_id: str) -> Optional[BuilderResult]:
    """
    Main Builder function: IBM Bob pattern
    Process → Ontology → Agent Spec → Code + SOP + Tests

    Args:
        process_id: ID of the process to build (e.g. SCOR-P1.1)

    Returns:
        BuilderResult with complete agent package
    """
    logger.info(f"Builder starting: {process_id}")

    # Load process from library
    process = load_process(process_id)
    if not process:
        logger.error(f"Cannot build agent: process {process_id} not found")
        return None

    logger.info(f"Building agent for: {process.get('name')}")

    try:
        # STEP 1 — Extract ontology
        logger.info("Step 1/4: Extracting ontology...")
        prompt = build_ontology_prompt(process)
        response = call_llm(prompt, expect_json=True)
        ontology_data = json.loads(response)
        ontology = ProcessOntology(
            process_id=process_id,
            entities=ontology_data.get("entities", []),
            relationships=ontology_data.get("relationships", []),
            decision_points=ontology_data.get("decision_points", []),
            rules=ontology_data.get("rules", []),
            exceptions=ontology_data.get("exceptions", []),
            data_requirements=ontology_data.get("data_requirements", []),
            triggers=ontology_data.get("triggers", []),
            success_criteria=ontology_data.get("success_criteria", []),
            failure_modes=ontology_data.get("failure_modes", []),
        )
        logger.success(
            f"Ontology extracted: {len(ontology.entities)} entities, {len(ontology.decision_points)} decision points"
        )

        # STEP 2 — Design agent spec
        logger.info("Step 2/4: Designing agent specification...")
        prompt = build_agent_spec_prompt(process, ontology.model_dump())
        response = call_llm(prompt, expect_json=True)
        spec_data = json.loads(response)
        agent_spec = AgentSpec(
            process_id=process_id,
            agent_name=spec_data.get(
                "agent_name", f"agent_{process_id.lower().replace('-', '_')}"
            ),
            agent_type=spec_data.get("agent_type", "reactive"),
            capabilities=spec_data.get("capabilities", []),
            tools_required=spec_data.get("tools_required", []),
            decision_logic=spec_data.get("decision_logic", ""),
            escalation_rules=spec_data.get("escalation_rules", []),
            monitoring_metrics=spec_data.get("monitoring_metrics", []),
            compliance_checks=spec_data.get("compliance_checks", []),
        )
        logger.success(f"Agent spec: {agent_spec.agent_name} ({agent_spec.agent_type})")

        # STEP 3 — Generate process logic
        logger.info("Step 3/4: Generating process logic...")
        prompt = build_process_logic_prompt(
            process, ontology.model_dump(), agent_spec.model_dump()
        )
        response = call_llm(prompt, expect_json=True)
        logic = json.loads(response)
        logger.success("Process logic generated")

        # STEP 4 — Generate test cases
        logger.info("Step 4/4: Generating test cases...")
        prompt = build_test_cases_prompt(process, agent_spec.model_dump())
        response = call_llm(prompt, expect_json=True)
        test_cases = json.loads(response)
        logger.success(f"{len(test_cases)} test cases generated")

        # Generate agent code from template
        agent_code = generate_agent_code(
            process, ontology.model_dump(), agent_spec.model_dump(), logic
        )
        sop = build_sop(process, ontology.model_dump())

        # Estimate token cost per execution
        avg_tokens = 500
        cost_per_1k = 0.0  # Groq free tier
        estimated_cost = (avg_tokens / 1000) * cost_per_1k

        result = BuilderResult(
            process_id=process_id,
            builder_timestamp=datetime.now().isoformat(),
            ontology=ontology,
            agent_spec=agent_spec,
            agent_code=agent_code,
            sop=sop,
            test_cases=test_cases if isinstance(test_cases, list) else [],
            deployment_notes=f"Agent ready for deployment. Compliance: {', '.join(process.get('compliance_flags', ['none']))}",
            ready_for_packager=True,
            estimated_token_cost=estimated_cost,
        )

        # Save to library
        save_builder_result(result, process)

        logger.success(
            f"Builder complete: {process_id} | "
            f"Agent: {agent_spec.agent_name} | "
            f"Ready for Packager: {result.ready_for_packager}"
        )

        return result

    except Exception as e:
        logger.error(f"Builder failed for {process_id}: {e}")
        return None


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def run_builder(process_ids: list[str]):
    """Run Builder from command line or as API"""
    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — BUILDER AGENT")
    logger.info(f"Processes to build: {process_ids}")
    logger.info(f"Model: {BUILDER_CONFIG['model']}")
    logger.info(f"Pattern: IBM Bob (Process → Ontology → Agent)")
    logger.info("=" * 60)

    results = []
    for pid in process_ids:
        logger.info(f"Building: {pid}")
        result = build_agent(pid)
        if result:
            results.append(result)
            print(f"\n✅ {pid} → {result.agent_spec.agent_name}")
            print(f"   Type: {result.agent_spec.agent_type}")
            print(f"   Capabilities: {len(result.agent_spec.capabilities)}")
            print(f"   Test cases: {len(result.test_cases)}")
            print(f"   Ready for Packager: {result.ready_for_packager}")
        else:
            print(f"\n❌ {pid} → Build failed")

    print(f"\n{'=' * 40}")
    print(f"Builder complete: {len(results)}/{len(process_ids)} agents built")
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("\nUsage: python builder.py PROCESS_ID [PROCESS_ID2 ...]")
        print("Example: python builder.py SCOR-P1.1")
        print("Example: python builder.py SCOR-P1.1 SCOR-P1.2 SCOR-S1.1\n")
        sys.exit(1)

    process_ids = sys.argv[1:]
    run_builder(process_ids)
