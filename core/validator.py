"""Basic structural validation of the aggregated research result.

Checks shape and serializability only — it never fills in or guesses at
missing information. Failed/empty agent sections are expected and are
validated as a legitimate, well-formed state rather than an error.
"""

import json
from typing import Any

REQUIRED_TOP_LEVEL_FIELDS = ("person", "research", "sources", "metadata")
EXPECTED_AGENTS = ("biography", "career", "companies", "education", "news")


def validate(result: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (is_valid, issues). `is_valid` is False only on structural problems."""
    issues: list[str] = []

    for field_name in REQUIRED_TOP_LEVEL_FIELDS:
        if field_name not in result:
            issues.append(f"Missing top-level field: {field_name}")

    research = result.get("research", {})
    if not isinstance(research, dict):
        issues.append("'research' must be an object keyed by agent name")
        research = {}

    for agent_name in EXPECTED_AGENTS:
        section = research.get(agent_name)

        if section is None:
            issues.append(f"Missing research section for agent: {agent_name}")
            continue

        if not isinstance(section, dict) or "status" not in section:
            issues.append(f"Agent section '{agent_name}' is missing a 'status' field")
            continue

        if section["status"] == "failed" and not section.get("error"):
            issues.append(f"Agent '{agent_name}' is marked failed but has no error message")

        if section["status"] == "success" and section.get("data") is None:
            issues.append(f"Agent '{agent_name}' is marked success but has no data")

    metadata = result.get("metadata", {})
    if isinstance(metadata, dict):
        declared_failed = set(metadata.get("failed_agents", []))
        actually_failed = {
            name for name in EXPECTED_AGENTS
            if research.get(name, {}).get("status") == "failed"
        }
        if declared_failed != actually_failed:
            issues.append(
                f"metadata.failed_agents {sorted(declared_failed)} does not match "
                f"actual failed sections {sorted(actually_failed)}"
            )

    try:
        json.dumps(result, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        issues.append(f"Result is not JSON-serializable: {exc}")

    return (len(issues) == 0, issues)
