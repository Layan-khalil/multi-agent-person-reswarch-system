"""Environment configuration and shared tuning constants.

Single source of truth for API credentials and pipeline knobs so that
`utils/`, `agents/`, and `core/` never read `os.environ` directly.
"""

import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

REQUIRED_ENV_VARS = ("GOOGLE_API_KEY", "GOOGLE_CSE_ID", "DEEPSEEK_API_KEY")


def validate_environment() -> None:
    """Raise if any required credential is missing from the environment."""
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]

    if missing:
        raise EnvironmentError(
            "Missing environment variables: "
            + ", ".join(missing)
            + "\nCreate a .env file (see .env.example) and set them."
        )


# --- Search provider -------------------------------------------------------

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
REQUEST_TIMEOUT = 20
CANDIDATES_PER_SEARCH = 8

# --- Source collection policy ------------------------------------------------

TARGET_SOURCES_PER_AGENT = 3
MAX_SEARCH_ROUNDS = 5

MIN_IDENTITY_MATCH = 8
MIN_PERSON_MATCH = 8
MIN_OBJECTIVE_MATCH = 7
MIN_OVERALL_SCORE = 7

BLOCKED_DOMAINS = frozenset({
    "youtube.com",
    "youtu.be",
    "reddit.com",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
})

PREFERRED_DOMAINS = frozenset({
    "linkedin.com",
    "crunchbase.com",
    "forbes.com",
    "wsj.com",
    "nytimes.com",
    "bloomberg.com",
    "reuters.com",
    "techcrunch.com",
    "businessinsider.com",
    "cnbc.com",
    "medium.com",
    "harvard.edu",
    "stanford.edu",
    "mit.edu",
})

# --- LLM provider ------------------------------------------------------------

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# --- Output -------------------------------------------------------------------

OUTPUT_DIR = "outputs"
