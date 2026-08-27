# AI Writing Tools

Streamlit + Google Gemini で作った個人用の AI ライティングツール集。サイドバーでツールを切り替える単一ページアプリで、各ツールはフォーム入力からプロンプトを組み立てて Gemini を呼び出し、結果を表示する。

## ツール

| ツール | 内容 |
|--------|------|
| ブログ記事執筆 | テーマ・読者・文字数・トーンからブログ記事のドラフトを生成 |
| メール返信文作成 | 受信メール本文と要点から返信文のドラフトを生成 |
| 文章要約 | 長さ・形式を指定して文章を要約 |
| 校正・リライト | 誤字脱字チェック / 文体統一 / リライト提案 |
| タイトル・キャッチコピー生成 | 内容に合うタイトル案を複数生成 |

## セットアップ

```bash
pip install -r requirements.txt
```

Gemini API キーを設定する（どちらか一方）:

- `.streamlit/secrets.toml` に記述（`.streamlit/secrets.toml.example` をコピーして編集）
  ```toml
  GEMINI_API_KEY = "your-api-key"
  ```
- または環境変数 `GEMINI_API_KEY`

API キーの解決は `core/gemini_client.py:_resolve_api_key` を参照。

## 起動

```bash
streamlit run app.py
```

## 構成

- `app.py` — エントリーポイント。`TOOLS` dict でラベルと機能モジュールを対応付け、サイドバー（ツール選択・モデル選択・temperature）を描画し、選択ツールの `render()` を呼ぶ。
- `core/gemini_client.py` — Gemini API を呼ぶ唯一の場所。`generate(prompt, *, system_instruction, model, temperature) -> str` を公開。`genai.Client` は `@st.cache_resource` で1回だけ構築。
- `features/_common.py` — 各機能モジュールが共有する `run_generation(...)`。`st.spinner` でラップし、`GeminiConfigError` と一般例外を捕捉して `st.error` で通知、失敗時は `None` を返す。プロンプトインジェクション対策の `INJECTION_GUARD` を system_instruction に付与する。
- `features/*.py` — 1ツール = 1モジュール。`SYSTEM_INSTRUCTION`、`_build_prompt(...)`、`render(model, temperature)` の3要素で構成。生成結果は `st.session_state["<tool>_output"]` に保持し再描画に耐える。

新しいツールを追加するには `features/new_tool.py` を同じ形で作り、`app.py` の `TOOLS` に登録する。

## 補足

- `core/gemini_client.py` は、ローカルの SSL 検査プロキシ（アンチウイルス）対策として `ssl.SSLContext` の `VERIFY_X509_STRICT` を無効化し、`httpx.Client` / `httpx.AsyncClient` 経由で `genai.Client` に注入している。証明書チェーンとホスト名の検証自体は有効。
- 利用可能なモデルは `core/gemini_client.py` の `DEFAULT_MODEL` / `AVAILABLE_MODELS` にハードコード。
- テスト・リンタ・ビルドステップは未設定。
