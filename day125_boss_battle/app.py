import streamlit as st
import json
import os
import random
from datetime import date, timedelta
import pandas as pd

APP_TITLE = "Day125：習慣ボス戦"
DATA_PATH = os.path.join("data", "day122_habit_tracker.json")

XP_PER_CHECK = 10

BOSSES = [
    {"name": "先延ばしドラゴン", "hp": 500},
    {"name": "やる気吸収スライム", "hp": 300},
    {"name": "思考停止ゴーレム", "hp": 700},
]


def load_data():
    if not os.path.exists(DATA_PATH):
        return {"habits": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_total_xp(habits):
    total = 0
    for h in habits:
        total += len(h.get("logs", [])) * XP_PER_CHECK
    return total


st.set_page_config(page_title=APP_TITLE, page_icon="👾", layout="wide")
st.title("👾 Day125：習慣ボス戦")
st.caption("習慣の力でボスを倒すアプリ。")

data = load_data()

if not data["habits"]:
    st.info("習慣データがないよ（Day122を使ってね）")
    st.stop()

# ----------------------------
# ボス選択
# ----------------------------
boss_names = [b["name"] for b in BOSSES]
selected_boss = st.selectbox("ボス選択", boss_names)

boss = next(b for b in BOSSES if b["name"] == selected_boss)

if "boss_hp" not in st.session_state:
    st.session_state.boss_hp = boss["hp"]

# ----------------------------
# プレイヤー
# ----------------------------
total_xp = calc_total_xp(data["habits"])
attack = total_xp // 10

st.subheader("プレイヤー")

col1, col2 = st.columns(2)

with col1:
    st.metric("総XP", total_xp)

with col2:
    st.metric("攻撃力", attack)

# ----------------------------
# ボス表示
# ----------------------------
st.subheader("ボス")

st.markdown(f"## {boss['name']}")
st.progress(st.session_state.boss_hp / boss["hp"])
st.write(f"HP：{st.session_state.boss_hp} / {boss['hp']}")

# ----------------------------
# 攻撃
# ----------------------------
if st.button("⚔️ 攻撃", type="primary"):
    damage = random.randint(int(attack*0.8), int(attack*1.2))
    st.session_state.boss_hp -= damage

    st.success(f"{damage} ダメージ！")

    if st.session_state.boss_hp <= 0:
        st.balloons()
        st.success("🎉 ボス撃破！！")
        st.session_state.boss_hp = boss["hp"]

# ----------------------------
# CSV
# ----------------------------
df = pd.DataFrame(data["habits"])

csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ CSV", data=csv)
