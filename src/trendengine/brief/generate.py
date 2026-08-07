"""Turn a scored Trend into a multichannel content Brief.

Deterministic draft by default so the pipeline runs offline; when
ANTHROPIC_API_KEY is present, _draft_with_claude() upgrades the creative
fields (angle, bait mechanic, channel cutdowns) in the Stephen Sancho voice.
Both paths return the same Brief shape.
"""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models import Brief, Trend
from ..settings import Settings

_TEMPLATES = Path(__file__).parent / "templates"
_VOICE = Path(__file__).parents[1] / "config" / "voice" / "stephen.md"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES)),
    autoescape=select_autoescape(enabled_extensions=()),
    trim_blocks=True,
    lstrip_blocks=True,
)
# jinja has no built-in 'unique'; register a stable one for the template footer.
_env.filters["unique"] = lambda seq: list(dict.fromkeys(seq))


def _channels(trend: Trend) -> dict[str, str]:
    return {
        "Blog / editorial": f"Pillar page targeting '{trend.title}'.",
        "YouTube": "Long-form hero cut with a strong thumbnail hook.",
        "Reels / TikTok": "3–5 native vertical cutdowns from the hero footage.",
        "IG carousel": "Data/insight carousel; save-worthy first frame.",
        "Email": "Segment to dreamers in the relevant destination interest.",
        "PR pitch": "Offer the data asset to travel press as an exclusive.",
    }


def _draft_fallback(trend: Trend) -> dict:
    return {
        "angle": f"An expert, first-hand take on {trend.title} only this brand can credibly own.",
        "audience": "Affluent experience-seekers researching a bucket-list expedition.",
        "intent_stage": "high-intent" if trend.factors.get("monetisability", 0) >= 0.6 else "dreaming",
        "hero_format": "Data study / editorial pillar",
        "keyword": trend.title,
        "ai_prompt": trend.title,
        "bait_mechanic": "Proprietary data or a defensible ranking that earns links and AI citations.",
        "channels": _channels(trend),
        "visual_notes": "Cinematic destination footage; a striking data-viz for the bait asset.",
        "cta": "Route engaged readers to a Voyagers enquiry / advisor consult.",
    }


def _draft_with_claude(trend: Trend, settings: Settings) -> dict:
    """Upgrade the creative fields via Claude. Falls back safely on any error."""
    try:
        import anthropic  # imported lazily so offline runs never need it

        voice = _VOICE.read_text(encoding="utf-8") if _VOICE.exists() else ""
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        prompt = (
            "You are the content strategist for a luxury expedition travel group.\n"
            f"Trend: {trend.title} (brand: {trend.brand}, score {trend.score}).\n"
            f"Signals: {[s.entity for s in trend.signals]}.\n"
            "Return a JSON object with keys: angle, audience, intent_stage, "
            "hero_format, keyword, ai_prompt, bait_mechanic, channels "
            "(object), visual_notes, cta. Propose an angle only this brand can "
            "credibly own; engineer one bait mechanic that earns links AND AI "
            "citations; specify native cutdowns per channel. Write in this voice:\n"
            f"{voice}"
        )
        msg = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        import json

        text = "".join(getattr(b, "text", "") for b in msg.content)
        start, end = text.find("{"), text.rfind("}")
        data = json.loads(text[start : end + 1])
        base = _draft_fallback(trend)
        base.update({k: v for k, v in data.items() if v})
        return base
    except Exception:
        return _draft_fallback(trend)


def generate_brief(trend: Trend, settings: Settings) -> Brief:
    fields = (
        _draft_with_claude(trend, settings)
        if settings.anthropic_api_key
        else _draft_fallback(trend)
    )
    b = Brief(title=trend.title, brand=trend.brand, **fields)
    b.body_markdown = _env.get_template("brief.md.j2").render(
        b=b, trend=trend, rationale=trend.rationale
    )
    trend.brief = b
    return b
