"""
LLM-based NLP parser — via LiteLLM (unified API for 100+ providers).

Używa structured output (JSON schema) do wyodrębnienia intent + entities.
NIE generuje DSL — tylko rozumie język naturalny.

Obsługiwane providery (automatycznie przez LiteLLM):
  - OpenRouter  (OPENROUTER_API_KEY)  → np. openrouter/openai/gpt-5-mini
  - OpenAI      (OPENAI_API_KEY)      → np. gpt-4o-mini
  - Anthropic   (ANTHROPIC_API_KEY)   → np. claude-sonnet-4-20250514
  - Ollama      (OLLAMA_API_BASE)     → np. ollama/llama3
  - Azure, Groq, Together, Mistral, Cohere, Bedrock, ...

Konfiguracja (env vars):
  LLM_MODEL         — model do użycia (default: openrouter/openai/gpt-5-mini)
  LLM_TEMPERATURE   — temperatura (default: 0)
  LLM_MAX_TOKENS    — max tokenów odpowiedzi (default: 1024)
  LLM_API_BASE      — custom API base URL (opcjonalne)

  Klucze API (LiteLLM automatycznie wykrywa):
  OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, itp.
"""

import json
import logging
import os
from pathlib import Path

import litellm
from litellm import acompletion

from app.contracts.nlp_result import response_format, validate_payload
from app.routing.parser.prompt_catalog import build_llm_system_prompt
from app.schemas import NLPEntities, NLPIntent, NLPResult

log = logging.getLogger("nlp.llm")

LLM_RESPONSE_PREVIEW_LEN: int = int("200")

# ── LiteLLM config ───────────────────────────────────────────

litellm.telemetry = False
litellm.drop_params = True

LLM_MODEL = os.getenv("LLM_MODEL", "openrouter/z-ai/glm-5.2")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
LLM_API_BASE = os.getenv("LLM_API_BASE", None)


def openrouter_extra_headers() -> dict[str, str]:
    """Return stable OpenRouter App attribution headers."""
    app_name = (
        os.getenv("OPENROUTER_APP_NAME", "").strip()
        or Path.cwd().name
        or "nlp2dsl"
    )
    headers = {"X-Title": app_name}
    app_url = os.getenv("OPENROUTER_APP_URL", "").strip()
    if app_url:
        headers["HTTP-Referer"] = app_url
    return headers


# ── Prompts ───────────────────────────────────────────────────

SYSTEM_PROMPT = build_llm_system_prompt()

USER_PROMPT_TEMPLATE = """Przeanalizuj tekst i zwróć JSON:

"{text}"
"""


# ── LLM Caller (LiteLLM) ─────────────────────────────────────


async def parse_llm(text: str) -> NLPResult:
    """Parse text using LLM via LiteLLM."""

    provider = _detect_provider()
    model = LLM_MODEL

    log.info("LLM call: model=%s provider=%s", model, provider)

    try:
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)},
            ],
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_TOKENS,
        }

        if LLM_API_BASE:
            kwargs["api_base"] = LLM_API_BASE
        if model.startswith("openrouter/"):
            kwargs["extra_headers"] = openrouter_extra_headers()
        kwargs["response_format"] = response_format()

        response = await acompletion(**kwargs)

        raw = response.choices[0].message.content
        log.debug("LLM raw response: %s", raw[:LLM_RESPONSE_PREVIEW_LEN])

        parsed = _parse_json_response(raw)
        validate_payload(parsed)

        return NLPResult(
            intent=NLPIntent(**parsed["intent"]),
            entities=NLPEntities(**parsed["entities"]),
            missing=parsed["missing"],
            raw_text=text,
        )

    except Exception:
        log.exception("LLM parsing failed (model=%s), returning unknown intent", model)
        return NLPResult(
            intent=NLPIntent(intent="unknown", confidence=0.0),
            entities=NLPEntities(),
            missing=[],
            raw_text=text,
        )


def _detect_provider() -> str:
    """Detect which LLM provider is configured."""
    if os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("OLLAMA_API_BASE"):
        return "ollama"
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("TOGETHER_API_KEY"):
        return "together"
    if os.getenv("MISTRAL_API_KEY"):
        return "mistral"
    if os.getenv("COHERE_API_KEY"):
        return "cohere"
    if LLM_API_BASE:
        return "custom"
    return "none"


def _parse_json_response(raw: str) -> dict:
    """Parse one complete JSON object; prose and markdown fail closed."""
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise TypeError("LLM response must be a JSON object")
    return parsed
