"""Companies research: founded, co-founded, owned, led, or led ventures."""

from typing import Any

from utils import llm_client, search

AGENT_NAME = "companies_agent"
OBJECTIVE = (
    "companies founded, co-founded, owned, led, "
    "business ventures, entrepreneurship"
)

SCHEMA_FIELDS = """
    "companies": [
        {
            "name": "",
            "relationship": "",
            "role": "",
            "description": ""
        }
    ]
"""


def build_queries(person_name: str, identity_profile: dict[str, Any], round_number: int) -> list[str]:
    base = f'"{person_name}"'
    return [
        f"{base} companies founded",
        f"{base} co-founded company",
        f"{base} founder entrepreneur",
        f"{base} business ventures",
        f"{base} company portfolio",
    ]


def run(person_name: str, identity_profile: dict[str, Any]) -> dict[str, Any]:
    """Collect and synthesize company affiliations for the target person."""
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
