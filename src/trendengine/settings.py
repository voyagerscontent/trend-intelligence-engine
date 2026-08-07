"""Centralised environment access.

All `os.getenv` calls live here so that (a) sources stay pure and testable
and (b) the static auditor can verify that every environment variable used
by the code is documented in .env.example. Do NOT read os.environ elsewhere.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _get(name: str, default: str = "") -> str:
    # .strip() so a stray trailing newline or space from a pasted secret
    # can't corrupt an HTTP header (a common cause of "InvalidHeader").
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str = field(default_factory=lambda: _get("ANTHROPIC_API_KEY"))
    ahrefs_api_key: str = field(default_factory=lambda: _get("AHREFS_API_KEY"))
    gsc_credentials: str = field(default_factory=lambda: _get("GSC_CREDENTIALS"))
    serpapi_key: str = field(default_factory=lambda: _get("SERPAPI_KEY"))
    youtube_api_key: str = field(default_factory=lambda: _get("YOUTUBE_API_KEY"))
    reddit_client_id: str = field(default_factory=lambda: _get("REDDIT_CLIENT_ID"))
    reddit_client_secret: str = field(default_factory=lambda: _get("REDDIT_CLIENT_SECRET"))
    news_api_key: str = field(default_factory=lambda: _get("NEWS_API_KEY"))
    airtable_token: str = field(default_factory=lambda: _get("AIRTABLE_TOKEN"))
    airtable_base_id: str = field(default_factory=lambda: _get("AIRTABLE_BASE_ID"))
    slack_token: str = field(default_factory=lambda: _get("SLACK_TOKEN"))
    slack_channel: str = field(default_factory=lambda: _get("SLACK_CHANNEL"))


def load_settings() -> Settings:
    """Load settings, pulling from a local .env when present (dev convenience)."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:  # dotenv is optional at runtime
        pass
    return Settings()
