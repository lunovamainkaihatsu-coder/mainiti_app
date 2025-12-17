import streamlit as st

st.set_page_config(
    page_title="頭の中ごちゃごちゃ整理",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 頭の中ごちゃごちゃ整理")
st.write("今、頭にあることをそのまま書いてください。整理はアプリがやります。")

text = st.text_area(
    "今考えていること",
    height=200,
    placeholder="例：お金が不安、体調が悪い、やる気が出ない…"
)

if st.button("整理する"):
    if text.strip() == "":
        st.warning("何か書いてから押してね")
    else:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        st.subheader("📝 今考えていること（整理）")
        for l in lines:
            st.write("・", l)

        st.subheader("🎯 いちばん大事そうなこと")
        st.write(lines[0])

        st.subheader("👣 今日できる最小の一歩")
        st.write("深呼吸を1回して、今の状態を否定しない")
