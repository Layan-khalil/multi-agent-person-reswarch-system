"""Education research: degrees, universities, certifications, academic background."""

from typing import Any

from utils import llm_client, search

AGENT_NAME = "education_agent"
OBJECTIVE = "education, universities, degrees, academic background"

SCHEMA_FIELDS = """
    "degrees": [],
    "institutions": [],
    "academic_background": ""
"""


def build_queries(person_name: str, identity_profile: dict[str, Any], round_number: int) -> list[str]:
    base = f'"{person_name}"'
    anchor = search.get_disambiguation_anchor(identity_profile)

    if anchor:
        return [
            f"{base} {anchor} education",
            f"{base} {anchor} university degree",
            f"{base} {anchor} college",
            f"{base} {anchor} academic background",
            f"{base} {anchor} graduated",
        ]

    return [
        f"{base} education LinkedIn",
        f"{base} university degree biography",
        f"{base} college founder",
        f"{base} academic background official",
        f"{base} graduated profile",
    ]


def run(person_name: str, identity_profile: dict[str, Any]) -> dict[str, Any]:
    """Collect and synthesize education history for the target person."""
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
