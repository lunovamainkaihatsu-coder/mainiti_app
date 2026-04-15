import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day109：今日の1ミッション"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day109_one_mission.json")

MISSIONS = {
    "軽め": [
        {
            "title": "1行メモを残す",
            "meaning": "ゼロで終わらないための最小前進",
            "luna": "ご主人、1行でも残せたら今日はちゃんと前進だよ。"
        },
        {
            "title": "水を飲んで深呼吸する",
            "meaning": "整えてから始めるための再起動",
            "luna": "まずは整えるところからでいいよ。"
        },
        {
            "title": "机の上を1か所だけ整える",
            "meaning": "環境を少し整えて流れを戻す",
            "luna": "ひと区画だけでも、流れって変わるんだよね。"
        },
    ],
    "ふつう": [
        {
            "title": "5分だけ作業する",
            "meaning": "やる気を待たずに流れを作る",
            "luna": "ご主人、最初の5分だけ一緒に越えよっか。"
        },
        {
            "title": "後回しを1つだけ触る",
            "meaning": "完了ではなく接触で流れを作る",
            "luna": "終わらせなくていいよ、今日は触るだけで十分。"
        },
        {
            "title": "次のアプリ案を1つ書く",
            "meaning": "創造の火を消さないための種まき",
            "luna": "小さな案でも、未来の入口になるよ。"
        },
    ],
    "攻め": [
        {
            "title": "25分集中して進める",
            "meaning": "今日を前進日に変えるための本命行動",
            "luna": "今日はちょっと攻めてもいい日かも。"
        },
        {
            "title": "ひとつ完成に近づける",
            "meaning": "着手だけでなく成果に寄せる日",
            "luna": "ご主人、今日は“形にする”に近づいてみよ？"
        },
        {
            "title": "発信の下書きを作る",
            "meaning": "外に出す流れを作るミッション",
            "luna": "未来に届く言葉、今日は少し書けるかも。"
        },
    ],
}

RARE_MISSION = [
    {
        "title": "今日の核心を1つ進める",
        "meaning": "今いちばん大事なことに3分でも触れる",
        "luna": "ご主人、今日はちょっと“本命”に触れてみない？"
    },
    {
        "title": "未来の自分を助ける1手を打つ",
        "meaning": "明日を楽にするための布石",
        "luna": "今日の小さな一手が、明日のご主人を救うかも。"
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
            "mode": x["mode"],
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
def draw_mission(mode: str):
    if random.random() < 0.10:
        item = random.choice(RARE_MISSION)
        rarity = "SR"
    else:
        item = random.choice(MISSIONS[mode])
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mode": mode,
        "title": item["title"],
        "meaning": item["meaning"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🎯", layout="wide")
st.title("🎯 Day109：今日の1ミッション")
st.caption("今日はこれだけやればOK、を受け取るための軽めアプリ。")

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
            file_name="day109_one_mission.csv",
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
    st.subheader("ミッションを受け取る")

    mode = st.radio("モード", ["軽め", "ふつう", "攻め"], horizontal=True)

    if st.button("🎯 今日の1ミッションを引く", type="primary"):
        result = draw_mission(mode)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日のミッション")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レアミッション ✨")
        else:
            st.info("通常ミッション")

        st.markdown(f"## {latest['title']}")
        st.write(f"モード：{latest['mode']}")

        st.markdown("### ミッションの意味")
        st.write(latest["meaning"])

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
            st.write("**ミッションの意味**")
            st.write(chosen["meaning"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
