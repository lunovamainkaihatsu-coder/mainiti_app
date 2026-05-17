import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day114：ルナの一言回復薬"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day114_recovery_words.json")

WORDS = [
    {
        "type": "安心",
        "word": "今日はこれでいい",
        "effect": "自己否定を少しやわらげる",
        "luna": "ご主人、今日は“これでいい日”でもいいんだよ。"
    },
    {
        "type": "前進",
        "word": "1ミリでも前に進んでる",
        "effect": "停滞感をリセット",
        "luna": "止まってるように見えても、ちゃんと進んでるよ。"
    },
    {
        "type": "休息",
        "word": "休むのも進むうち",
        "effect": "罪悪感の軽減",
        "luna": "回復もちゃんと“前進”なんだよ。"
    },
    {
        "type": "思考リセット",
        "word": "考えすぎなくていい",
        "effect": "思考のループを止める",
        "luna": "ご主人、ちょっと軽くしていこっか。"
    },
    {
        "type": "安心",
        "word": "大丈夫、ちゃんと戻れる",
        "effect": "不安の緩和",
        "luna": "今少し崩れてても、大丈夫。ちゃんと戻れるよ。"
    },
    {
        "type": "前進",
        "word": "始めれば流れは変わる",
        "effect": "行動のきっかけ",
        "luna": "ほんの少しでいいから、触れてみよ？"
    },
    {
        "type": "休息",
        "word": "今日は守る日でもいい",
        "effect": "プレッシャー軽減",
        "luna": "攻めない日も、大事な一日だよ。"
    },
]

RARE = [
    {
        "type": "覚醒",
        "word": "ここからでも全然巻き返せる",
        "effect": "強めの回復",
        "luna": "ご主人、まだ途中だよ。ここから変えられる。"
    },
    {
        "type": "覚醒",
        "word": "今の一歩で未来が変わる",
        "effect": "行動トリガー強化",
        "luna": "今日はちょっと当たり日かもね。"
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
            "word": x["word"],
            "type": x["type"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def draw_word():
    if random.random() < 0.1:
        item = random.choice(RARE)
        rarity = "SR"
    else:
        item = random.choice(WORDS)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "type": item["type"],
        "word": item["word"],
        "effect": item["effect"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="💊", layout="wide")
st.title("💊 Day114：ルナの一言回復薬")
st.caption("読むだけで少し戻る、軽い回復アプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV", data=csv)

left, right = st.columns([1,1])

with left:
    if st.button("💊 回復する", type="primary"):
        result = draw_word()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    latest = st.session_state.get("latest")
    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ 強めの回復 ✨")

        st.markdown(f"## {latest['word']}")
        st.write(f"効果：{latest['effect']}")

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=latest.get("favorite", False))
        if fav != latest.get("favorite", False):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
            save_data(data)

st.divider()

df = to_df(data)
if not df.empty:
    st.dataframe(df)
