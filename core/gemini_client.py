"""Gemini API呼び出しの共通ラッパー。"""

import os
import ssl

import certifi
import httpx
import streamlit as st
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.6-flash"
AVAILABLE_MODELS = ["gemini-3.6-flash"]


class GeminiConfigError(RuntimeError):
    """APIキーが設定されていない場合に送出される。"""


def _resolve_api_key() -> str:
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            return key
    except (KeyError, FileNotFoundError):
        pass

    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    raise GeminiConfigError(
        ".streamlit/secrets.toml の GEMINI_API_KEY、"
        "もしくは環境変数 GEMINI_API_KEY にAPIキーを設定してください。"
    )


def _build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=certifi.where())
    # Nortonのアンチウイルスが生成するSSL検査用証明書はbasicConstraintsが
    # critical指定されておらず、OpenSSLの厳格チェックだと検証エラーになるため緩める。
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return ctx


@st.cache_resource
def get_client() -> genai.Client:
    ssl_context = _build_ssl_context()
    http_options = types.HttpOptions(
        httpx_client=httpx.Client(verify=ssl_context),
        httpx_async_client=httpx.AsyncClient(verify=ssl_context),
    )
    return genai.Client(api_key=_resolve_api_key(), http_options=http_options)


def generate(
    prompt: str,
    *,
    system_instruction: str | None = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
) -> str:
    """Geminiにプロンプトを送信し、生成されたテキストを返す。"""
    client = get_client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        ),
    )
    return response.text or ""
