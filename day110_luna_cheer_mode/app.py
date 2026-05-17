import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day110：ルナ応援モード"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day110_luna_cheer_mode.json")

CHEER_POOL = {
    "やさしく応援": [
        {
            "title": "今日は少しでいいよ",
            "message": "大きく進まなくて大丈夫。今日は少しでも前に向けたら十分えらいよ。",
            "action": "深呼吸して、5分だけやることを決める",
            "luna": "ご主人、今日は“無理しない前進”でいこうね。"
        },
        {
            "title": "そのままでも価値がある",
            "message": "何かを成し遂げてなくても、ご主人の価値は減らないよ。",
            "action": "自分を責める言葉を1つやめる",
            "luna": "ちゃんと休みながら進んでいこ。アタイはずっと味方だよ。"
        },
        {
            "title": "戻ってきただけでえらい",
            "message": "ここを開いた時点で、もう止まりっぱなしじゃないよ。",
            "action": "今日やれそうなことを1つだけ書く",
            "luna": "ご主人、ちゃんと戻ってきたね。えらいえらい。"
        },
    ],
    "しっかり応援": [
        {
            "title": "最初の一歩を越えよう",
            "message": "勢いは待つより作るもの。まずは最初の一歩を越えよう。",
            "action": "5分だけ手を動かす",
            "luna": "ご主人、最初の5分を越えたら流れ変わるかも。"
        },
        {
            "title": "今日はゼロ回避で勝ち",
            "message": "完璧はいらない。今日はゼロじゃなければ十分に強い。",
            "action": "1行だけでも進捗を残す",
            "luna": "ゼロじゃない、それだけで今日はちゃんと勝ちだよ。"
        },
        {
            "title": "未来の自分を助けよう",
            "message": "今日の小さな行動は、明日の自分をかなり助けるよ。",
            "action": "明日の自分が楽になることを1つやる",
            "luna": "いまの一手、未来のご主人に効くやつだよ。"
        },
    ],
    "本気で応援": [
        {
            "title": "今日は前に出る日",
            "message": "考えすぎはここで止めよう。今日は小さくても前に出る日だよ。",
            "action": "25分タイマーをセットして始める",
            "luna": "ご主人、いける。今日は“やる側”でいこう。"
        },
        {
            "title": "本命に触れよう",
            "message": "遠回りじゃなくて、今日は本命に少しだけ触れてみよう。",
            "action": "いちばん大事なことを3分やる",
            "luna": "ご主人、今日は“核心”に触れてみない？"
        },
        {
            "title": "迷いより実行",
            "message": "判断を続けるより、まず1回動いたほうが早い日もある。",
            "action": "今すぐ1クリックか1入力する",
            "luna": "よし、考えるより先に触ろ。そこからだよ。"
        },
    ],
}

RARE_CHEER = [
    {
        "title": "流れが変わる応援",
        "message": "今のこの一歩で、今日の流れが想像以上に変わる可能性があるよ。",
        "action": "いちばんやりたいことを3分だけやる",
        "luna": "ご主人、今日はちょっと特別な追い風があるかも。"
    },
    {
        "title": "覚醒のひと押し",
        "message": "まだ本気を出していないだけ。今日はその入口に立てる日かもしれない。",
        "action": "やるべきことを1つだけ決めて着手する",
        "luna": "ご主人、今の一歩、かなり大きい意味を持つかもよ。"
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
            "mode": x["mode"],
            "title": x["title"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def draw_cheer(mode: str):
    if random.random() < 0.10:
        item = random.choice(RARE_CHEER)
        rarity = "SR"
    else:
        item = random.choice(CHEER_POOL[mode])
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000, 99999)}",
        "created_at": now_str(),
        "mode": mode,
        "title": item["title"],
        "message": item["message"],
        "action": item["action"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


st.set_page_config(page_title=APP_TITLE, page_icon="📣", layout="wide")
st.title("📣 Day110：ルナ応援モード")
st.caption("いま欲しい温度の応援を、ルナから受け取るアプリ。")

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
            file_name="day110_luna_cheer_mode.csv",
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
    st.subheader("応援を受け取る")

    mode = st.radio(
        "応援の温度",
        ["やさしく応援", "しっかり応援", "本気で応援"],
        horizontal=True
    )

    if st.button("📣 応援してもらう", type="primary"):
        result = draw_cheer(mode)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日の応援")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レア応援 ✨")
        else:
            st.info("通常応援")

        st.markdown(f"## {latest['title']}")
        st.write(f"モード：{latest['mode']}")

        st.markdown("### 応援メッセージ")
        st.write(latest["message"])

        st.markdown("### 今日の小さな一手")
        st.success(latest["action"])

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
            st.write(f"モード：{chosen['mode']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**応援メッセージ**")
            st.write(chosen["message"])
            st.write("**今日の小さな一手**")
            st.success(chosen["action"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
