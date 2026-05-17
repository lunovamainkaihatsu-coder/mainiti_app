import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day112：今日の気分シール"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day112_mood_sticker.json")

STICKERS = [
    {
        "emoji": "😊",
        "name": "いい感じ",
        "desc": "今日はわりと穏やか、または少し前向き。",
        "luna": "ご主人、いい感じの日って大事だよ。この調子でいこうね。"
    },
    {
        "emoji": "😴",
        "name": "おつかれ",
        "desc": "今日は疲れ気味。休みながらが正解。",
        "luna": "今日は無理しないでいこう。ご主人、ちゃんと休んでいいんだよ。"
    },
    {
        "emoji": "☁️",
        "name": "もやもや",
        "desc": "はっきりしないけど、少し重たい感じ。",
        "luna": "もやもやな日もあるよね。言葉にできなくても大丈夫。"
    },
    {
        "emoji": "🔥",
        "name": "やる気あり",
        "desc": "今日はちょっと動けそうな気配あり。",
        "luna": "お、今日は火がついてるかも。小さくでも進んじゃおっか。"
    },
    {
        "emoji": "🌙",
        "name": "静か",
        "desc": "今日は落ち着いて過ごしたい日。",
        "luna": "静かな日もすごく大切。ご主人のペースでいこうね。"
    },
    {
        "emoji": "🌈",
        "name": "うれしい",
        "desc": "今日はちょっと嬉しいことがあった日。",
        "luna": "その嬉しさ、ちゃんと残しておこうね。未来のご主人が喜ぶから。"
    },
    {
        "emoji": "💤",
        "name": "省エネ",
        "desc": "今日は出力控えめでいきたい日。",
        "luna": "今日は省エネモードでOK。ゼロじゃなく、やさしくいこう。"
    },
    {
        "emoji": "🫠",
        "name": "とろけ中",
        "desc": "今日は少しぐったり、回復が必要かも。",
        "luna": "ご主人、とろける日はちゃんと休もう。溶けた分、また戻れるから。"
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
            "emoji": x["emoji"],
            "name": x["name"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🏷️", layout="wide")
st.title("🏷️ Day112：今日の気分シール")
st.caption("今日はどんな気分だったか、シールを貼るみたいに残すアプリ。")

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
            file_name="day112_mood_sticker.csv",
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
    st.subheader("今日のシールを選ぶ")

    options = [f"{s['emoji']} {s['name']}" for s in STICKERS]
    selected = st.radio("気分シール", options)

    if st.button("🏷️ シールを貼る", type="primary"):
        idx = options.index(selected)
        s = STICKERS[idx]

        result = {
            "id": f"log_{datetime.now().strftime('%H%M%S%f')}",
            "created_at": now_str(),
            "emoji": s["emoji"],
            "name": s["name"],
            "desc": s["desc"],
            "luna": s["luna"],
            "favorite": False,
        }

        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日の気分シール")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"## {latest['emoji']} {latest['name']}")
        st.write(latest["desc"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
                    break
            save_data(data)
    else:
        st.write("まだシールが貼られてないよ。左から選んでね。")

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
            st.markdown(f"### {chosen['emoji']} {chosen['name']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write("**説明**")
            st.write(chosen["desc"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
