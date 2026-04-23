import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day117：ひとことクエスト発生"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day117_quest_event.json")

QUESTS = [
    {
        "title": "クエスト：最初の一歩",
        "desc": "何かを5分だけやる",
        "reward": "やる気 +1",
        "luna": "ご主人、このクエストは軽いけど効果あるよ。"
    },
    {
        "title": "クエスト：整える者",
        "desc": "机の上を1か所整える",
        "reward": "集中力 +1",
        "luna": "環境変わると流れも変わるよ。"
    },
    {
        "title": "クエスト：回復の儀",
        "desc": "深呼吸を3回する",
        "reward": "安定 +1",
        "luna": "まずは整えるところからいこっか。"
    },
    {
        "title": "クエスト：接触任務",
        "desc": "後回しを1つ開く",
        "reward": "停滞解除 +1",
        "luna": "終わらせなくていい、触るだけでOK。"
    },
    {
        "title": "クエスト：記録者",
        "desc": "1行メモを書く",
        "reward": "未来ポイント +1",
        "luna": "その1行、あとで効いてくるよ。"
    },
    {
        "title": "クエスト：観測者",
        "desc": "今の気分を1つ言葉にする",
        "reward": "自己理解 +1",
        "luna": "言葉にすると、ちょっと整理されるよ。"
    },
]

RARE_QUESTS = [
    {
        "title": "レアクエスト：運命分岐",
        "desc": "いちばん重要なことを3分やる",
        "reward": "未来変動 +10",
        "luna": "ご主人、今日はちょっと特別な分岐かも。"
    },
    {
        "title": "レアクエスト：覚醒の一手",
        "desc": "今すぐ1つ行動する",
        "reward": "覚醒 +5",
        "luna": "この一手、流れ変えるかもよ。"
    },
]


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


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "title": x["title"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def draw_quest():
    if random.random() < 0.1:
        item = random.choice(RARE_QUESTS)
        rarity = "SR"
    else:
        item = random.choice(QUESTS)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "title": item["title"],
        "desc": item["desc"],
        "reward": item["reward"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="⚔️", layout="wide")
st.title("⚔️ Day117：ひとことクエスト発生")
st.caption("今日の小さなクエストを受け取るアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1,1])

with left:
    if st.button("⚔️ クエスト発生", type="primary"):
        result = draw_quest()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    latest = st.session_state.get("latest")
    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レアクエスト ✨")

        st.markdown(f"## {latest['title']}")
        st.write(latest["desc"])

        st.markdown("### 報酬")
        st.success(latest["reward"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

st.divider()

df = to_df(data)
if not df.empty:
    st.dataframe(df)
