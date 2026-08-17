"""News research: recent developments, interviews, announcements."""

from datetime import datetime, timezone
from typing import Any

from utils import llm_client, search

AGENT_NAME = "news_agent"
OBJECTIVE = (
    "recent news, latest developments, interviews, "
    "announcements, official updates"
)

SCHEMA_FIELDS = """
    "recent_developments": [],
    "key_facts": []
"""


def build_queries(person_name: str, identity_profile: dict[str, Any], round_number: int) -> list[str]:
    base = f'"{person_name}"'
    current_year = datetime.now(timezone.utc).year

    return [
        f"{base} latest news",
        f"{base} {current_year} news",
        f"{base} interview {current_year}",
        f"{base} announcement",
        f"{base} recent",
    ]


def run(person_name: str, identity_profile: dict[str, Any]) -> dict[str, Any]:
    """Collect and synthesize recent news coverage for the target person."""
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
