"""メール返信文作成ツール。"""

import streamlit as st

from features._common import run_generation

SYSTEM_INSTRUCTION = (
    "あなたはビジネスメール作成のアシスタントです。"
    "受け取ったメールの文脈を踏まえ、自然で失礼のない返信文を作成してください。"
    "宛名・署名は簡潔にし、本文の要点を明確に伝えてください。"
)


def _build_prompt(original, points, tone, language) -> str:
    lines = [
        "以下の受信メールに対する返信文を作成してください。",
        "---受信メール---",
        original,
        "---",
        f"返信で伝えたい要点・意図: {points or '本文の内容に自然に応答する'}",
        f"トーン: {tone}",
        f"言語: {language}",
    ]
    return "\n".join(lines)


def render(model: str, temperature: float) -> None:
    st.header("メール返信文作成")

    original = st.text_area("受信したメール本文", height=200, max_chars=20000, placeholder="返信対象のメール本文を貼り付けてください")
    points = st.text_area("返信の要点・意図(任意)", max_chars=2000, placeholder="例: 来週の打ち合わせは金曜午後で調整可能と伝えたい")
    tone = st.selectbox("トーン", ["丁寧・フォーマル", "カジュアル", "謝罪", "感謝"])
    language = st.selectbox("言語", ["日本語", "英語"])

    if st.button("返信文を生成", type="primary", key="email_generate"):
        if not original.strip():
            st.warning("受信したメール本文を入力してください。")
        else:
            prompt = _build_prompt(original, points, tone, language)
            result = run_generation(
                prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                model=model,
                temperature=temperature,
                spinner="返信文を生成中...",
            )
            if result:
                st.session_state["email_output"] = result

    if st.session_state.get("email_output"):
        st.text_area("生成結果", value=st.session_state["email_output"], height=300)
