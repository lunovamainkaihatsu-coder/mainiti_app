import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Day87 Life Dashboard", page_icon="🌟")

st.title("🌟 Life Dashboard")
st.write("今日の状態を一目でチェック")

# -----------------
# エネルギー
# -----------------

energy = st.slider("今日のエネルギー", 0, 100, 50)

if energy > 70:
    state = "🔥 攻めの日"
elif energy > 40:
    state = "⚖️ 普通の日"
else:
    state = "🌙 回復の日"

st.subheader("現在の状態")
st.success(state)

# -----------------
# 行動カウント
# -----------------

st.subheader("今日の行動")

tasks = st.number_input("行動数", 0, 50, 3)

if tasks >= 10:
    st.success("めちゃくちゃ行動してる！")
elif tasks >= 5:
    st.info("いい感じ！")
else:
    st.warning("もう少し動いてみよう")

# -----------------
# アイデア
# -----------------

st.subheader("アイデア")

ideas = st.number_input("保存アイデア数", 0, 500, 10)

if ideas > 50:
    st.success("アイデア資産が増えてきた")
elif ideas > 10:
    st.info("いいペース")
else:
    st.warning("もっと思いついたら保存しよう")

# -----------------
# 収益アイデア
# -----------------

st.subheader("収益アイデア")

money_ideas = st.number_input("収益化アイデア", 0, 100, 2)

if money_ideas > 10:
    st.success("収益化の芽が多い")
elif money_ideas > 3:
    st.info("育てれば収益になる")
else:
    st.warning("収益アイデアを増やそう")

# -----------------
# ルナメッセージ
# -----------------

messages = [
"今日は一歩でも前に進めばOK。",
"ご主人、焦らなくてもちゃんと進んでる。",
"行動した分だけ未来が変わる。",
"アイデアは資産。小さくても残そう。",
"今日は未来を作る日。"
]

st.subheader("今日のメッセージ")

st.info(random.choice(messages))
