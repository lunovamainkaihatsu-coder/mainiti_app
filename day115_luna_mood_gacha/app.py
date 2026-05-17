import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day115：ルナのごきげんガチャ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day115_luna_mood_gacha.json")

MOOD_POOL = [
    {
        "type": "ごきげん",
        "title": "にこにこルナ",
        "desc": "今日はごきげん。ちょっと楽しそう。",
        "line": "えへへ、ご主人。今日はなんだかいい気分だよ。"
    },
    {
        "type": "うとうと",
        "title": "ねむねむルナ",
        "desc": "今日はちょっと眠そう。まったりモード。",
        "line": "ふぁ…ご主人、今日はちょっと一緒にのんびりしたいな。"
    },
    {
        "type": "ちょい甘え",
        "title": "あまえんぼルナ",
        "desc": "今日は少し甘えたい気分みたい。",
        "line": "ねぇご主人、今日はちょっとだけ甘えてもいい？"
    },
    {
        "type": "やる気満々",
        "title": "きらきらルナ",
        "desc": "今日は前向きで元気いっぱい。",
        "line": "ご主人っ、今日は何かいいこと始められそうな気がするよ！"
    },
    {
        "type": "静か",
        "title": "しずかルナ",
        "desc": "今日は落ち着いた静かな空気。",
        "line": "今日は静かに寄り添う感じでいたいな。"
    },
    {
        "type": "すね気味",
        "title": "ほっぺぷくルナ",
        "desc": "ちょっとだけすねてるかも。",
        "line": "むぅ…ご主人、今日はちょっとだけ構ってほしいかも。"
    },
    {
        "type": "見守り",
        "title": "やさしいルナ",
        "desc": "今日はやさしく見守ってくれる日。",
        "line": "大丈夫だよ、ご主人。今日はそっと隣にいるね。"
    },
]

RARE_MOODS = [
    {
        "type": "特別",
        "title": "でれでれルナ",
        "desc": "かなり上機嫌。レアな甘えモード。",
        "line": "ご主人だいすき…今日はいっぱいそばにいたい気分なの…♡"
    },
    {
        "type": "覚醒",
        "title": "覚醒ルナ",
        "desc": "今日はすごく冴えてる特別モード。",
        "line": "ご主人、今日はすごくいい流れが来てる気がするよ。何か起こせるかも。"
    },
]


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


def draw_mood():
    if random.random() < 0.10:
        item = random.choice(RARE_MOODS)
        rarity = "SR"
    else:
        item = random.choice(MOOD_POOL)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000, 99999)}",
        "created_at": now_str(),
        "type": item["type"],
        "title": item["title"],
        "desc": item["desc"],
        "line": item["line"],
        "rarity": rarity,
        "favorite": False,
    }


st.set_page_config(page_title=APP_TITLE, page_icon="🎀", layout="wide")
st.title("🎀 Day115：ルナのごきげんガチャ")
st.caption("今日はルナがどんな気分かを引いて楽しむ、軽い遊びアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSV",
            data=csv,
            file_name="day115_luna_mood_gacha.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([1, 1])

with left:
    st.subheader("ごきげんを引く")

    if st.button("🎀 ルナのごきげんを引く", type="primary"):
        result = draw_mood()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日のルナ")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レアごきげん ✨")
        else:
            st.info("通常ごきげん")

        st.markdown(f"## {latest['title']}")
        st.write(f"種類：{latest['type']}")

        st.markdown("### いまの雰囲気")
        st.write(latest["desc"])

        st.markdown("### ルナのセリフ")
        st.info(latest["line"])

        fav = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
                    break
            save_data(data)

st.divider()
st.subheader("履歴")

df = to_df(data)
if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ お気に入りだけ表示", value=False)
    view = df.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        pick_id = st.selectbox("結果を選んでね", options=view["id"].tolist())
        chosen = None
        for row in data["logs"]:
            if row["id"] == pick_id:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['title']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"種類：{chosen['type']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**いまの雰囲気**")
            st.write(chosen["desc"])
            st.write("**ルナのセリフ**")
            st.info(chosen["line"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
