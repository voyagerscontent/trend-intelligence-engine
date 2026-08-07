#!/usr/bin/env python3
"""Static project auditor for the Trend Intelligence Engine.

Deterministic, dependency-light checks that enforce the architecture map so
glitches are caught up front and config/code can't silently drift. This is the
robust half of the auditor (the .claude/agents/trend-engine-auditor.md agent is
the judgement half). Run locally or in CI:

    python scripts/audit_static.py        # exits non-zero on any FAIL

Add a check by appending a function decorated with @check.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PKG = SRC / "trendengine"
sys.path.insert(0, str(SRC))

_CHECKS = []


def check(fn):
    _CHECKS.append(fn)
    return fn


def _py_files() -> list[Path]:
    return [p for p in PKG.rglob("*.py")]


# --------------------------------------------------------------------------- #
# 1. Source contract + registry
# --------------------------------------------------------------------------- #
@check
def source_contract() -> tuple[bool, str]:
    from trendengine.sources import REGISTRY

    problems = []
    names = []
    for src in REGISTRY:
        name = getattr(src, "NAME", None)
        if not isinstance(name, str) or not name:
            problems.append(f"{src!r} has no valid NAME")
            continue
        names.append(name)
        if not callable(getattr(src, "fetch", None)):
            problems.append(f"{name} has no fetch()")
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        problems.append(f"duplicate source NAME(s): {sorted(dupes)}")

    # every source module is registered
    registered_modules = {type(s).__module__.split(".")[-1] for s in REGISTRY}
    on_disk = {
        p.stem for p in (PKG / "sources").glob("*.py")
        if p.stem not in {"__init__", "base"}
    }
    missing = on_disk - registered_modules
    if missing:
        problems.append(f"source modules not in REGISTRY: {sorted(missing)}")

    return (not problems, "; ".join(problems) or f"{len(names)} sources OK, names unique")


# --------------------------------------------------------------------------- #
# 2. Scoring config <-> code consistency
# --------------------------------------------------------------------------- #
@check
def weights_match_factors() -> tuple[bool, str]:
    from trendengine.score import FACTORS

    data = yaml.safe_load((PKG / "config" / "weights.yaml").read_text())
    wkeys = set((data.get("weights") or {}).keys())
    fkeys = set(FACTORS)
    if wkeys != fkeys:
        return False, f"weights.yaml keys {sorted(wkeys)} != FACTORS {sorted(fkeys)}"
    total = sum(data["weights"].values())
    if abs(total - 1.0) > 1e-6:
        return False, f"weights sum to {total}, must be 1.0"
    th = data.get("thresholds") or {}
    for key in ("min_sources_to_escalate", "min_score_to_brief", "min_brand_fit"):
        if key not in th:
            return False, f"thresholds missing '{key}'"
    return True, "weights match FACTORS, sum=1.0, thresholds present"


# --------------------------------------------------------------------------- #
# 3. Every env var used is documented in .env.example
# --------------------------------------------------------------------------- #
@check
def env_vars_documented() -> tuple[bool, str]:
    documented = set()
    for line in (ROOT / ".env.example").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            documented.add(line.split("=", 1)[0].strip())

    used = set()
    # Match direct os access AND the settings._get("VAR") indirection, so the
    # check actually sees the vars (all env access flows through settings.py).
    pats = [
        re.compile(r"""os\.(?:getenv|environ\.get)\(\s*["']([A-Z0-9_]+)["']"""),
        re.compile(r"""os\.environ\[\s*["']([A-Z0-9_]+)["']\s*\]"""),
        re.compile(r"""_get\(\s*["']([A-Z0-9_]+)["']"""),
    ]
    for f in _py_files():
        text = f.read_text()
        for pat in pats:
            used |= set(pat.findall(text))

    if not used:
        return False, "no env vars detected — the scan is broken, not the code"
    undocumented = used - documented
    if undocumented:
        return False, f"env vars used but not in .env.example: {sorted(undocumented)}"
    return True, f"{len(used)} env var(s) all documented"


# --------------------------------------------------------------------------- #
# 4. No hardcoded secrets committed
# --------------------------------------------------------------------------- #
@check
def no_hardcoded_secrets() -> tuple[bool, str]:
    danger = [
        re.compile(r"sk-ant-[A-Za-z0-9\-]{10,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
        re.compile(r"pat[A-Za-z0-9]{14,}\."),  # Airtable PAT
    ]
    # Scan code AND config/workflow/env text — a secret can be pasted anywhere.
    scan_files = list(PKG.rglob("*.py"))
    scan_files += list(ROOT.glob(".github/workflows/*.yml"))
    scan_files += list(PKG.rglob("*.yaml"))
    scan_files += [p for p in ROOT.glob(".env*") if p.name != ".env.example"]
    hits = []
    for f in scan_files:
        if not f.exists():
            continue
        text = f.read_text()
        for rx in danger:
            if rx.search(text):
                hits.append(f"{f.relative_to(ROOT)} ~ {rx.pattern}")
    return (not hits, "; ".join(hits) or f"no secret-like literals in {len(scan_files)} files")


# --------------------------------------------------------------------------- #
# 5. Pipeline wires every stage (architecture mapping)
# --------------------------------------------------------------------------- #
@check
def pipeline_wires_all_stages() -> tuple[bool, str]:
    text = (PKG / "pipeline.py").read_text()
    required = {
        "ingest": "REGISTRY",
        "normalize": "normalize(",
        "cluster": "cluster(",
        "score": "score_trend(",
        "brief": "generate_brief(",
        "deliver-slack": "deliver_slack(",
        "deliver-airtable": "deliver_airtable(",
        "corroboration-gate": "min_sources_to_escalate",
        "brand-fit-gate": "min_brand_fit",
        "failure-alert": "alert_failure(",
        "structured-logging": "log_event(",
    }
    missing = [stage for stage, token in required.items() if token not in text]
    return (not missing, f"missing stage wiring: {missing}" if missing else "all 5 stages wired")


# --------------------------------------------------------------------------- #
# 6. Every module imports/parses cleanly (no syntax errors)
# --------------------------------------------------------------------------- #
@check
def modules_parse() -> tuple[bool, str]:
    bad = []
    for f in _py_files():
        try:
            ast.parse(f.read_text())
        except SyntaxError as exc:
            bad.append(f"{f.relative_to(ROOT)}: {exc}")
    return (not bad, "; ".join(bad) or f"{len(_py_files())} modules parse")


# --------------------------------------------------------------------------- #
# 7. Brands config integrity
# --------------------------------------------------------------------------- #
@check
def brands_config_valid() -> tuple[bool, str]:
    data = yaml.safe_load((PKG / "config" / "brands.yaml").read_text())
    brands = data.get("brands") or {}
    if not brands:
        return False, "brands.yaml has no brands"
    for key, cfg in brands.items():
        for req in ("name", "role", "seed_topics"):
            if req not in cfg:
                return False, f"brand '{key}' missing '{req}'"
    return True, f"{len(brands)} brand(s) valid"


def run() -> int:
    print("=" * 68)
    print(" TREND INTELLIGENCE ENGINE · STATIC AUDIT")
    print("=" * 68)
    failed = 0
    for fn in _CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:  # a crashing check is itself a failure
            ok, detail = False, f"check raised {exc!r}"
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{status}] {fn.__name__:<26} {detail}")
    print("-" * 68)
    print(f"{'ALL CHECKS PASSED' if not failed else str(failed) + ' CHECK(S) FAILED'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
