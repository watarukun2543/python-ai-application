"""ブログ記事執筆ツール。"""

import streamlit as st

from features._common import run_generation

SYSTEM_INSTRUCTION = (
    "あなたはプロのブログライターです。読者に価値のある、"
    "読みやすく自然な日本語のブログ記事を作成してください。"
    "見出し(##)を使って構成し、導入・本文・まとめの流れを意識してください。"
)


def _build_prompt(theme, audience, length, tone, extra) -> str:
    lines = [
        f"以下の条件でブログ記事のドラフトを作成してください。",
        f"テーマ・キーワード: {theme}",
        f"想定読者: {audience or '特に指定なし'}",
        f"文字数の目安: {length}",
        f"トーン: {tone}",
    ]
    if extra:
        lines.append(f"追加の指示: {extra}")
    return "\n".join(lines)


def render(model: str, temperature: float) -> None:
    st.header("ブログ記事執筆")

    theme = st.text_input("テーマ・キーワード", max_chars=200, placeholder="例: 在宅ワークの生産性を上げる方法")
    audience = st.text_input("想定読者", max_chars=200, placeholder="例: リモートワーク初心者")
    length = st.selectbox("文字数の目安", ["800字程度", "1500字程度", "3000字程度"], index=1)
    tone = st.selectbox("トーン", ["フォーマル", "カジュアル", "専門的", "親しみやすい"])
    extra = st.text_area("追加の指示(任意)", max_chars=2000, placeholder="含めてほしい内容、避けたい表現など")

    if st.button("記事を生成", type="primary", key="blog_generate"):
        if not theme.strip():
            st.warning("テーマ・キーワードを入力してください。")
        else:
            prompt = _build_prompt(theme, audience, length, tone, extra)
            result = run_generation(
                prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                model=model,
                temperature=temperature,
                spinner="記事を生成中...",
            )
            if result:
                st.session_state["blog_output"] = result

    if st.session_state.get("blog_output"):
        st.text_area("生成結果", value=st.session_state["blog_output"], height=400)
