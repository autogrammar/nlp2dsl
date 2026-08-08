"""Offline tests for the LLM-to-NLPResult boundary contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from app.contracts.nlp_result import CONTRACT_VERSION, load_schema, validate_payload
from app.routing.parser import llm
from app.schemas import NLPEntities

FIXTURES = Path(__file__).parent / "fixtures" / "contracts" / "nlp-result" / "v1"
CONTRACTS = Path(llm.__file__).parents[2] / "contracts" / "nlp_result" / "v1"


class _Message:
    def __init__(self, content: str) -> None:
        self.content = content


class _Response:
    def __init__(self, content: str) -> None:
        self.choices = [type("Choice", (), {"message": _Message(content)})()]


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_valid_and_invalid_fixtures() -> None:
    validate_payload(_fixture("valid.json"))
    with pytest.raises(ValueError, match="violates NLPResult v1"):
        validate_payload(_fixture("invalid.json"))


def test_complete_json_only() -> None:
    with pytest.raises(json.JSONDecodeError):
        llm._parse_json_response('```json\n{"contractVersion":"1.0.0"}\n```')


@pytest.mark.asyncio
async def test_parse_llm_binds_schema_and_app_identity(monkeypatch, tmp_path: Path) -> None:
    project = tmp_path / "customer-flow"
    project.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setattr(llm, "LLM_MODEL", "openrouter/z-ai/glm-5.2")
    monkeypatch.delenv("OPENROUTER_APP_NAME", raising=False)
    monkeypatch.setenv("OPENROUTER_APP_URL", "https://example.test/nlp")
    captured: dict = {}

    async def fake_acompletion(**kwargs):
        captured.update(kwargs)
        return _Response(json.dumps(_fixture("valid.json")))

    monkeypatch.setattr(llm, "acompletion", fake_acompletion)
    result = await llm.parse_llm("send status")
    assert result.intent.intent == "send_email"
    assert result.raw_text == "send status"
    assert captured["response_format"]["json_schema"]["schema"] == load_schema()
    assert captured["extra_headers"] == {
        "X-Title": "customer-flow",
        "HTTP-Referer": "https://example.test/nlp",
    }


def test_manifest_binds_runtime_and_artifacts() -> None:
    manifest = json.loads((CONTRACTS / "manifest.json").read_text())
    assert manifest["version"] == CONTRACT_VERSION
    assert manifest["boundary"] == "app.routing.parser.llm.parse_llm"
    for artifact in manifest["artifacts"].values():
        assert (CONTRACTS / artifact).is_file()
    assert "message NLPResultFields" in (CONTRACTS / "nlp-result.proto").read_text()
    assert f'\\"{CONTRACT_VERSION}\\"' in (CONTRACTS / "nlp-result.gbnf").read_text()


def test_schema_entity_fields_match_runtime_model() -> None:
    schema_fields = set(load_schema()["properties"]["entities"]["properties"])
    assert schema_fields == set(NLPEntities.model_fields)
