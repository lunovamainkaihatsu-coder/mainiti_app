# app.py
from __future__ import annotations

import datetime as dt

import streamlit as st

APP_TITLE = "今年、まだこれだけある"
YEAR = dt.date.today().year

st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption("減っているのではなく、まだ“ある”。")

now = dt.datetime.now()
end = dt.datetime(YEAR, 12, 31, 23, 59, 59)

remaining = end - now
total_seconds = int(remaining.total_seconds())

if total_seconds < 0:
    total_seconds = 0

days = total_seconds // (24 * 3600)
hours = (total_seconds % (24 * 3600)) // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

# メイン表示
st.markdown(
    f"""
    <div style="text-align:center; font-size:28px; line-height:1.6;">
        今年は、まだ<br>
        <strong>{days}日 {hours}時間 {minutes}分</strong><br>
        あります
        <div style="font-size:14px; color:#777; margin-top:8px;">
            （{seconds} 秒）
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# メッセージ
if days >= 300:
    msg = "まだ始まったばかり。焦る必要はない。"
elif days >= 100:
    msg = "十分な時間がある。選び直していい。"
elif days >= 30:
    msg = "まだ選択肢は残っている。"
elif days >= 1:
    msg = "今日は今日だけを見ればいい。"
else:
    msg = "ここまで来た。それでいい。"

st.success(msg)

st.divider()
st.caption("※ この数字は、あなたを急かすためのものではありません。")
