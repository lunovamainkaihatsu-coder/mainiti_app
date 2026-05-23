import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day147：今日のステータス画面"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day147_today_status.json")

STATUS_ITEMS = {
    "体力": "❤️",
    "集中": "🧠",
    "回復": "✨",
    "お金意識": "💰",
    "やる気": "🔥",
    "安心感": "🌙",
}

MODES = ["回復日", "通常日", "前進日", "覚醒日"]


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


def judge_mode(avg):
    if avg >= 80:
        return "覚醒日"
    elif avg >= 60:
        return "前進日"
    elif avg >= 40:
        return "通常日"
    else:
        return "回復日"


def luna_comment(mode):
    comments = {
        "回復日": "ご主人、今日は無理に攻めなくていいよ。まずは整える日。",
        "通常日": "今日は普通に進める日。小さな一歩を積めば十分だよ。",
        "前進日": "いい感じ！今日は少し前に出ても大丈夫そう。",
        "覚醒日": "ご主人、今日はかなり流れが来てるかも。大事なことに触れてみよう。",
    }
    return comments.get(mode, "今日のご主人もちゃんと進んでるよ。")


def to_df(data):
    rows = []
    for x in data["logs"]:
        row = {
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "mode": x["mode"],
            "average": x["average"],
            "memo": x.get("memo", ""),
        }
        for key in STATUS_ITEMS.keys():
            row[key] = x["status"].get(key, 0)
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🎮", layout="wide")
st.title("🎮 Day147：今日のステータス画面")
st.caption("今日の自分をRPG風ステータスで見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日のステータス入力")

    status_values = {}

    for name, icon in STATUS_ITEMS.items():
        status_values[name] = st.slider(
            f"{icon} {name}",
            0,
            100,
            50,
            step=5
        )

    avg = round(sum(status_values.values()) / len(status_values), 1)
    mode = judge_mode(avg)

    st.metric("総合ステータス", f"{avg}")
    st.info(f"今日のモード：{mode}")
    st.info(luna_comment(mode))

    memo = st.text_area(
        "メモ",
        height=100,
        placeholder="例：眠いけど気分は悪くない / 今日は回復寄り"
    )

    if st.button("🎮 ステータス保存", type="primary"):
        item = {
            "id": f"status_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "status": status_values,
            "average": avg,
            "mode": mode,
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)
        st.success("今日のステータスを保存したよ。")
        st.rerun()

with right:
    st.subheader("最新ステータス")

    df = to_df(data)

    if df.empty:
        st.info("まだ記録がないよ。")
    else:
        latest = data["logs"][-1]

        st.markdown(f"## {latest['mode']}")
        st.metric("総合", latest["average"])
        st.info(luna_comment(latest["mode"]))

        for name, icon in STATUS_ITEMS.items():
            value = latest["status"].get(name, 0)
            st.write(f"{icon} {name}：{value}")
            st.progress(value / 100)

        if latest.get("memo"):
            st.write(f"メモ：{latest['memo']}")

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )

    chart_df = df.sort_values("date").set_index("date")[["average"]]
    st.line_chart(chart_df)

    selected = st.selectbox("削除する記録を選ぶ", df["id"].tolist())

    if st.button("🗑️ 選択した記録を削除", type="secondary"):
        data["logs"] = [x for x in data["logs"] if x["id"] != selected]
        save_data(data)
        st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day147_today_status.csv",
        mime="text/csv"
    )
