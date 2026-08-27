# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal AI writing toolkit built with Streamlit + Google Gemini (`google-genai`). A single-page app with a sidebar tool switcher; each tool is a self-contained prompt-building form that calls Gemini and renders the result.

## Commands

Run the app:
```
streamlit run app.py
```

Install dependencies:
```
pip install -r requirements.txt
```

There is no test suite, linter, or build step configured in this repo.

## Setup

Gemini API key is read from `.streamlit/secrets.toml` (`GEMINI_API_KEY = "..."`, copy from `.streamlit/secrets.toml.example`) or falls back to the `GEMINI_API_KEY` environment variable. See `core/gemini_client.py:_resolve_api_key`.

## Architecture

- `app.py` — entry point. Defines the `TOOLS` dict mapping a Japanese label to a feature module, renders the sidebar (tool picker, model select, temperature slider), and dispatches to `TOOLS[selected_tool].render(model=..., temperature=...)`.
- `core/gemini_client.py` — the only place that talks to the Gemini API. Exposes `generate(prompt, *, system_instruction, model, temperature) -> str`. The `genai.Client` is built once via `@st.cache_resource`.
  - It constructs an `ssl.SSLContext` with `VERIFY_X509_STRICT` disabled and passes it into `httpx.Client`/`httpx.AsyncClient`, which are injected into the client through `types.HttpOptions`. This works around a local SSL-inspection proxy (antivirus) whose CA cert has a non-critical `basicConstraints` extension, which OpenSSL's strict mode otherwise rejects. Don't remove this without confirming the target environment doesn't need it.
- `features/_common.py` — shared `run_generation(...)` wrapper used by every feature module: wraps `core.gemini_client.generate` in `st.spinner`, catches `GeminiConfigError` and generic exceptions, reports them via `st.error`, and returns `None` on failure so callers can skip updating state.
- `features/*.py` — one module per tool (`blog_writer`, `email_reply`, `summarizer`, `proofreader`, `title_generator`). Each follows the same shape:
  - a module-level `SYSTEM_INSTRUCTION` string (where applicable)
  - `_build_prompt(...)` — assembles the user-facing form inputs into a single prompt string
  - `render(model: str, temperature: float) -> None` — draws the Streamlit form, calls `run_generation` on submit, and stores the result in `st.session_state["<tool>_output"]` so it persists across reruns; the output is re-rendered from session state on every run.

To add a new tool: create `features/new_tool.py` following that shape, then register it in the `TOOLS` dict in `app.py`.

## Available models

`core/gemini_client.py` hardcodes `DEFAULT_MODEL` / `AVAILABLE_MODELS`. Gemini model availability changes over time (older model IDs get retired for new API keys) — if calls start failing with a 404 naming a replacement model, update these constants rather than assuming the client code is broken.
