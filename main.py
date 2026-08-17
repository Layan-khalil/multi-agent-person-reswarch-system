"""Multi-agent person research system — entry point.

Flow: user input -> orchestrator (identity resolution + parallel agents)
-> aggregator -> validator -> structured JSON output.

Usage:
    python main.py
    python main.py "Person Name"
"""

import json
import logging
import re
import sys
import time
from pathlib import Path

import config
from core import aggregator, orchestrator, validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger("main")


def save_result(person_name: str, result: dict) -> str:
    output_dir = Path(config.OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", person_name.lower())
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{safe_name}_{timestamp}.json"

    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    return str(output_path)


def print_summary(result: dict) -> None:
    metadata = result["metadata"]

    print("\n" + "=" * 70)
    print("RESEARCH SUMMARY")
    print("=" * 70)

    for agent_name in orchestrator.AGENTS:
        section = result["research"].get(agent_name, {})
        duration = metadata["agent_durations_seconds"].get(agent_name, 0.0)

        if section.get("status") == "success":
            print(f"  [OK]     {agent_name:<16} {duration:6.2f}s  {section['source_count']} sources")
        else:
            print(f"  [FAILED] {agent_name:<16} {duration:6.2f}s  {section.get('error')}")

    print("-" * 70)
    print(f"  Total agent wall time : {metadata['total_duration_seconds']:.2f}s")
    print(f"  Unique sources        : {len(result['sources'])}")
    print(f"  Failed agents         : {metadata['failed_agents'] or 'none'}")
    print("=" * 70)


def run(person_name: str) -> dict:
    config.validate_environment()

    logger.info("Starting research pipeline for '%s'", person_name)

    orchestrator_result = orchestrator.run_research(person_name)
    result = aggregator.aggregate(orchestrator_result)

    is_valid, issues = validator.validate(result)
    if not is_valid:
        for issue in issues:
            logger.warning("Validation issue: %s", issue)

    output_path = save_result(person_name, result)
    logger.info("Results saved to %s", output_path)

    print_summary(result)
    print(f"\nSaved to: {output_path}")

    return result


def main() -> None:
    person_name = " ".join(sys.argv[1:]).strip()

    if not person_name:
        person_name = input("Enter person to research: ").strip()

    if not person_name:
        raise ValueError("Person name cannot be empty.")

    run(person_name)


if __name__ == "__main__":
    main()
