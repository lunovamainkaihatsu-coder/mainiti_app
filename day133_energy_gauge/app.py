import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day133：気力ゲージ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day133_energy_gauge.json")


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


def judge_state(value):
    if value >= 80:
        return (
            "🔥 高エネルギー",
            "今日はかなり動けそう。攻めるなら今かも。",
            "ご主人、今日は流れ来てるね。"
        )

    elif value >= 60:
        return (
            "✨ 安定",
            "いい感じ。無理せず進める日。",
            "今日は“普通に動ける”が強い日だよ。"
        )

    elif value >= 40:
        return (
            "🌥️ 低下気味",
            "少し重いかも。軽めでOK。",
            "ご主人、今日は小さくいこう。"
        )

    elif value >= 20:
        return (
            "🌧️ 回復優先",
            "今日は守りと回復を優先。",
            "無理に進まなくて大丈夫。"
        )

    else:
        return (
            "🛌 休息モード",
            "今日は生存だけでも十分。",
            "ご主人、今日は休む勇気も大事。"
        )


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "energy": x["energy"],
            "state": x["state"],
            "memo": x["memo"],
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at")

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="⚡", layout="wide")
st.title("⚡ Day133：気力ゲージ")
st.caption("今日のエネルギー状態を見える化するアプリ。")

data = load_data()

left, right = st.columns([1,1], gap="large")

# ----------------------------
# 入力
# ----------------------------
with left:
    st.subheader("今日の気力")

    energy = st.slider(
        "今の気力",
        0,
        100,
        50
    )

    memo = st.text_area(
        "ひとことメモ",
        height=120,
        placeholder="例：少し眠い、でも動けそう"
    )

    state, desc, luna = judge_state(energy)

    st.markdown(f"### {state}")
    st.write(desc)
    st.info(luna)

    if st.button("⚡ 気力を記録", type="primary"):

        item = {
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "energy": energy,
            "state": state,
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)

        st.success("気力を記録したよ。")
        st.rerun()

# ----------------------------
# 表示
# ----------------------------
with right:
    st.subheader("最近の状態")

    df = to_df(data)

    if df.empty:
        st.info("まだ記録がないよ")
    else:
        latest = data["logs"][-1]

        st.metric(
            "最新気力",
            latest["energy"]
        )

        st.write(f"状態：{latest['state']}")

        if latest["memo"]:
            st.write(f"メモ：{latest['memo']}")

        st.divider()

        st.subheader("推移")

        chart_df = df[["created_at", "energy"]].copy()
        chart_df = chart_df.set_index("created_at")

        st.line_chart(chart_df)

st.divider()

# ----------------------------
# 履歴
# ----------------------------
st.subheader("履歴")

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True,
        height=320
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day133_energy_gauge.csv",
        mime="text/csv"
    )
