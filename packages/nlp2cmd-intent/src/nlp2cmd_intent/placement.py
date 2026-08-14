"""Detect ambiguous HOME vs ADOPT phrasing on existing IntentIR."""

from __future__ import annotations

from pact_ir import Ambiguity, IntentIR

HOME_MARKERS = ("home wellmanifest", "home subactor", "home semcod")
ADOPT_MARKERS = ("adopt wellmanifest/", "adopt wellmanifest")
WELLMANIFEST_HINTS = (
    "wellmanifest",
    "w ramach wellmanifest",
    "within wellmanifest",
)
RUNTIME_HINTS = (
    "new repo",
    "nowe repo",
    "new-project",
    "daemon",
    "cli",
    "runtime",
    "subactor",
    "develop it",
    "rozwi",
)

PLACEMENT_AMBIGUITY = Ambiguity(
    field="placement.home",
    message=(
        'Ambiguous HOME vs ADOPT. "w ramach wellmanifest" / '
        '"within wellmanifest standardization" means ADOPT packs, not HOME '
        "wellmanifest. Runtime CLI/daemons belong in subactor or semcod."
    ),
    candidates=[
        "HOME wellmanifest; SHAPE domain_pack",
        "HOME subactor; SHAPE runtime_service; ADOPT wellmanifest/{new-project,dsl,logs}",
        "HOME semcod; SHAPE runtime_service; ADOPT wellmanifest/{new-project,dsl,logs}",
    ],
)


def _normalized(query: str) -> str:
    return " ".join(query.lower().split())


def placement_ambiguities(query: str) -> list[Ambiguity]:
    text = _normalized(query)
    has_home = any(marker in text for marker in HOME_MARKERS)
    has_adopt = any(marker in text for marker in ADOPT_MARKERS)
    mentions_wellmanifest = any(hint in text for hint in WELLMANIFEST_HINTS)
    mentions_runtime = any(hint in text for hint in RUNTIME_HINTS)
    if mentions_wellmanifest and mentions_runtime and not (has_home and has_adopt):
        return [PLACEMENT_AMBIGUITY]
    return []


def annotate_placement(intent: IntentIR) -> IntentIR:
    """Fail-closed: missing HOME/ADOPT on a wellmanifest+runtime phrase is a gap."""
    extra = placement_ambiguities(intent.query)
    if not extra:
        return intent
    existing = {item.field for item in intent.ambiguities}
    merged = list(intent.ambiguities)
    for item in extra:
        if item.field not in existing:
            merged.append(item)
    intent.ambiguities = merged
    return intent
