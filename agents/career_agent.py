"""Career research: employment history, professional roles, career progression."""

from typing import Any

from utils import llm_client, search

AGENT_NAME = "career_agent"
OBJECTIVE = (
    "career history, professional experience, jobs, roles, "
    "career progression, leadership positions"
)

SCHEMA_FIELDS = """
    "roles": [],
    "career_progression": []
"""


def build_queries(person_name: str, identity_profile: dict[str, Any], round_number: int) -> list[str]:
    base = f'"{person_name}"'
    return [
        f"{base} career history",
        f"{base} professional experience",
        f"{base} founder CEO career",
        f"{base} leadership roles",
        f"{base} career progression",
    ]


def run(person_name: str, identity_profile: dict[str, Any]) -> dict[str, Any]:
    """Collect and synthesize career history for the target person."""
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
