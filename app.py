import random

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI大喜利アプリ（β）", page_icon="🎭")

st.title("AI大喜利アプリ（β）")

# -----------------------------
# セッションにAPIキーを保存
# -----------------------------
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# -----------------------------
# サイドバー：ページ切り替え
# -----------------------------
page = st.sidebar.radio("ページを選んでね", ["あそぶ", "APIキー設定＆使い方"])

# -----------------------------
# APIキー設定ページ
# -----------------------------
if page == "APIキー設定＆使い方":
    st.header("APIキー設定")

    st.write(
        "このアプリは OpenAI のAPIを使って、AIに大喜利の回答を考えてもらうよ。"
        "\n\nまずは **あなた自身の OpenAI APIキー** をここに入力してね。"
    )

    api_input = st.text_input(
        "OpenAI APIキーを入力（他人には絶対教えないでね）",
        type="password",
        value=st.session_state["api_key"],
        help="https://platform.openai.com/ の API Keys ページで作成できます。",
    )

    # 入力があればセッションに保存
    if api_input:
        st.session_state["api_key"] = api_input
        st.success("APIキーを保存したよ！左上の『あそぶ』ページから遊べるよ。")

    st.markdown("---")
    st.subheader("APIキーの取り方（ざっくり）")

    st.markdown(
        """
1. ブラウザで [OpenAIのサイト](https://platform.openai.com/) にアクセス  
2. ログインして、右上のアイコン → **"API Keys"** をクリック  
3. **"Create new secret key"** を押して新しいキーを作成  
4. 表示されたキーをコピーして、このページの入力欄に貼り付け  

※ このアプリにはあなたのPCブラウザから直接キーが送られます。  
　作者のAPIは使われないので、料金はあなたのアカウントに計上されます。
        """
    )

# -----------------------------
# あそぶページ（大喜利本体）
# -----------------------------
else:
    st.caption("※ まだAPIキーを入れていない人は、サイドバーの『APIキー設定＆使い方』から設定してね。")

    # お題リスト（増量）
    prompts = [
        "もしAIが総理大臣になったら最初にやりそうなこと",
        "未来の冷蔵庫のビックリ機能とは？",
        "こんなAIアシスタントはイヤだ…どんなの？",
        "学校に『AI係』という係が新設された。どんな仕事？",
        "10年後、スマホの代わりにみんなが持ち歩いているものとは？",
        "AIが突然、アイドルデビュー！その決めゼリフは？",
        "未来のコンビニに絶対ありそうな新サービスとは？",
        "AIと人間だけの合コン、ありがちな光景は？",
        "異世界転生したら、職業が『◯◯』だった。何？",
        "とんでもないバグが起きたAI。どんな挙動になった？",
        "新しい国語の教科書に追加された、まさかの新単元とは？",
        "AIが人生相談に本気で答えたら、どんなアドバイスをしそう？",
        "24時間推しアイドルと一緒にいられるチケット。その唯一の注意事項とは？",
        "未来の目覚まし時計、どんな方法で絶対に起こしてくる？",
        "AIが考えた『最高にダサい必殺技名』を教えてください。",
        "『AIだけの運動会』で起こりそうなハプニングとは？",
        "未来のラーメン屋、斬新すぎる新サービスとは？",
        "AIが書いたラブレターにありがちなことは？",
        "AIコンシェルジュが一日だけ人間になったら、まずやりそうなことは？",
        "AI時代の修学旅行、行き先と名物イベントを教えてください。",
    ]

    # APIキー確認
    if not st.session_state.get("api_key"):
        st.error("まだAPIキーが設定されていないよ。サイドバーの『APIキー設定＆使い方』から設定してね。")
    else:
        client = OpenAI(api_key=st.session_state["api_key"])

        if st.button("お題を出す！"):
            prompt = random.choice(prompts)
            st.subheader("お題")
            st.write(prompt)

            try:
                system_prompt = (
                    "あなたは面白いツッコミ・ボケをする日本語の大喜利AIです。"
                    "お題に対して、1〜2文くらいでテンポよく答えてください。"
                    "ブラックすぎるネタや誹謗中傷は避けて、ゆるく楽しい方向でお願いします。"
                )

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                )

                ai_text = response.choices[0].message.content

                st.subheader("AIの回答")
                st.write(ai_text)

            except Exception as e:
                st.error("API呼び出し中にエラーが起きちゃった… APIキーや残高、ネット環境を確認してみてね。")
                st.code(str(e))
