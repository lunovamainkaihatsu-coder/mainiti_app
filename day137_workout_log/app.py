import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day137：筋トレ記録ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day137_workout_log.json")

WORKOUT_TYPES = [
    "筋トレ",
    "散歩",
    "ジョギング",
    "ストレッチ",
    "なわとび",
    "休養",
    "その他",
]

PARTS = [
    "全身",
    "胸",
    "背中",
    "腕",
    "肩",
    "腹筋",
    "脚",
    "体幹",
    "有酸素",
    "回復",
]

INTENSITY = ["軽め", "普通", "きつめ", "限界近い"]


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
            "workout_type": x["workout_type"],
            "part": x["part"],
            "menu": x["menu"],
            "sets": x["sets"],
            "reps": x["reps"],
            "minutes": x["minutes"],
            "intensity": x["intensity"],
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def calc_points(log):
    points = 0
    points += int(log.get("minutes", 0)) * 2
    points += int(log.get("sets", 0)) * 5
    points += int(log.get("reps", 0)) // 2

    if log.get("intensity") == "普通":
        points += 10
    elif log.get("intensity") == "きつめ":
        points += 20
    elif log.get("intensity") == "限界近い":
        points += 30
    elif log.get("intensity") == "軽め":
        points += 5

    if log.get("workout_type") == "休養":
        points = 10

    return points


st.set_page_config(page_title=APP_TITLE, page_icon="💪", layout="wide")
st.title("💪 Day137：筋トレ記録ログ")
st.caption("筋トレ・散歩・有酸素・休養を記録して、体づくりを見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("運動を記録する")

    workout_date = st.date_input("日付", value=date.today())
    workout_type = st.selectbox("種類", WORKOUT_TYPES)
    part = st.selectbox("部位", PARTS)

    menu = st.text_input(
        "メニュー",
        placeholder="例：スクワット、腕立て、散歩、ジョギング"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        sets = st.number_input("セット数", min_value=0, max_value=50, value=0)
    with col2:
        reps = st.number_input("回数", min_value=0, max_value=1000, value=0)
    with col3:
        minutes = st.number_input("時間（分）", min_value=0, max_value=300, value=10)

    intensity = st.radio("強度", INTENSITY, horizontal=True)

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：脚がきつかった / 軽めにした / 娘と歩いた"
    )

    favorite = st.checkbox("⭐ 良い運動として保存")

    preview = {
        "minutes": minutes,
        "sets": sets,
        "reps": reps,
        "intensity": intensity,
        "workout_type": workout_type,
    }
    points = calc_points(preview)
    st.metric("今回の運動ポイント", points)

    if st.button("💪 記録する", type="primary"):
        if not menu.strip() and workout_type != "休養":
            st.warning("メニューを入れてね。")
        else:
            item = {
                "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": workout_date.isoformat(),
                "workout_type": workout_type,
                "part": part,
                "menu": menu.strip() if menu.strip() else workout_type,
                "sets": int(sets),
                "reps": int(reps),
                "minutes": int(minutes),
                "intensity": intensity,
                "points": points,
                "memo": memo.strip(),
                "favorite": favorite,
            }
            data["logs"].append(item)
            save_data(data)
            st.success("運動を記録したよ。")
            st.rerun()

with right:
    st.subheader("今日の運動")

    today_logs = [x for x in data["logs"] if x["date"] == today_str()]
    today_points = sum(int(x.get("points", 0)) for x in today_logs)
    today_minutes = sum(int(x.get("minutes", 0)) for x in today_logs)

    st.metric("今日の運動ポイント", today_points)
    st.metric("今日の運動時間", f"{today_minutes} 分")

    if not today_logs:
        st.info("今日の記録はまだないよ。")
    else:
        for x in sorted(today_logs, key=lambda y: y["created_at"]):
            st.markdown(f"### {x['workout_type']}｜{x['menu']}")
            st.write(f"部位：{x['part']} / 強度：{x['intensity']}")
            st.write(f"{x['sets']}セット / {x['reps']}回 / {x['minutes']}分")
            st.caption(f"ポイント：{x.get('points', 0)}")
            if x.get("memo"):
                st.caption(x["memo"])
            st.divider()

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ運動ログがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        filter_date = st.date_input("日付で絞る", value=date.today())
    with col_b:
        filter_type = st.selectbox("種類で絞る", ["すべて"] + WORKOUT_TYPES)
    with col_c:
        fav_only = st.checkbox("⭐ 良い運動だけ")

    view = df.copy()

    if filter_date:
        view = view[view["date"] == filter_date.isoformat()]

    if filter_type != "すべて":
        view = view[view["workout_type"] == filter_type]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "workout_type", "part", "menu", "sets", "reps", "minutes", "intensity", "favorite"]],
        use_container_width=True,
        height=320
    )

    if not view.empty:
        with st.expander("詳細・削除"):
            selected = st.selectbox("記録を選ぶ", view["id"].tolist())
            item = next((x for x in data["logs"] if x["id"] == selected), None)

            if item:
                st.markdown(f"### {item['date']} / {item['workout_type']}")
                st.write(f"メニュー：{item['menu']}")
                st.write(f"部位：{item['part']}")
                st.write(f"セット：{item['sets']} / 回数：{item['reps']} / 分：{item['minutes']}")
                st.write(f"強度：{item['intensity']}")
                st.write(f"ポイント：{item.get('points', 0)}")
                if item.get("memo"):
                    st.write(f"メモ：{item['memo']}")

                fav = st.checkbox("⭐ 良い運動", value=bool(item.get("favorite", False)))
                if fav != bool(item.get("favorite", False)):
                    item["favorite"] = fav
                    save_data(data)
                    st.rerun()

                if st.button("🗑️ この記録を削除", type="secondary"):
                    data["logs"] = [x for x in data["logs"] if x["id"] != selected]
                    save_data(data)
                    st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day137_workout_log.csv",
        mime="text/csv"
    )
