"""Gemini API呼び出しの共通ラッパー。"""

import os
import ssl
import tomllib
from pathlib import Path

import certifi
import httpx
import streamlit as st
from google import genai
from google.genai import types

# このファイル(core/)の1つ上がプロジェクトルート。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL = "gemini-3.6-flash"
AVAILABLE_MODELS = ["gemini-3.6-flash"]


class GeminiConfigError(RuntimeError):
    """APIキーが設定されていない場合に送出される。"""


def _key_from_project_secrets() -> str | None:
    """`streamlit run` の起動ディレクトリに関係なく、プロジェクト同梱の
    .streamlit/secrets.toml から直接キーを読む。st.secrets は
    カレントディレクトリ基準でファイルを探すため、プロジェクト外から
    起動されると見つからない。そのフォールバック。"""
    path = _PROJECT_ROOT / ".streamlit" / "secrets.toml"
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    value = data.get("GEMINI_API_KEY")
    return value or None


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

    key = _key_from_project_secrets()
    if key:
        return key

    raise GeminiConfigError(
        f"{_PROJECT_ROOT / '.streamlit' / 'secrets.toml'} の GEMINI_API_KEY、"
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
