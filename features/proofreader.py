"""校正・リライトツール。"""

import streamlit as st

from features._common import run_generation

SYSTEM_INSTRUCTION = (
    "あなたは日本語校正のプロフェッショナルです。"
    "指定されたモードに応じて文章を修正し、"
    "「修正版」のあとに「主な変更点」を箇条書きで簡潔に説明してください。"
)

MODE_INSTRUCTIONS = {
    "誤字脱字チェック": "誤字脱字や文法的な誤りのみを修正してください。文体や表現は極力変えないでください。",
    "文体統一": "文体(です・ます調 / だ・である調など)を統一し、表記ゆれを修正してください。",
    "リライト提案": "より読みやすく自然な表現になるよう、文章全体をリライトしてください。",
}


def _build_prompt(text, mode, target_tone) -> str:
    lines = [
        "以下の文章を校正・修正してください。",
        f"モード: {mode}",
        f"指示: {MODE_INSTRUCTIONS[mode]}",
    ]
    if target_tone:
        lines.append(f"変更先のトーン: {target_tone}")
    lines += ["---元の文章---", text]
    return "\n".join(lines)


def render(model: str, temperature: float) -> None:
    st.header("校正・リライト")

    text = st.text_area("校正したい文章", height=250, max_chars=30000, placeholder="校正対象の文章を貼り付けてください")
    mode = st.selectbox("モード", list(MODE_INSTRUCTIONS.keys()))
    target_tone = st.text_input("変更先のトーン(任意)", max_chars=200, placeholder="例: もっとフォーマルに")

    if st.button("校正する", type="primary", key="proofread_generate"):
        if not text.strip():
            st.warning("校正したい文章を入力してください。")
        else:
            prompt = _build_prompt(text, mode, target_tone)
            result = run_generation(
                prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                model=model,
                temperature=temperature,
                spinner="校正中...",
            )
            if result:
                st.session_state["proofread_output"] = result

    if st.session_state.get("proofread_output"):
        # モデル出力はプレーンテキストで表示する。st.markdown だと、貼り付け元が
        # 攻撃者由来の場合に画像ビーコンや誘導リンクを描画してしまう恐れがある。
        st.text_area("校正結果", value=st.session_state["proofread_output"], height=400)
