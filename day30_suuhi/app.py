import streamlit as st
from datetime import date

# ページ設定
st.set_page_config(page_title="今日の数秘1桁うらない", page_icon="🔢")

st.title("🔢 今日の数秘1桁うらない")
st.write("日付の数字をぜんぶ足して、1〜9の数字から今日のメッセージを出すよ。")

# 数秘を計算する関数
def calc_number(d: date) -> int:
    digits = list(str(d.year) + f"{d.month:02d}" + f"{d.day:02d}")
    n = sum(int(x) for x in digits)
    while n > 9:
        n = sum(int(x) for x in str(n))
    return n

# 数字ごとのメッセージ
NUM_MESSAGES = {
    1: {
        "keyword": "スタート・行動",
        "message": "小さな一歩でOK。1ミリでも前に進めたら、今日は合格だよ。"
    },
    2: {
        "keyword": "やさしさ・バランス",
        "message": "自分にも他人にもやさしく。休むことも立派な行動だよ。"
    },
    3: {
        "keyword": "楽しさ・ひらめき",
        "message": "しんどい日でも、ちょっとだけクスッとできることを探してみて。"
    },
    4: {
        "keyword": "安定・土台づくり",
        "message": "今日は“崩さない”だけで十分。現状維持は立派な成果だよ。"
    },
    5: {
        "keyword": "変化・気分転換",
        "message": "いつもと違う飲み物やルーティンにしてみると、流れが軽くなるよ。"
    },
    6: {
        "keyword": "愛情・ケア",
        "message": "誰かを気づかう前に、自分の心と体をなでなでしてあげてね。"
    },
    7: {
        "keyword": "内省・ひとり時間",
        "message": "ひとりでぼーっとする時間も大事。考えすぎたら深呼吸だけしよう。"
    },
    8: {
        "keyword": "パワー・成果",
        "message": "今日は“やれたこと”に目を向けて。できなかったことは一旦保留。"
    },
    9: {
        "keyword": "手放し・リセット",
        "message": "もう抱えきれないものは、心の中でそっと『手放す』って宣言してみて。"
    },
}

# 日付入力（デフォルトは今日）
today = date.today()
selected_date = st.date_input("日付を選んでね（その日の運勢が出るよ）", value=today)

if st.button("今日の運勢を見る"):
    n = calc_number(selected_date)
    info = NUM_MESSAGES[n]

    st.markdown(f"## ✨ 今日の数字は **{n}**")
    st.markdown(f"**キーワード：{info['keyword']}**")
    st.write(info["message"])

    st.caption("※数秘術の考え方をベースにした、ゆる〜いメッセージだよ。気楽に読んでね。")
