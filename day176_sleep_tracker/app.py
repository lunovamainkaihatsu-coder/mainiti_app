import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, time, timedelta

APP_TITLE = "Day176：睡眠記録帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day176_sleep_tracker.json")

QUALITY_OPTIONS = [
    "😫 最悪",
    "😕 悪い",
    "😐 普通",
    "🙂 良い",
    "😴 最高",
]

WAKE_OPTIONS = [
    "0回",
    "1回",
    "2回",
    "3回以上",
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


def quality_score(label):
    return {
        "😫 最悪": 1,
        "😕 悪い": 2,
        "😐 普通": 3,
        "🙂 良い": 4,
        "😴 最高": 5,
    }.get(label, 3)


def calc_sleep_hours(bed_date, bed_time, wake_date, wake_time):
    start = datetime.combine(bed_date, bed_time)
    end = datetime.combine(wake_date, wake_time)

    if end <= start:
        end += timedelta(days=1)

    diff = end - start
    return round(diff.total_seconds() / 3600, 2)


def sleep_rank(hours, quality, wake_count):
    q = quality_score(quality)

    wake_penalty = {
        "0回": 0,
        "1回": 0,
        "2回": 1,
        "3回以上": 2,
    }.get(wake_count, 0)

    score = 0

    if hours >= 8:
        score += 45
    elif hours >= 7:
        score += 40
    elif hours >= 6:
        score += 30
    elif hours >= 5:
        score += 20
    else:
        score += 10

    score += q * 12
    score -= wake_penalty * 10

    score = max(0, min(100, score))

    if score >= 90:
        return "S", score, "かなり良い睡眠！回復できてる可能性が高いよ。"

    if score >= 75:
        return "A", score, "いい睡眠。今日は動きやすそう。"

    if score >= 60:
        return "B", score, "悪くないけど、少し改善できそう。"

    if score >= 45:
        return "C", score, "睡眠がやや不足気味かも。無理しすぎ注意。"

    return "D", score, "今日は回復優先でいこう。"


def advice_text(hours, quality, wake_count):
    advice = []

    if hours < 6:
        advice.append("睡眠時間が短め。今日はカフェインや無理な追い込みを控えめに。")
    elif hours < 7:
        advice.append("あと30分〜1時間眠れるとさらに良さそう。")
    else:
        advice.append("睡眠時間はいい感じ。続けていこう。")

    if quality_score(quality) <= 2:
        advice.append("睡眠の質が低め。寝る前のスマホ・食事・照明を少し見直すと良さそう。")

    if wake_count in ["2回", "3回以上"]:
        advice.append("途中覚醒が多め。寝る前の水分量や室温もチェックしてみよう。")

    if not advice:
        advice.append("かなり整ってるよ。今日もいい流れでいこう。")

    return advice


def hours_text(hours):
    h = int(hours)
    m = int(round((hours - h) * 60))
    return f"{h}時間{m}分"


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "bed_date": x["bed_date"],
            "bed_time": x["bed_time"],
            "wake_date": x["wake_date"],
            "wake_time": x["wake_time"],
            "sleep_hours": float(x.get("sleep_hours", 0)),
            "quality": x["quality"],
            "quality_score": int(x.get("quality_score", 3)),
            "wake_count": x["wake_count"],
            "rank": x["rank"],
            "score": int(x.get("score", 0)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("date", ascending=True)

    return df


def find_log(data, log_id):
    for x in data["logs"]:
        if x["id"] == log_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="😴",
    layout="wide"
)

st.title("😴 Day176：睡眠記録帳")
st.caption("就寝・起床時間、睡眠時間、睡眠の質を記録して見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("睡眠を記録")

    sleep_date = st.date_input(
        "記録日",
        value=date.today()
    )

    bed_date = st.date_input(
        "就寝日",
        value=date.today()
    )

    bed_time = st.time_input(
        "就寝時間",
        value=time(23, 30)
    )

    wake_date = st.date_input(
        "起床日",
        value=date.today() + timedelta(days=1)
    )

    wake_time = st.time_input(
        "起床時間",
        value=time(6, 30)
    )

    quality = st.selectbox(
        "睡眠の質",
        QUALITY_OPTIONS,
        index=3
    )

    wake_count = st.selectbox(
        "途中覚醒",
        WAKE_OPTIONS
    )

    sleep_hours = calc_sleep_hours(
        bed_date,
        bed_time,
        wake_date,
        wake_time
    )

    rank, score, comment = sleep_rank(
        sleep_hours,
        quality,
        wake_count
    )

    st.info(f"睡眠時間：{hours_text(sleep_hours)} / ランク：{rank} / {score}点")

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：暑くて起きた / 夢を見た / 早く寝られた"
    )

    if st.button("😴 記録する", type="primary"):
        item = {
            "id": f"sleep_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": sleep_date.isoformat(),
            "bed_date": bed_date.isoformat(),
            "bed_time": bed_time.strftime("%H:%M"),
            "wake_date": wake_date.isoformat(),
            "wake_time": wake_time.strftime("%H:%M"),
            "sleep_hours": float(sleep_hours),
            "quality": quality,
            "quality_score": quality_score(quality),
            "wake_count": wake_count,
            "rank": rank,
            "score": score,
            "comment": comment,
            "advice": advice_text(sleep_hours, quality, wake_count),
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)

        st.success("睡眠記録を保存したよ。")
        st.rerun()

with right:
    st.subheader("最新の睡眠評価")

    df = to_df(data)

    if df.empty:
        st.info("まだ記録がないよ。")
    else:
        latest = df.iloc[-1]

        st.metric("睡眠時間", hours_text(float(latest["sleep_hours"])))
        st.metric("睡眠ランク", latest["rank"])
        st.metric("睡眠スコア", f"{int(latest['score'])}点")

        st.progress(min(int(latest["score"]) / 100, 1.0))

        selected = find_log(data, latest["id"])

        if selected:
            st.success(selected.get("comment", ""))

            st.divider()

            st.subheader("アドバイス")

            for adv in selected.get("advice", []):
                st.info(adv)

st.divider()
st.subheader("睡眠グラフ")

df = to_df(data)

if df.empty:
    st.write("まだグラフ表示できる記録がないよ。")
else:
    chart_df = df.set_index("date")

    st.write("睡眠時間推移")
    st.line_chart(chart_df[["sleep_hours"]])

    st.write("睡眠の質推移")
    st.line_chart(chart_df[["quality_score"]])

    st.write("睡眠スコア推移")
    st.line_chart(chart_df[["score"]])

st.divider()
st.subheader("睡眠履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("記録数", len(df))

    with c2:
        st.metric("平均睡眠", hours_text(float(df["sleep_hours"].mean())))

    with c3:
        st.metric("平均スコア", f"{int(df['score'].mean())}点")

    view = df.sort_values("date", ascending=False)

    st.dataframe(
        view[[
            "date",
            "bed_time",
            "wake_time",
            "sleep_hours",
            "quality",
            "wake_count",
            "rank",
            "score",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・削除")

    selected_id = st.selectbox(
        "記録を選ぶ",
        view["id"].tolist(),
        format_func=lambda x: f"{find_log(data, x)['date']} / {hours_text(find_log(data, x)['sleep_hours'])} / {find_log(data, x)['rank']}"
    )

    selected = find_log(data, selected_id)

    if selected:
        st.markdown(f"## {selected['date']} の睡眠")
        st.write(f"就寝：{selected['bed_date']} {selected['bed_time']}")
        st.write(f"起床：{selected['wake_date']} {selected['wake_time']}")
        st.write(f"睡眠時間：{hours_text(selected['sleep_hours'])}")
        st.write(f"睡眠の質：{selected['quality']}")
        st.write(f"途中覚醒：{selected['wake_count']}")
        st.write(f"ランク：{selected['rank']} / {selected['score']}点")

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
        file_name="day176_sleep_tracker.csv",
        mime="text/csv"
    )
