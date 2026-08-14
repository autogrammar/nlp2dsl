from nlp2cmd_intent import IntentPipeline, annotate_placement, placement_ambiguities
from pact_ir import IntentIR


AMBIGUOUS = (
    "propose a new repo if missing in subactor and develop it within "
    "wellmanifest standardization {new-project,dsl,logs}"
)
CLEAR = (
    "HOME subactor | SHAPE runtime_service | "
    "ADOPT wellmanifest/{new-project,dsl,logs} | "
    "if missing, propose a new runtime_service repo in subactor and develop it there"
)


def test_original_phrase_is_ambiguous_home_vs_adopt():
    gaps = placement_ambiguities(AMBIGUOUS)
    assert gaps
    assert gaps[0].field == "placement.home"
    assert "ADOPT packs, not HOME" in gaps[0].message


def test_closed_vocabulary_phrase_is_not_ambiguous():
    assert placement_ambiguities(CLEAR) == []


def test_pipeline_blocks_ambiguous_wellmanifest_runtime_phrase():
    intent = IntentPipeline().run(AMBIGUOUS)
    assert intent.needs_clarification()
    assert any(item.field == "placement.home" for item in intent.ambiguities)


def test_annotate_is_idempotent():
    intent = IntentIR(query=AMBIGUOUS, intent="unknown")
    once = annotate_placement(intent)
    twice = annotate_placement(once)
    assert sum(item.field == "placement.home" for item in twice.ambiguities) == 1
