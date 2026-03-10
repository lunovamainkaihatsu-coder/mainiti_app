import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="Day90 Achievement", page_icon="🏆")

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "achievements.json")

os.makedirs(DATA_DIR, exist_ok=True)

# -------------------
# 称号定義
# -------------------

ACHIEVEMENTS = [
    {"name": "再起動者", "condition": 3, "desc": "3日行動した"},
    {"name": "習慣の芽", "condition": 7, "desc": "7日行動した"},
    {"name": "継続者", "condition": 14, "desc": "14日行動した"},
    {"name": "ビルダー", "condition": 10, "desc": "アプリ10個"},
    {"name": "発想の泉", "condition": 50, "desc": "アイデア50個"},
    {"name": "覚醒者", "condition": 100, "desc": "XP100"},
]

# -------------------
# データロード
# -------------------

def load():
    if not os.path.exists(DATA_FILE):
        return {"progress": 0}
    with open(DATA_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

data = load()

# -------------------
# UI
# -------------------

st.title("🏆 称号コレクション")

progress = st.number_input("現在の進行値",0,500,data["progress"])

if st.button("更新"):
    data["progress"] = progress
    save(data)
    st.success("保存した")

st.divider()

unlocked = []
locked = []

for a in ACHIEVEMENTS:
    if progress >= a["condition"]:
        unlocked.append(a)
    else:
        locked.append(a)

st.subheader("解放済み称号")

if unlocked:
    for a in unlocked:
        st.success(f"🏆 {a['name']} - {a['desc']}")
else:
    st.write("まだなし")

st.subheader("未解放称号")

for a in locked:
    st.info(f"🔒 {a['name']} - 条件:{a['condition']}")

rate = int(len(unlocked)/len(ACHIEVEMENTS)*100)

st.divider()

st.metric("達成率",f"{rate}%")

st.progress(rate/100)
