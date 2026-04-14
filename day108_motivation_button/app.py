import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day108：やる気復活ボタン"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day108_motivation_button.json")

MOTIVATION_POOL = [
    {
        "type": "軽め回復",
        "title": "まずはエネルギー回復",
        "message": "やる気がない時は、まずエネルギー不足の可能性あり。",
        "action": "水を飲む＋深呼吸3回",
        "luna": "ご主人、まずはちょっとだけ整えよっか。"
    },
    {
        "type": "軽め回復",
        "title": "思考リセット",
        "message": "考えすぎで止まってるかも。",
        "action": "30秒目を閉じる",
        "luna": "一回リセットするだけで、全然違うよ。"
    },
    {
        "type": "行動トリガー",
        "title": "5分だけやる",
        "message": "やる気は行動の後に出る。",
        "action": "5分だけ作業スタート",
        "luna": "最初の5分だけ、一緒にやろ？"
    },
    {
        "type": "行動トリガー",
        "title": "触れるだけでOK",
        "message": "やるじゃなくて、触るだけでいい。",
        "action": "ファイルを1つ開く",
        "luna": "ご主人、開くだけで十分すごいよ。"
    },
    {
        "type": "強制再起動",
        "title": "ゼロ回避モード",
        "message": "今日はゼロで終わらせないだけで勝ち。",
        "action": "1行だけ何かやる",
        "luna": "ご主人、1でも積めたら今日は勝ちだよ。"
    },
    {
        "type": "強制再起動",
        "title": "とりあえず立つ",
        "message": "身体を動かすとスイッチ入る。",
        "action": "立って伸びをする",
        "luna": "よし、まず立ってみよ。そこからでいい。"
    },
]

RARE_EVENT = [
    {
        "type": "覚醒",
        "title": "流れ変わる瞬間",
        "message": "今のこの一歩で、流れが変わる可能性あり。",
        "action": "いちばんやりたいことを3分やる",
        "luna": "ご主人、今ちょっとチャンス来てるかも。"
    }
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
            "type": x["type"],
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
def draw_motivation():
    if random.random() < 0.1:
        item = random.choice(RARE_EVENT)
        rarity = "SR"
    else:
        item = random.choice(MOTIVATION_POOL)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "type": item["type"],
        "title": item["title"],
        "message": item["message"],
        "action": item["action"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="⚡", layout="wide")
st.title("⚡ Day108：やる気復活ボタン")
st.caption("押すだけで、次の一歩に戻るためのアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV", data=csv)

left, right = st.columns([1,1])

with left:
    if st.button("⚡ やる気復活", type="primary"):
        result = draw_motivation()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    latest = st.session_state.get("latest")
    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ 覚醒イベント ✨")

        st.markdown(f"## {latest['title']}")
        st.write(latest["message"])

        st.markdown("### 行動")
        st.success(latest["action"])

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
