import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day177：筋トレ記録帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day177_workout_log.json")

EXERCISES = [
    "懸垂",
    "腕立て",
    "スクワット",
    "腹筋",
    "ヒップリフト",
    "縄跳び",
    "ランニング",
    "プランク",
    "ストレッチ",
    "その他",
]

INTENSITIES = [
    "軽め",
    "普通",
    "きつい",
    "限界",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def current_week_key(d):
    dt = datetime.strptime(d, "%Y-%m-%d").date()
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def calc_volume(reps, sets):
    return int(reps) * int(sets)


def to_df(data):
    rows = []

    for x in data["logs"]:
        volume = calc_volume(
            x.get("reps", 0),
            x.get("sets", 0)
        )

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "week": current_week_key(x["date"]),
            "exercise": x["exercise"],
            "reps": int(x.get("reps", 0)),
            "sets": int(x.get("sets", 0)),
            "volume": volume,
            "minutes": int(x.get("minutes", 0)),
            "intensity": x.get("intensity", "普通"),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_log(data, log_id):
    for x in data["logs"]:
        if x["id"] == log_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💪",
    layout="wide"
)

st.title("💪 Day177：筋トレ記録帳")
st.caption("種目・回数・セット数・時間を記録して、筋トレの積み上げを見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の筋トレを記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    exercise = st.selectbox(
        "種目",
        EXERCISES
    )

    c1, c2 = st.columns(2)

    with c1:
        reps = st.number_input(
            "回数",
            min_value=0,
            value=10,
            step=1
        )

    with c2:
        sets = st.number_input(
            "セット数",
            min_value=0,
            value=3,
            step=1
        )

    minutes = st.number_input(
        "時間（分）",
        min_value=0,
        value=0,
        step=1
    )

    intensity = st.selectbox(
        "強度",
        INTENSITIES,
        index=1
    )

    volume = calc_volume(reps, sets)

    st.info(f"合計回数：{volume} 回")

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：懸垂がきつかった / 今日は軽め / フォーム意識"
    )

    if st.button("💪 記録する", type="primary"):
        if reps == 0 and minutes == 0:
            st.warning("回数か時間を入力してね。")
        else:
            item = {
                "id": f"workout_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "exercise": exercise,
                "reps": int(reps),
                "sets": int(sets),
                "minutes": int(minutes),
                "intensity": intensity,
                "memo": memo.strip(),
            }

            data["logs"].append(item)
            save_data(data)

            st.success("筋トレを記録したよ。")
            st.rerun()

with right:
    st.subheader("今日・今週の積み上げ")

    df = to_df(data)

    if df.empty:
        st.info("まだ筋トレ記録がないよ。")
    else:
        today = today_str()
        week = current_week_key(today)

        today_df = df[df["date"] == today]
        week_df = df[df["week"] == week]

        today_volume = int(today_df["volume"].sum()) if not today_df.empty else 0
        week_volume = int(week_df["volume"].sum()) if not week_df.empty else 0
        total_volume = int(df["volume"].sum())

        today_minutes = int(today_df["minutes"].sum()) if not today_df.empty else 0
        week_minutes = int(week_df["minutes"].sum()) if not week_df.empty else 0

        c1, c2 = st.columns(2)

        with c1:
            st.metric("今日の合計回数", f"{today_volume:,} 回")
            st.metric("今週の合計回数", f"{week_volume:,} 回")

        with c2:
            st.metric("今日の時間", f"{today_minutes} 分")
            st.metric("今週の時間", f"{week_minutes} 分")

        st.metric("累計回数", f"{total_volume:,} 回")

        st.divider()

        if not week_df.empty:
            st.subheader("今週の種目別")
            ex_sum = week_df.groupby("exercise")["volume"].sum().reset_index()
            ex_sum = ex_sum.sort_values("volume", ascending=False)

            st.dataframe(
                ex_sum,
                use_container_width=True,
                height=220
            )

st.divider()
st.subheader("筋トレ履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        exercise_filter = st.selectbox(
            "種目で絞る",
            ["すべて"] + EXERCISES
        )

    with col_b:
        intensity_filter = st.selectbox(
            "強度で絞る",
            ["すべて"] + INTENSITIES
        )

    with col_c:
        week_filter = st.text_input(
            "週で絞る",
            value="",
            placeholder="例：2026-W25"
        )

    view = df.copy()

    if exercise_filter != "すべて":
        view = view[view["exercise"] == exercise_filter]

    if intensity_filter != "すべて":
        view = view[view["intensity"] == intensity_filter]

    if week_filter.strip():
        view = view[view["week"] == week_filter.strip()]

    st.dataframe(
        view[[
            "date",
            "exercise",
            "reps",
            "sets",
            "volume",
            "minutes",
            "intensity",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("種目別グラフ")

    if not view.empty:
        graph_df = view.sort_values("date", ascending=True)

        selected_graph_exercise = st.selectbox(
            "グラフ表示する種目",
            ["全体"] + EXERCISES
        )

        if selected_graph_exercise != "全体":
            graph_df = graph_df[graph_df["exercise"] == selected_graph_exercise]

        if graph_df.empty:
            st.write("グラフ表示できるデータがないよ。")
        else:
            daily = graph_df.groupby("date")["volume"].sum().reset_index()
            daily = daily.set_index("date")

            st.line_chart(daily[["volume"]])

    st.divider()
    st.subheader("詳細・削除")

    if view.empty:
        st.write("条件に合う記録がないよ。")
    else:
        selected_id = st.selectbox(
            "記録を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_log(data, x)['date']} / {find_log(data, x)['exercise']}"
        )

        selected = find_log(data, selected_id)

        if selected:
            st.markdown(f"## {selected['exercise']}")
            st.write(f"日付：{selected['date']}")
            st.write(f"回数：{selected.get('reps', 0)}")
            st.write(f"セット数：{selected.get('sets', 0)}")
            st.write(f"時間：{selected.get('minutes', 0)} 分")
            st.write(f"強度：{selected.get('intensity', '')}")

            if selected.get("memo"):
                st.info(selected["memo"])

            if st.button("🗑️ この記録を削除", type="secondary"):
                data["logs"] = [
                    x for x in data["logs"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day177_workout_log.csv",
        mime="text/csv"
    )
