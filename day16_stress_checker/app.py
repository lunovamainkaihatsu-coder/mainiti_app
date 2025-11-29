import streamlit as st

st.set_page_config(page_title="ストレスチェッカー", page_icon="😵", layout="centered")

# --- カスタムCSS（ちょっとだけ雰囲気よく） ---
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #222733 0%, #1b1f29 40%, #151820 100%);
        color: #f5f5f5;
    }
    .stRadio > label {
        font-weight: 600;
    }
    .score-box {
        padding: 1rem 1.2rem;
        border-radius: 0.8rem;
        margin-top: 0.8rem;
    }
    .low { background: rgba(46, 204, 113, 0.15); border: 1px solid #2ecc71; }
    .mid { background: rgba(241, 196, 15, 0.12); border: 1px solid #f1c40f; }
    .high { background: rgba(231, 76, 60, 0.15); border: 1px solid #e74c3c; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("😵‍💫 今日のストレスチェッカー")
st.caption("※お医者さんの診断ではなく、いまの自分の様子をざっくり見るためのツールだよ。")


st.write("### ① ここ数日の状態をえらんでみてね")

questions = [
    "最近、理由もなくイライラすることが多い",
    "眠りが浅い・寝つきが悪い・夜中に目が覚める",
    "体がだるくて、やる気がわかない",
    "集中力が続かない・ぼーっとする",
    "頭痛・肩こり・胃の違和感など、体の不調をよく感じる",
    "常に不安や焦りが頭のどこかにある",
    "「楽しい」と感じる時間が減っている",
    "すぐに自分を責めてしまう・ダメ出ししがち",
]

options = {
    "全くない": 0,
    "たまにある": 1,
    "よくある": 2,
    "ほとんどいつも": 3,
}

scores = []

for q in questions:
    choice = st.radio(
        q,
        list(options.keys()),
        horizontal=True,
        key=q,
    )
    scores.append(options[choice])

if st.button("結果を見る"):
    total_score = sum(scores)
    max_score = len(questions) * 3
    level = total_score / max_score

    st.write("### ② 結果")

    st.write(f"あなたのストレススコア： **{total_score} / {max_score}**")
    st.progress(level)

    # レベル別コメント
    if total_score <= 8:
        level_text = "ストレスは今のところ**低め**みたい。"
        css_class = "low"
        advice = [
            "この状態をキープするために、好きなことをする時間を少しだけ確保しておこう。",
            "疲れを感じる前に、こまめに休憩を入れてあげて。",
            "「今日はここまでやれた自分えらい」と、1つだけでも自分をほめてみよう。",
        ]
    elif total_score <= 16:
        level_text = "ストレスは**やや高め**になってきているかも。"
        css_class = "mid"
        advice = [
            "今日は「完璧にやる」じゃなくて「60〜70％できたらOK」にしてみよう。",
            "5分だけでも深呼吸しながら、目を閉じてぼーっとする時間をとってみて。",
            "スマホ・SNSから少しだけ離れて、温かい飲み物を飲みながら休むのもおすすめ。",
        ]
    else:
        level_text = "ストレスが**かなり高い状態**かもしれない…！"
        css_class = "high"
        advice = [
            "今日は「がんばる日」じゃなくて「生き延びる日」にしてOKだよ。",
            "やることを3つじゃなくて、1つだけに絞って、それ以外は明日に回してみて。",
            "もし数週間レベルでつらさが続くようなら、専門家や相談窓口に頼るのも本当に大事だよ。",
        ]

    st.markdown(
        f"""
        <div class="score-box {css_class}">
        <b>{level_text}</b><br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("### ③ 今日やることを「ひとつだけ」選ぶ")

    choice = st.radio(
        "いまのあなたに近そうなものを、肩の力を抜いて選んでね。",
        [
            "5〜10分だけ、深呼吸しながら何も考えずぼーっとする",
            "温かい飲み物をゆっくり飲む時間をつくる",
            "タスクを1つだけに絞って、それができたら今日は合格にする",
            "軽くストレッチ or 近所を少し歩く",
            "今日は何も決めず、ただダラダラする自分をゆるす",
        ],
    )

    st.success(f"✅ 今日やること：**「{choice}」**")

    st.write("---")
    st.write("#### ひとことメッセージ")
    st.write(
        "今つらいのは、あなたがダメだからじゃなくて、ちゃんとがんばってきた証拠でもあるよ。"
        " 今日は「回復するために、意図的にさぼる」のもアリ。"
    )

else:
    st.info("下の質問に答えてから「結果を見る」を押してね。")
