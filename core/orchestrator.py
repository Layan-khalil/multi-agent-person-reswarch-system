"""Coordinates the research pipeline: identity resolution, then parallel
agent execution.

This module intentionally contains no research logic of its own — it only
resolves identity once (shared prerequisite for every agent), launches the
five specialized agents concurrently, and captures each one's outcome
(success, timing, or isolated failure) for the aggregator to combine.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any

from agents import biography_agent, career_agent, companies_agent, education_agent, news_agent
from utils import llm_client

logger = logging.getLogger(__name__)

AGENTS: dict[str, ModuleType] = {
    "biography": biography_agent,
    "career": career_agent,
    "companies": companies_agent,
    "education": education_agent,
    "news": news_agent,
}


@dataclass
class AgentOutcome:
    """Result of running a single agent, success or failure."""

    status: str  # "success" | "failed"
    duration_seconds: float
    data: Any = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    rejected_count: int = 0
    search_rounds_used: int = 0
    error: str | None = None


def resolve_identity(person_name: str) -> dict[str, Any]:
    """Run the shared identity-resolution step once, ahead of all agents."""
    logger.info("Resolving target identity for '%s'", person_name)
    return llm_client.build_identity_profile(person_name)


def _run_single_agent(
    name: str, module: ModuleType, person_name: str, identity_profile: dict[str, Any]
) -> AgentOutcome:
    start = time.perf_counter()
    logger.info("Agent '%s' started", name)

    try:
        result = module.run(person_name, identity_profile)
        duration = time.perf_counter() - start

        logger.info(
            "Agent '%s' finished in %.2fs (%d sources)",
            name, duration, len(result["sources"]),
        )

        return AgentOutcome(
            status="success",
            duration_seconds=duration,
            data=result["data"],
            sources=result["sources"],
            rejected_count=result["rejected_count"],
            search_rounds_used=result["search_rounds_used"],
        )

    except Exception as exc:
        duration = time.perf_counter() - start
        logger.error("Agent '%s' failed after %.2fs: %s", name, duration, exc)
        return AgentOutcome(status="failed", duration_seconds=duration, error=str(exc))


def run_research(person_name: str) -> dict[str, Any]:
    """Resolve identity, then run every research agent concurrently.

    A failure in one agent is captured as a failed `AgentOutcome` and does
    not stop the others — every agent gets its own future and its own
    try/except boundary.
    """
    identity_profile = resolve_identity(person_name)

    logger.info("Launching %d research agents in parallel", len(AGENTS))
    overall_start = time.perf_counter()

    outcomes: dict[str, AgentOutcome] = {}

    with ThreadPoolExecutor(max_workers=len(AGENTS)) as executor:
        futures = {
            executor.submit(_run_single_agent, name, module, person_name, identity_profile): name
            for name, module in AGENTS.items()
        }

        for future in as_completed(futures):
            name = futures[future]
            outcomes[name] = future.result()

    total_duration = time.perf_counter() - overall_start
    logger.info("All agents completed in %.2fs", total_duration)

    return {
        "person_name": person_name,
        "identity_profile": identity_profile,
        "agent_outcomes": outcomes,
        "total_duration_seconds": total_duration,
    }
