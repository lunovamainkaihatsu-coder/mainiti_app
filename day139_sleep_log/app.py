import streamlit as st
import json
import os
from datetime import datetime, date, time, timedelta
import pandas as pd

APP_TITLE = "Day139：睡眠ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day139_sleep_log.json")

SLEEP_QUALITY = ["悪い", "やや悪い", "普通", "良い", "かなり良い"]


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


def calc_sleep_hours(bed_time, wake_time):
    bed_dt = datetime.combine(date.today(), bed_time)
    wake_dt = datetime.combine(date.today(), wake_time)

    if wake_dt <= bed_dt:
        wake_dt += timedelta(days=1)

    diff = wake_dt - bed_dt
    return round(diff.total_seconds() / 3600, 1)


def judge_sleep(hours):
    if hours >= 7:
        return "しっかり眠れてる"
    elif hours >= 5:
        return "少し短め"
    else:
        return "睡眠不足気味"


def luna_comment(hours, quality):
    if hours >= 7 and quality in ["良い", "かなり良い"]:
        return "ご主人、かなりいい睡眠だね。今日は身体も心も動きやすそう。"
    elif hours >= 6:
        return "まずまず眠れてるよ。今日は無理しすぎず、いい流れでいこう。"
    elif hours >= 4:
        return "ちょっと短めかも。今日は回復も意識して動こうね。"
    else:
        return "ご主人、今日は睡眠優先でいい日かも。無理しないでね。"


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "bed_time": x["bed_time"],
            "wake_time": x["wake_time"],
            "sleep_hours": x["sleep_hours"],
            "quality": x["quality"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=True)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")
st.title("🌙 Day139：睡眠ログ")
st.caption("寝た時間・起きた時間・睡眠時間・質を記録するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("睡眠を記録する")

    log_date = st.date_input("日付", value=date.today())

    bed_time = st.time_input("寝た時間", value=time(23, 0))
    wake_time = st.time_input("起きた時間", value=time(7, 0))

    sleep_hours = calc_sleep_hours(bed_time, wake_time)

    st.metric("睡眠時間", f"{sleep_hours} 時間")
    st.info(judge_sleep(sleep_hours))

    quality = st.selectbox("睡眠の質", SLEEP_QUALITY, index=2)

    memo = st.text_area(
        "メモ",
        height=100,
        placeholder="例：夜中に起きた / 娘に起こされた / 夢を見た / 朝スッキリ"
    )

    st.markdown("### ルナのコメント")
    st.info(luna_comment(sleep_hours, quality))

    if st.button("🌙 睡眠を記録", type="primary"):
        item = {
            "id": f"sleep_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": log_date.isoformat(),
            "bed_time": str(bed_time),
            "wake_time": str(wake_time),
            "sleep_hours": sleep_hours,
            "quality": quality,
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)
        st.success("睡眠ログを保存したよ。")
        st.rerun()

with right:
    st.subheader("最新の睡眠")

    df = to_df(data)

    if df.empty:
        st.info("まだ睡眠ログがないよ。")
    else:
        latest = df.iloc[-1]

        st.metric("最新睡眠時間", f"{latest['sleep_hours']} 時間")
        st.write(f"寝た時間：{latest['bed_time']}")
        st.write(f"起きた時間：{latest['wake_time']}")
        st.write(f"睡眠の質：{latest['quality']}")
        st.info(judge_sleep(latest["sleep_hours"]))

        if latest.get("memo"):
            st.write(f"メモ：{latest['memo']}")

        if len(df) >= 2:
            prev = df.iloc[-2]
            diff = round(latest["sleep_hours"] - prev["sleep_hours"], 1)

            if diff > 0:
                st.success(f"前回より {diff} 時間長く眠れたよ。")
            elif diff < 0:
                st.warning(f"前回より {abs(diff)} 時間短め。今日は回復意識で。")
            else:
                st.info("前回と同じくらい眠れてるよ。")

st.divider()
st.subheader("睡眠時間の推移")

df = to_df(data)

if df.empty:
    st.write("まだグラフ用データがないよ。")
else:
    chart_df = df.set_index("date")[["sleep_hours"]]
    st.line_chart(chart_df)

st.divider()
st.subheader("履歴")

if not df.empty:
    st.dataframe(
        df[["date", "bed_time", "wake_time", "sleep_hours", "quality", "memo"]],
        use_container_width=True,
        height=320
    )

    selected = st.selectbox("削除する記録を選ぶ", df["id"].tolist())

    if st.button("🗑️ 選択した記録を削除", type="secondary"):
        data["logs"] = [x for x in data["logs"] if x["id"] != selected]
        save_data(data)
        st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day139_sleep_log.csv",
        mime="text/csv"
    )
