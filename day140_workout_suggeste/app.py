import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day140：筋トレ提案アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day140_workout_suggester.json")

CONDITIONS = [
    "疲れてる",
    "普通",
    "元気",
    "本気出したい"
]

GOALS = [
    "ダイエット",
    "筋力UP",
    "健康維持",
    "ストレス発散",
    "テストステロン意識"
]

LEVELS = [
    "軽め",
    "普通",
    "本気"
]

WORKOUTS = {
    "疲れてる": {
        "軽め": [
            ["深呼吸 3回", "ストレッチ 3分", "散歩 5分"],
            ["スクワット 10回", "ストレッチ 5分"],
        ],
        "普通": [
            ["スクワット 15回", "膝つき腕立て 10回", "プランク 20秒"],
        ],
        "本気": [
            ["スクワット 20回", "腕立て 10回", "プランク 30秒"],
        ],
    },

    "普通": {
        "軽め": [
            ["スクワット 20回", "ストレッチ 5分"],
        ],
        "普通": [
            ["スクワット 30回", "腕立て 15回", "プランク 45秒"],
            ["スクワット 20回 ×2", "腕立て 10回 ×2"],
        ],
        "本気": [
            ["スクワット 50回", "腕立て 20回", "プランク 60秒"],
        ],
    },

    "元気": {
        "軽め": [
            ["散歩 20分", "スクワット 20回"],
        ],
        "普通": [
            ["スクワット 40回", "腕立て 20回", "腹筋 20回"],
        ],
        "本気": [
            ["スクワット 50回 ×3", "腕立て 20回 ×3", "プランク 60秒 ×3"],
        ],
    },

    "本気出したい": {
        "軽め": [
            ["スクワット 30回", "腕立て 15回"],
        ],
        "普通": [
            ["スクワット 50回", "腕立て 20回", "腹筋 30回"],
        ],
        "本気": [
            ["スクワット 50回 ×3", "腕立て 20回 ×3", "腹筋 30回 ×3"],
        ],
    },
}

LUNA_COMMENTS = {
    "疲れてる": [
        "今日は軽めでも十分えらいよ。",
        "ゼロじゃなければ勝ちだよ、ご主人。",
    ],

    "普通": [
        "今日はいい感じ。少し積んでいこう。",
        "普通の日に動けるのって強いよ。",
    ],

    "元気": [
        "今日は身体を動かすと気持ちよさそう！",
        "少し攻めても良さそうだね。",
    ],

    "本気出したい": [
        "今日は燃えてるね、ご主人！",
        "攻める日だ。でもフォームは丁寧にね。",
    ],
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


def generate_plan(condition, level):
    return random.choice(WORKOUTS[condition][level])


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "date": x["date"],
            "condition": x["condition"],
            "goal": x["goal"],
            "level": x["level"],
            "menu": " / ".join(x["menu"]),
            "done": x["done"],
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("date", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💪",
    layout="wide"
)

st.title("💪 Day140：筋トレ提案アプリ")
st.caption("今日の状態に合わせて筋トレを提案するアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1,1], gap="large")

# ----------------------------
# 入力
# ----------------------------
with left:

    st.subheader("今日の状態")

    condition = st.radio(
        "コンディション",
        CONDITIONS,
        horizontal=True
    )

    goal = st.selectbox(
        "目的",
        GOALS
    )

    level = st.radio(
        "強度",
        LEVELS,
        horizontal=True
    )

    if st.button("💪 メニュー提案", type="primary"):

        menu = generate_plan(condition, level)

        item = {
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "condition": condition,
            "goal": goal,
            "level": level,
            "menu": menu,
            "done": False,
            "memo": "",
            "favorite": False,
            "comment": random.choice(LUNA_COMMENTS[condition]),
        }

        data["logs"].append(item)

        save_data(data)

        st.session_state["latest"] = item

        st.rerun()

# ----------------------------
# 表示
# ----------------------------
with right:

    st.subheader("今日のメニュー")

    latest = st.session_state.get("latest")

    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:

        st.markdown(
            f"## {latest['condition']} × {latest['level']}"
        )

        st.markdown("### メニュー")

        for i, m in enumerate(latest["menu"], start=1):
            st.success(f"{i}. {m}")

        st.markdown("### ルナコメント")
        st.info(latest["comment"])

        done = st.checkbox(
            "✅ 実行した",
            value=bool(latest.get("done", False))
        )

        favorite = st.checkbox(
            "⭐ お気に入り",
            value=bool(latest.get("favorite", False))
        )

        memo = st.text_area(
            "メモ",
            value=latest.get("memo", "")
        )

        if st.button("📝 保存"):

            latest["done"] = done
            latest["favorite"] = favorite
            latest["memo"] = memo

            for x in data["logs"]:
                if x["id"] == latest["id"]:
                    x.update(latest)

            save_data(data)

            st.success("保存したよ！")
            st.rerun()

    else:
        st.info("まだ提案がないよ。")

st.divider()

# ----------------------------
# 履歴
# ----------------------------
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ")

else:

    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day140_workout_suggester.csv",
        mime="text/csv"
    )
