import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day143：気分回復ガチャ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day143_recovery_gacha.json")

GACHA_ITEMS = [
    {
        "title": "💧 水を飲む",
        "desc": "まず一口だけでもOK。",
        "rarity": "N"
    },
    {
        "title": "🌤 外を見る",
        "desc": "30秒だけ空を見る。",
        "rarity": "N"
    },
    {
        "title": "🎵 好きな曲",
        "desc": "好きな曲を1曲だけ聴こう。",
        "rarity": "N"
    },
    {
        "title": "🫁 深呼吸",
        "desc": "ゆっくり3回呼吸してみよう。",
        "rarity": "N"
    },
    {
        "title": "🛏 5分休憩",
        "desc": "少しだけ身体を休めよう。",
        "rarity": "R"
    },
    {
        "title": "🚶 1分だけ歩く",
        "desc": "部屋の中でもOK。",
        "rarity": "R"
    },
    {
        "title": "🧘 肩回し",
        "desc": "肩をゆっくり10回回そう。",
        "rarity": "R"
    },
    {
        "title": "☀ 太陽チャージ",
        "desc": "窓際に行って光を浴びよう。",
        "rarity": "SR"
    },
    {
        "title": "🍫 ごほうびOK",
        "desc": "今日は少し甘やかしていい日。",
        "rarity": "SR"
    },
    {
        "title": "🌙 ルナの言葉",
        "desc": "ご主人、今日は生きてるだけでもちゃんと進んでるよ。",
        "rarity": "SSR"
    },
]

RARITY_COLORS = {
    "N": "#aaaaaa",
    "R": "#4fa3ff",
    "SR": "#bb66ff",
    "SSR": "#ffcc33",
}


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


def today_str():
    return date.today().isoformat()


def roll_gacha():
    weights = [40, 40, 40, 40, 25, 25, 25, 10, 10, 3]

    return random.choices(
        GACHA_ITEMS,
        weights=weights,
        k=1
    )[0]


def to_df(data):

    rows = []

    for x in data["logs"]:
        rows.append({
            "date": x["date"],
            "title": x["title"],
            "rarity": x["rarity"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("date", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎰",
    layout="centered"
)

st.title("🎰 Day143：気分回復ガチャ")
st.caption("小さな回復行動をガチャ感覚で引けるアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

st.divider()

if st.button("🎰 ガチャを引く！", type="primary"):

    result = roll_gacha()

    item = {
        "id": f"gacha_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "created_at": now_str(),
        "date": today_str(),
        "title": result["title"],
        "desc": result["desc"],
        "rarity": result["rarity"],
        "memo": "",
    }

    data["logs"].append(item)

    save_data(data)

    st.session_state["latest"] = item

    st.rerun()

latest = st.session_state.get("latest")

if latest:

    color = RARITY_COLORS.get(
        latest["rarity"],
        "#ffffff"
    )

    st.markdown(
        f"""
        <div style="
            padding: 24px;
            border-radius: 20px;
            border: 3px solid {color};
            text-align: center;
            margin-top: 20px;
        ">
            <h1>{latest['rarity']}</h1>
            <h2>{latest['title']}</h2>
            <p>{latest['desc']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    memo = st.text_area(
        "メモ",
        placeholder="やってみた感想とか"
    )

    if st.button("📝 メモ保存"):

        latest["memo"] = memo

        for x in data["logs"]:
            if x["id"] == latest["id"]:
                x.update(latest)

        save_data(data)

        st.success("保存したよ！")

st.divider()

st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")

else:

    st.dataframe(
        df,
        use_container_width=True,
        height=300
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day143_recovery_gacha.csv",
        mime="text/csv"
    )
