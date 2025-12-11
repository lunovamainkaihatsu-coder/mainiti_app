import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ============================
# 初期設定
# ============================
load_dotenv()

# 1. 環境変数（.env）から読む
api_key = os.getenv("OPENAI_API_KEY")

# 2. もし空なら、Streamlit の secrets から読む（Cloud 用）
if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = ""

# 3. OpenAI クライアントを作成
client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="ルナ式 気づかせAI β",
    page_icon="💬",
    layout="centered",
)

# ============================
# ヘッダー
# ============================
st.title("💬 ルナ式 気づかせAI β")
st.caption(
    "今の気持ちをルナにそっと打ち明けると、"
    "その裏にある本音と「今日やるたった1つの小さな一歩」を返してくれるアプリだよ。"
)

st.markdown(
    """
**注意:**  
このアプリはメンタルケアの“補助”であって、医療や専門カウンセリングの代わりにはならないよ。  
つらさが強いときは、専門機関や信頼できる人にも頼ってね。
"""
)

# ============================
# サイドバー
# ============================
with st.sidebar:
    st.subheader("🔧 設定 / 状態")
    if api_key:
        st.success("OpenAI APIキーが見つかりました ✅")
    else:
        st.error("OPENAI_API_KEY が見つかりません ❌\n.env または Streamlit secrets を確認してね。")

# ============================
# セッションステート（今日のログ用）
# ============================
if "logs" not in st.session_state:
    st.session_state.logs = []  # 各要素は dict

# ============================
# 気づかせAI（OpenAI呼び出し）
# ============================
def call_kizukase_ai(feeling_text: str, mood_label: str) -> str:
    """
    OpenAI API を呼び出して、
    指定フォーマットのテキストを返す。
    """
    # mood_label も一緒に投げて、文脈として使ってもらう
    user_prompt = f"""
今の気持ちのメモ:
- 気分カテゴリ: {mood_label}
- 具体的な気持ち: {feeling_text}

あなたは、優しくて落ち着いた雰囲気の日本語カウンセラー「ルナ」です。
相手を否定せず、「今の気持ち」をまず受け止めてから、
その裏にある本音やニーズをやわらかく言語化してください。

出力フォーマットは、必ず次のテンプレートに**日本語で**沿ってください。
追加の文章は書かず、このテンプレートの中だけで書いてください。

---
【表に出ている気持ち】
（相手が今感じている気持ちを、そのまま優しく言い換える）

【その裏にある本音・大事にしていること】
（その気持ちの裏側にある本音・願い・大事にしている価値観を言語化する）

【今日おすすめの小さな一歩】
（今の状態でも、ほんの少しだけできそうな具体的行動を1つだけ提案する）

【ルナからのやさしいひとこと】
（相手を責めず、存在そのものを肯定する短いメッセージ）
---
    """.strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 必要に応じて gpt-4o などに変更OK
        messages=[
            {
                "role": "system",
                "content": "あなたは優しくて現実的な日本語カウンセラーAI『ルナ』です。"
                           "相手を否定せず、安心できる言葉を使ってください。",
            },
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.9,
    )
    return response.choices[0].message.content


# ============================
# メイン入力エリア
# ============================
st.subheader("1️⃣ 今の気持ちをルナに教えてね")

mood_label = st.selectbox(
    "いまのざっくりとした気分",
    [
        "なんとなくモヤモヤする",
        "不安・焦りが強い",
        "イライラ・怒りっぽい",
        "疲れている・何もしたくない",
        "さみしい・孤独感がある",
        "なんとなく元気だけど、方向性が分からない",
        "言葉にしづらいけど、とにかく聞いてほしい",
    ],
)

feeling_text = st.text_area(
    "その気分について、ひとことでも長くてもOKだから、自由に書いてみてください。",
    height=150,
    placeholder="例）やることいっぱいなのに、何も進んでなくて自分がダメに思えてくる…",
)

col1, col2 = st.columns([2, 1])
with col1:
    submit = st.button("✨ ルナに気づかせてもらう", use_container_width=True)
with col2:
    clear = st.button("🧹 入力をクリア", use_container_width=True)

if clear:
    st.experimental_rerun()

# ============================
# 実行 & 結果表示
# ============================
if submit:
    if not feeling_text.strip():
        st.warning("今の気持ちを少しだけでも書いてからボタンを押してね。")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY が設定されていないため、AIに聞くことができません。")
    else:
        with st.spinner("ルナが、そっと気持ちを整理してくれているよ…"):
            try:
                result_text = call_kizukase_ai(feeling_text, mood_label)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

                # ログに追加
                st.session_state.logs.insert(
                    0,
                    {
                        "time": timestamp,
                        "mood": mood_label,
                        "input": feeling_text,
                        "output": result_text,
                    },
                )

                st.success("ルナからのメッセージが届いたよ 💌")
                st.markdown("### 2️⃣ 今日の『気づき』")
                st.markdown(result_text)

            except Exception as e:
                st.error("ごめんね、ルナ側でエラーが起きちゃったみたい…")
                st.code(str(e))


# ============================
# 今日のログ表示（セッション内）
# ============================
if st.session_state.logs:
    st.markdown("---")
    st.subheader("📒 今日のログ（このアプリを開いている間だけ保存されます）")

    for log in st.session_state.logs:
        with st.expander(f"{log['time']}｜{log['mood']}"):
            st.markdown("**あなたのメモ:**")
            st.write(log["input"])
            st.markdown("**ルナからのメッセージ:**")
            st.markdown(log["output"])
else:
    st.info("まだログはないよ。最初の気持ちをルナに話してみようか。")
