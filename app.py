"""個人用AIライティングツール - Streamlitエントリーポイント。"""

import streamlit as st

from core.gemini_client import AVAILABLE_MODELS, DEFAULT_MODEL
from features import blog_writer, email_reply, proofreader, summarizer, title_generator

st.set_page_config(page_title="AI Writing Tools", page_icon="✍️", layout="wide")

TOOLS = {
    "ブログ記事執筆": blog_writer,
    "メール返信文作成": email_reply,
    "文章要約": summarizer,
    "校正・リライト": proofreader,
    "タイトル・キャッチコピー生成": title_generator,
}

st.sidebar.title("✍️ AI Writing Tools")
selected_tool = st.sidebar.radio("ツールを選択", list(TOOLS.keys()))

st.sidebar.caption(
    "入力した内容は Google Gemini API に送信されます。"
    "個人情報や機密情報は入力しないでください。"
)

with st.sidebar.expander("詳細設定"):
    model = st.selectbox("モデル", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(DEFAULT_MODEL))
    temperature = st.slider("temperature(創造性)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

TOOLS[selected_tool].render(model=model, temperature=temperature)
