import random
import streamlit as st

st.set_page_config(page_title="必殺技メーカー", layout="centered")

st.title("💥 必殺技メーカー")
st.caption("ボタンを押して、あなただけの必殺技を生み出せ！")


# -----------------------------
# ワードリスト
# -----------------------------
prefix = [
    "天翔", "紅蓮", "漆黒", "雷鳴", "蒼炎",
    "銀河", "閃光", "覇王", "極光", "神速",
    "暗黒", "天空", "無限", "絶対", "終焉"
]

middle = [
    "爆裂", "斬撃", "衝撃", "旋風", "流星",
    "龍撃", "烈火", "閃刃", "轟雷", "破壊",
    "零式", "究極", "無双", "超越"
]

suffix = [
    "ブレイカー", "インパクト", "クラッシュ",
    "スラッシュ", "ストライク", "キャノン",
    "スマッシュ", "フィニッシュ", "バースト",
    "エクスプロージョン", "ジャッジメント"
]


# -----------------------------
# 生成関数
# -----------------------------
def make_skill():
    return f"{random.choice(prefix)}{random.choice(middle)}{random.choice(suffix)}！！"


# -----------------------------
# UI
# -----------------------------
if "skill" not in st.session_state:
    st.session_state.skill = make_skill()

st.divider()

st.header(f"🔥 {st.session_state.skill}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🎲 生成！", use_container_width=True):
        st.session_state.skill = make_skill()
        st.rerun()

with col2:
    if st.button("📋 コピー用表示", use_container_width=True):
        st.code(st.session_state.skill)

st.divider()

st.caption("🌙 これで世界を救え、ご主人。")
