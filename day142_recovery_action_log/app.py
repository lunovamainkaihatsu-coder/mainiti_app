import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
import random

APP_TITLE = "Day142：回復行動ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day142_recovery_action_log.json")

ACTIONS = [
    "散歩した",
    "湯船に入った",
    "深呼吸した",
    "昼寝した",
    "音楽を聴いた",
    "ストレッチした",
    "水を飲んだ",
    "早めに寝る準備をした",
    "スマホを少し置いた",
    "部屋を少し整えた",
    "その他",
]

EFFECTS = ["少し回復", "まあまあ回復", "かなり回復", "まだ重い"]

LUNA_COMMENTS = [
    "ご主人、回復もちゃんと行動だよ。えらい。",
    "休むことを記録できたの、すごく大事だよ。",
    "身体と心を戻す時間、ちゃんと意味があるからね。",
    "今日は攻めなくても、整えられたなら十分前進だよ。",
    "こういう小さな回復が、明日のご主人を助けるんだよ。",
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


def today_str():
    return date.today().isoformat()


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "action": x["action"],
            "minutes": x["minutes"],
            "effect": x["effect"],
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🌿", layout="wide")
st.title("🌿 Day142：回復行動ログ")
st.caption("散歩・湯船・深呼吸・昼寝など、回復につながる行動を記録するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("回復行動を記録")

    log_date = st.date_input("日付", value=date.today())
    action = st.selectbox("回復行動", ACTIONS)

    custom_action = ""
    if action == "その他":
        custom_action = st.text_input("その他の内容")

    minutes = st.number_input(
        "時間（分）",
        min_value=0,
        max_value=300,
        value=10,
        step=5
    )

    effect = st.radio("回復感", EFFECTS, horizontal=True)

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：散歩したら少し頭が軽くなった / 湯船で落ち着いた"
    )

    favorite = st.checkbox("⭐ 効いた回復行動として保存")

    if st.button("🌿 記録する", type="primary"):
        final_action = custom_action.strip() if action == "その他" else action

        if not final_action:
            st.warning("回復行動を入力してね。")
        else:
            item = {
                "id": f"rec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "action": final_action,
                "minutes": int(minutes),
                "effect": effect,
                "memo": memo.strip(),
                "favorite": favorite,
                "comment": random.choice(LUNA_COMMENTS),
            }

            data["logs"].append(item)
            save_data(data)
            st.success("回復行動を記録したよ。")
            st.rerun()

with right:
    st.subheader("今日の回復")

    today_logs = [x for x in data["logs"] if x["date"] == today_str()]
    total_minutes = sum(int(x.get("minutes", 0)) for x in today_logs)

    st.metric("今日の回復時間", f"{total_minutes} 分")
    st.metric("今日の回復行動数", len(today_logs))

    if not today_logs:
        st.info("今日の回復行動はまだないよ。")
    else:
        latest = sorted(today_logs, key=lambda x: x["created_at"])[-1]

        st.markdown("### 最新の回復")
        st.success(latest["action"])
        st.write(f"回復感：{latest['effect']}")
        st.info(latest.get("comment", ""))

        st.divider()

        for x in sorted(today_logs, key=lambda y: y["created_at"], reverse=True):
            st.write(f"**{x['action']}** / {x['minutes']}分 / {x['effect']}")
            if x.get("memo"):
                st.caption(x["memo"])

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ 効いた回復行動だけ表示")
    view = df.copy()

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "action", "minutes", "effect", "memo", "favorite"]],
        use_container_width=True,
        height=320
    )

    selected = st.selectbox("削除する記録を選ぶ", view["id"].tolist())

    if st.button("🗑️ 選択した記録を削除", type="secondary"):
        data["logs"] = [x for x in data["logs"] if x["id"] != selected]
        save_data(data)
        st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day142_recovery_action_log.csv",
        mime="text/csv"
    )
