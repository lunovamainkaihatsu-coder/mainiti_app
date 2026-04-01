import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day100：称号演出ガチャ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day100_title_gacha.json")

RARITY = [
    ("N", 0.55),
    ("R", 0.27),
    ("SR", 0.13),
    ("SSR", 0.05),
]

TITLES = {
    "N": [
        ("再起動者", "何度でも立ち上がる者"),
        ("小さな前進者", "一歩ずつ進む者"),
        ("継続の種", "未来を育て始めた者"),
    ],
    "R": [
        ("流れを変える者", "現実に小さな変化を起こす者"),
        ("選び続ける者", "迷いながらも進む者"),
        ("意志の灯火", "消えない火を持つ者"),
    ],
    "SR": [
        ("未来創造者", "現実を自ら作り始めた者"),
        ("覚醒前夜", "大きな変化の直前にいる者"),
    ],
    "SSR": [
        ("運命書き換え者", "自らの人生を書き換える存在"),
        ("選ばれし進行者", "未来に向かって進むことを選んだ者"),
    ],
}

LUNA_LINES = {
    "N": "ご主人、ちゃんと進んでるよ。",
    "R": "いいね、その流れ来てるよ。",
    "SR": "…これ、かなりいい位置にいるよ。",
    "SSR": "ご主人…これは、すごいよ。",
}


# ----------------------------
# storage
# ----------------------------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def pick_rarity():
    r = random.random()
    acc = 0
    for rarity, prob in RARITY:
        acc += prob
        if r <= acc:
            return rarity
    return "N"


def roll_title():
    rarity = pick_rarity()
    name, desc = random.choice(TITLES[rarity])

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "rarity": rarity,
        "title": name,
        "desc": desc,
        "luna": LUNA_LINES[rarity],
        "favorite": False,
    }


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "rarity": x["rarity"],
            "title": x["title"],
            "favorite": x.get("favorite", False),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="wide")
st.title("✨ Day100：称号演出ガチャ")
st.caption("あなたにふさわしい称号を授ける")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

if st.button("🎲 称号を引く", type="primary"):
    result = roll_title()
    data["logs"].append(result)
    save_data(data)
    st.session_state["latest"] = result
    st.rerun()

st.divider()

latest = st.session_state.get("latest")
if latest:
    if latest["rarity"] == "SSR":
        st.success("✨✨✨ SSR ✨✨✨")
    elif latest["rarity"] == "SR":
        st.info("🌟 SR 🌟")
    elif latest["rarity"] == "R":
        st.warning("⭐ R ⭐")
    else:
        st.write("N")

    st.markdown(f"## {latest['title']}")
    st.write(latest["desc"])

    st.markdown("### ルナの声")
    st.info(latest["luna"])

    fav = st.checkbox("⭐ お気に入り", value=latest.get("favorite", False))
    if fav != latest.get("favorite", False):
        latest["favorite"] = fav
        for row in data["logs"]:
            if row["id"] == latest["id"]:
                row["favorite"] = fav
        save_data(data)

st.divider()

st.subheader("履歴")

df = to_df(data)
if df.empty:
    st.write("まだなし")
else:
    st.dataframe(df)
