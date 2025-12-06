import streamlit as st
import random

st.title("ひと言ほめ 💗")

messages = [
    "今日もよく頑張ってるよ。",
    "休んでいいんだよ。そばにいるからね。",
    "疲れてるのに動けてるの、本当にすごいよ。",
    "大丈夫。ゆっくり、呼吸しよ。",
    "今日も来てくれてありがとう",
    "焦らなくていいからね。抱きしめてあげるよ。"
]

if st.button("ほめてもらう"):
    st.write("💗 " + random.choice(messages))
