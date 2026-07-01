# client_access/access_boundary.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class AccessDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ResourceClass(str, Enum):
    CUSTOMER_VISIBLE = "CUSTOMER_VISIBLE"
    CUSTOMER_PACKAGE = "CUSTOMER_PACKAGE"
    CUSTOMER_REPORT = "CUSTOMER_REPORT"
    INTERNAL_ENGINE = "INTERNAL_ENGINE"
    INTERNAL_CODE = "INTERNAL_CODE"
    INTERNAL_MEMORY = "INTERNAL_MEMORY"
    INTERNAL_LOGS = "INTERNAL_LOGS"
    INTERNAL_PROMPTS = "INTERNAL_PROMPTS"
    INTERNAL_SECURITY = "INTERNAL_SECURITY"


@dataclass
class AccessBoundaryDecision:
    client_id: str
    resource: str
    resource_class: ResourceClass
    decision: AccessDecision
    reason: str
    metadata: dict[str, Any]


class AccessBoundary:
    """
    Defines the hard boundary between customer-accessible assets
    and Agentic Zero internal platform assets.

    Customer can access:
    - delivered package
    - reports
    - allowed downloads
    - license / billing status
    - customer-facing documentation

    Customer can NEVER access:
    - The Machine
    - Agentic Shield source
    - runtime_core source
    - security source
    - saas source
    - internal memory
    - internal audit logs
    - prompts
    - orchestration internals
    """

    ALWAYS_DENY_PREFIXES = (
        "the_machine/",
        "agentic_shield/",
        "runtime_core/",
        "security/",
        "saas/",
        "memory/",
        "internal/",
        "prompts/",
        "logs/internal/",
        ".env",
        "secrets/",
    )

    CUSTOMER_ALLOWED_PREFIXES = (
        "deliveries/",
        "customer_packages/",
        "reports/",
        "docs/customer/",
        "exports/",
        "licenses/customer/",
    )

    def classify(self, resource: str) -> ResourceClass:
        normalized = self._normalize(resource)

        if normalized.startswith(self.ALWAYS_DENY_PREFIXES):
            if normalized.startswith("the_machine/"):
                return ResourceClass.INTERNAL_ENGINE
            if normalized.startswith("agentic_shield/"):
                return ResourceClass.INTERNAL_ENGINE
            if normalized.startswith("runtime_core/"):
                return ResourceClass.INTERNAL_CODE
            if normalized.startswith("security/"):
                return ResourceClass.INTERNAL_SECURITY
            if normalized.startswith("saas/"):
                return ResourceClass.INTERNAL_CODE
            if normalized.startswith("memory/"):
                return ResourceClass.INTERNAL_MEMORY
            if normalized.startswith("prompts/"):
                return ResourceClass.INTERNAL_PROMPTS
            return ResourceClass.INTERNAL_CODE

        if normalized.startswith("customer_packages/"):
            return ResourceClass.CUSTOMER_PACKAGE

        if normalized.startswith("reports/"):
            return ResourceClass.CUSTOMER_REPORT

        if normalized.startswith(self.CUSTOMER_ALLOWED_PREFIXES):
            return ResourceClass.CUSTOMER_VISIBLE

        return ResourceClass.INTERNAL_CODE

    def authorize_resource_access(
        self,
        *,
        client_id: str,
        resource: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AccessBoundaryDecision:
        resource_class = self.classify(resource)

        if resource_class in {
            ResourceClass.INTERNAL_ENGINE,
            ResourceClass.INTERNAL_CODE,
            ResourceClass.INTERNAL_MEMORY,
            ResourceClass.INTERNAL_LOGS,
            ResourceClass.INTERNAL_PROMPTS,
            ResourceClass.INTERNAL_SECURITY,
        }:
            return AccessBoundaryDecision(
                client_id=client_id,
                resource=resource,
                resource_class=resource_class,
                decision=AccessDecision.DENY,
                reason="Internal Agentic Zero asset. Customer access denied.",
                metadata=metadata or {},
            )

        return AccessBoundaryDecision(
            client_id=client_id,
            resource=resource,
            resource_class=resource_class,
            decision=AccessDecision.ALLOW,
            reason="Customer-visible resource.",
            metadata=metadata or {},
        )

    def _normalize(self, resource: str) -> str:
        # Replace backslashes and clean up duplicate slashes first, then
        # resolve any ".." components BEFORE classifying. Without this,
        # "customer_packages/../the_machine/evolution_engine.py" starts
        # with "customer_packages/" and is incorrectly classified as
        # CUSTOMER_PACKAGE + ALLOW, bypassing the boundary entirely.
        # Standard library Path.resolve() requires touching the filesystem;
        # this does the equivalent manually on the string itself.
        normalized = resource.replace("\\", "/").lstrip("/").strip()

        parts = []
        for segment in normalized.split("/"):
            if not segment or segment == ".":
                continue
            if segment == "..":
                if parts:
                    parts.pop()
                else:
                    # Traversal above the root - deny immediately
                    return "internal/blocked_traversal"
            else:
                parts.append(segment)

        return "/".join(parts)


def main() -> None:
    boundary = AccessBoundary()

    tests = [
        "customer_packages/dis_solar/package.zip",
        "reports/dis_solar/roi_report.pdf",
        "the_machine/evolution_engine.py",
        "agentic_shield/policy_engine.py",
        "security/license_manager.py",
        "runtime_core/event_router.py",
        "memory/dis_solar/state.json",
        "prompts/internal/system_prompt.md",
    ]

    results = [
        asdict(
            boundary.authorize_resource_access(
                client_id="dis_solar",
                resource=item,
                metadata={"test": True},
            )
        )
        for item in tests
    ]

    out = Path("client_access/state/access_boundary_test_result.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")

    print("")
    print("Access Boundary")
    print("---------------")
    for result in results:
        print(
            result["decision"],
            "|",
            result["resource_class"],
            "|",
            result["resource"],
        )
    print("")
    print(f"Output: {out}")
    print("")


if __name__ == "__main__":
    main()
