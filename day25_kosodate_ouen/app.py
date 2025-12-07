import streamlit as st

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(
    page_title="こども気分チェッカー",
    page_icon="👶",
    layout="centered",
)

# -----------------------------
# 簡単なスタイル調整
# -----------------------------
st.markdown(
    """
    <style>
    .big-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-text {
        font-size: 14px;
        color: #555555;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.2rem;
    }
    .advice-box {
        font-size: 16px;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# タイトル
# -----------------------------
st.markdown('<div class="big-title">👶 こども気分チェッカー & 親フォロー</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">子どもの「今日の様子」と、あなたの「疲れ具合」から、関わり方のコツと、親への一言メッセージをお届けします。</div>',
    unsafe_allow_html=True,
)

st.write("---")

# -----------------------------
# 入力エリア
# -----------------------------
st.markdown('<div class="section-title">1️⃣ こどもの様子をえらんでね</div>', unsafe_allow_html=True)

mood_labels = {
    "ごきげん 😊": "ごきげん",
    "ふつう 🙂": "ふつう",
    "ちょっと不機嫌 😕": "ちょっと不機嫌",
    "すごく不機嫌 😡": "すごく不機嫌",
    "ぐったり・体調いまいち 🤒": "ぐったり",
    "ハイテンション 🎉": "ハイテンション",
}

mood_choice = st.radio(
    "今日のこどもの雰囲気はどれが近い？",
    options=list(mood_labels.keys()),
    horizontal=True,
)

child_mood = mood_labels[mood_choice]

st.markdown('<div class="section-title">2️⃣ あなたの疲れ具合</div>', unsafe_allow_html=True)
parent_tired = st.slider(
    "今のあなたの疲れレベル（1＝まだ余裕、5＝正直かなり限界…）",
    min_value=1,
    max_value=5,
    value=3,
)

st.markdown('<div class="section-title">3️⃣ こどもの年齢</div>', unsafe_allow_html=True)
age_group = st.selectbox(
    "おおよその年齢帯をえらんでください",
    ["未就学（0〜6歳くらい）", "小学生くらい", "中学生以上"],
)


# -----------------------------
# アドバイス生成ロジック
# -----------------------------
def get_child_advice(mood: str, age_group: str) -> str:
    """子どもへの関わり方アドバイスを返す"""
    if mood == "ごきげん":
        if age_group == "未就学（0〜6歳くらい）":
            return (
                "今日はごきげんみたいだね。スキンシップ多めで、"
                "「一緒に遊べてうれしいな」と言葉にしてあげると自己肯定感アップにつながるよ。"
            )
        elif age_group == "小学生くらい":
            return (
                "ごきげんモードの日は、子どもの話をじっくり聞くチャンス。"
                "今日楽しかったことを質問して、共感をたっぷり返してあげてね。"
            )
        else:
            return (
                "機嫌が良い時は、つい親も安心して放置しがち。"
                "少しだけ「最近どう？」と世間話をして、味方でいることをそっと伝えてあげて。"
            )

    if mood == "ふつう":
        return (
            "特に荒れていない“ふつう”の日こそ、穏やかなルーティンが安心感につながるよ。"
            "いつも通りの声かけと、少しだけ「ありがとう」「助かったよ」を増やしてみてね。"
        )

    if mood == "ちょっと不機嫌":
        if age_group == "未就学（0〜6歳くらい）":
            return (
                "ちょっと不機嫌な時は、言葉よりスキンシップ。"
                "抱っこや膝の上で「イヤだったね」と気持ちを代弁してあげると落ち着きやすいよ。"
            )
        else:
            return (
                "少しトゲトゲしている時は、理由を聞き出すよりも、"
                "「そう感じてるんだね」と受け止める一言を先に。"
                "落ち着いてから、短めに話を聞いてあげると◎。"
            )

    if mood == "すごく不機嫌":
        return (
            "かなり不機嫌な時は、まず親子ともにクールダウンが最優先。"
            "すぐに諭そうとせず、物理的な距離や時間を少しおいてから、"
            "「さっきはお互いしんどかったね」と振り返ると建設的になりやすいよ。"
        )

    if mood == "ぐったり":
        return (
            "ぐったりしている時は、頑張らせるより休ませる選択が吉。"
            "予定や勉強を少しゆるめて、水分・睡眠・ぬくもりを優先してあげてね。"
        )

    if mood == "ハイテンション":
        if age_group == "未就学（0〜6歳くらい）":
            return (
                "ハイテンションな時は、危なくない範囲で一緒に発散してあげると◎。"
                "最後に「おしまいの合図」（歌やポーズ）を決めておくと、切り替えやすくなるよ。"
            )
        else:
            return (
                "テンションが高い時は、叱るより“ルールだけ短く伝える”がコツ。"
                "「ここまではOK、これはNG」と線引きをシンプルに伝えて、"
                "OKゾーンで思い切り楽しませてあげてね。"
            )

    # 想定外の時のフォールバック
    return "今日はいつもと少し違う様子かもしれないね。まずはよく観察して、安心できる雰囲気をつくってあげてね。"


def get_parent_message(tired_level: int, mood: str) -> str:
    """親へのフォローメッセージを返す"""
    base = ""

    if tired_level <= 2:
        base = (
            "今日はまだ少し余裕があるみたい。"
            "その余裕は、ここまでたどり着くまでに積み重ねてきた努力の証だよ。"
        )
    elif tired_level == 3:
        base = (
            "ほどよく疲れもたまってきているね。"
            "それでも今日も向き合おうとしている時点で、あなたは十分に素敵な親だよ。"
        )
    elif tired_level == 4:
        base = (
            "だいぶお疲れさま…。ここまでよく踏ん張ってきたね。"
            "無理して完璧を目指さなくていいから、どこか1つだけ「サボる場所」を決めてね。"
        )
    else:
        base = (
            "正直かなり限界に近いよね…。それでもこのアプリを開いている時点で、"
            "あなたは“ちゃんと向き合おうとしている親”だよ。今日は100点を目指さなくていい。"
        )

    # 子どもの機嫌による一言を追加
    add = ""
    if mood in ["すごく不機嫌", "ちょっと不機嫌"]:
        add = (
            " こどもが荒れている日は、自分までダメ親だと感じがちだけど、"
            "「しんどい日もあるよね」と自分に言ってあげてね。"
        )
    elif mood == "ぐったり":
        add = (
            " こどもの体調が不安だと、あなたの心も落ち着かないよね。"
            " 心配しているだけで、もう十分すぎるほど愛情を注いでいる証拠だよ。"
        )
    elif mood == "ごきげん":
        add = (
            " こどもがごきげんな日は、あなたのがんばりがちゃんと届いている日。"
            " 今日は自分にも小さなご褒美をあげてね。"
        )
    else:
        add = " どんな一日でも、今日をここまで連れてきた時点で、あなたは本当にがんばってる。"

    return base + add


# -----------------------------
# 結果表示
# -----------------------------
st.write("---")

if st.button("✨ アドバイスを見る"):
    child_advice = get_child_advice(child_mood, age_group)
    parent_msg = get_parent_message(parent_tired, child_mood)

    st.markdown('<div class="section-title">🧒 こどもへの関わり方のヒント</div>', unsafe_allow_html=True)
    st.info(f"【今日の様子】{child_mood}\n\n{child_advice}")

    st.markdown('<div class="section-title">💌 あなたへの一言メッセージ</div>', unsafe_allow_html=True)
    st.success(parent_msg)

    st.caption("※このアプリは医療・専門相談の代わりではありません。しんどさが続くときは、専門機関への相談も頼ってね。")
else:
    st.markdown(
        '<div class="advice-box">上の項目をえらんでから「✨ アドバイスを見る」ボタンを押してね。</div>',
        unsafe_allow_html=True,
    )
