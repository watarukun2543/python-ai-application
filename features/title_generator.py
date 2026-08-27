"""タイトル・キャッチコピー生成ツール。"""

import streamlit as st

from features._common import run_generation

SYSTEM_INSTRUCTION = (
    "あなたはコピーライティングのプロフェッショナルです。"
    "与えられた内容に合う日本語のタイトル・キャッチコピー案を、番号付きリストで出力してください。"
)

STYLE_INSTRUCTIONS = {
    "SEO重視": "検索されやすいキーワードを含め、簡潔で分かりやすいタイトルにしてください。",
    "キャッチー": "読者の興味を引く、インパクトのある表現にしてください。",
    "シンプル": "装飾を抑えた、簡潔で誠実な表現にしてください。",
}


def _build_prompt(content, count, style) -> str:
    return "\n".join(
        [
            f"以下の内容に合うタイトル・キャッチコピー案を{count}個作成してください。",
            f"スタイル: {style}",
            f"指示: {STYLE_INSTRUCTIONS[style]}",
            "---内容---",
            content,
        ]
    )


def render(model: str, temperature: float) -> None:
    st.header("タイトル・キャッチコピー生成")

    content = st.text_area("記事の概要または本文", height=200, max_chars=30000, placeholder="タイトルを付けたい記事の概要や本文を入力してください")
    count = st.slider("生成数", min_value=3, max_value=10, value=5)
    style = st.selectbox("スタイル", list(STYLE_INSTRUCTIONS.keys()))

    if st.button("タイトルを生成", type="primary", key="title_generate"):
        if not content.strip():
            st.warning("記事の概要または本文を入力してください。")
        else:
            prompt = _build_prompt(content, count, style)
            result = run_generation(
                prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                model=model,
                temperature=temperature,
                spinner="タイトルを生成中...",
            )
            if result:
                st.session_state["title_output"] = result

    if st.session_state.get("title_output"):
        # モデル出力はプレーンテキストで表示（st.markdown 経由の画像ビーコン等を避ける）。
        st.text_area("生成結果", value=st.session_state["title_output"], height=300)
