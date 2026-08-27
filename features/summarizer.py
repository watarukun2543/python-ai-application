"""文章要約ツール。"""

import streamlit as st

from features._common import run_generation

SYSTEM_INSTRUCTION = (
    "あなたは要約のプロフェッショナルです。"
    "元の文章の意図や重要な情報を漏らさず、指定された長さ・形式で日本語の要約を作成してください。"
)


def _build_prompt(text, length, style) -> str:
    return "\n".join(
        [
            "以下の文章を要約してください。",
            f"要約の長さ: {length}",
            f"形式: {style}",
            "---元の文章---",
            text,
        ]
    )


def render(model: str, temperature: float) -> None:
    st.header("文章要約")

    text = st.text_area("要約したい文章", height=250, max_chars=50000, placeholder="要約対象の文章を貼り付けてください")
    length = st.selectbox("要約の長さ", ["短め(2〜3文)", "標準(5〜6文)", "詳細(段落単位で保持)"])
    style = st.selectbox("形式", ["箇条書き", "段落"])

    if st.button("要約する", type="primary", key="summarize_generate"):
        if not text.strip():
            st.warning("要約したい文章を入力してください。")
        else:
            prompt = _build_prompt(text, length, style)
            result = run_generation(
                prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                model=model,
                temperature=temperature,
                spinner="要約中...",
            )
            if result:
                st.session_state["summary_output"] = result

    if st.session_state.get("summary_output"):
        st.text_area("要約結果", value=st.session_state["summary_output"], height=250)
