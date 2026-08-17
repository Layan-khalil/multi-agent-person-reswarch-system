"""Combines independent agent outcomes into one structured research profile.

Purely a combination/normalization step — no searching, no LLM calls.
Each agent already produced its own structured section; this module just
assembles them, preserves source attribution, deduplicates sources shared
across agents, and records which agents failed.
"""

import time
from typing import Any


def _strip_page_text(source: dict[str, Any]) -> dict[str, Any]:
    """Drop the large extracted page body; keep attribution and scoring."""
    return {key: value for key, value in source.items() if key != "text"}


def aggregate(orchestrator_result: dict[str, Any]) -> dict[str, Any]:
    """Build the final `{person, research, sources, metadata}` structure."""
    outcomes = orchestrator_result["agent_outcomes"]

    research: dict[str, Any] = {}
    failed_agents: list[str] = []
    agent_durations: dict[str, float] = {}
    all_sources: list[dict[str, Any]] = []

    for name, outcome in outcomes.items():
        agent_durations[name] = round(outcome.duration_seconds, 3)

        if outcome.status == "success":
            research[name] = {
                "status": "success",
                "data": outcome.data,
                "source_count": len(outcome.sources),
                "rejected_count": outcome.rejected_count,
                "search_rounds_used": outcome.search_rounds_used,
            }
            all_sources.extend(outcome.sources)
        else:
            failed_agents.append(name)
            research[name] = {
                "status": "failed",
                "data": None,
                "error": outcome.error,
            }

    seen_urls: set[str] = set()
    unique_sources: list[dict[str, Any]] = []
    for source in all_sources:
        url = source.get("url")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        unique_sources.append(_strip_page_text(source))

    return {
        "person": orchestrator_result["person_name"],
        "identity_profile": orchestrator_result["identity_profile"],
        "research": research,
        "sources": unique_sources,
        "metadata": {
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "agents": list(outcomes.keys()),
            "failed_agents": failed_agents,
            "agent_durations_seconds": agent_durations,
            "total_duration_seconds": round(orchestrator_result["total_duration_seconds"], 3),
        },
    }
