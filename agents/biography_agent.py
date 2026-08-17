"""Biographical research: personal history, early life, background."""

from typing import Any

from utils import llm_client, search

AGENT_NAME = "biography_agent"
OBJECTIVE = (
    "biography, background, personal history, early life, "
    "family background, origin"
)

SCHEMA_FIELDS = """
    "early_life": "",
    "background": "",
    "major_milestones": []
"""


def build_queries(person_name: str, identity_profile: dict[str, Any], round_number: int) -> list[str]:
    base = f'"{person_name}"'
    return [
        f"{base} biography",
        f"{base} early life",
        f"{base} background",
        f"{base} founder story",
        f"{base} interview",
    ]


def run(person_name: str, identity_profile: dict[str, Any]) -> dict[str, Any]:
    """Collect and synthesize biographical information for the target person."""
    gathered = search.gather_sources(person_name, AGENT_NAME, OBJECTIVE, identity_profile, build_queries)

    data = llm_client.synthesize_section(
        person_name, identity_profile, AGENT_NAME, OBJECTIVE, gathered["sources"], SCHEMA_FIELDS
    )

    return {
        "data": data,
        "sources": gathered["sources"],
        "rejected_count": len(gathered["rejected_sources"]),
        "search_rounds_used": gathered["search_rounds_used"],
    }
