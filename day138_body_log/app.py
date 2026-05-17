import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day138：体重・体脂肪・BMI管理ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day138_body_log.json")


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


def calc_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        return 0
    h = height_cm / 100
    return round(weight_kg / (h * h), 1)


def bmi_label(bmi):
    if bmi < 18.5:
        return "低体重"
    elif bmi < 25:
        return "普通体重"
    elif bmi < 30:
        return "肥満1度"
    else:
        return "肥満傾向"


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "weight": x["weight"],
            "body_fat": x["body_fat"],
            "height": x["height"],
            "bmi": x["bmi"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=True)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="⚖️", layout="wide")
st.title("⚖️ Day138：体重・体脂肪・BMI管理ログ")
st.caption("体重・体脂肪率・BMIを記録して、身体の変化を見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の身体データを記録")

    log_date = st.date_input("日付", value=date.today())

    height = st.number_input(
        "身長(cm)",
        min_value=100.0,
        max_value=230.0,
        value=170.0,
        step=0.1
    )

    weight = st.number_input(
        "体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=70.0,
        step=0.1
    )

    body_fat = st.number_input(
        "体脂肪率(%)",
        min_value=0.0,
        max_value=70.0,
        value=20.0,
        step=0.1
    )

    bmi = calc_bmi(weight, height)

    st.metric("BMI", bmi)
    st.info(f"判定：{bmi_label(bmi)}")

    memo = st.text_area(
        "メモ",
        height=100,
        placeholder="例：朝測定 / 筋トレ後 / 食べすぎた翌日 / 体が軽い"
    )

    if st.button("⚖️ 記録する", type="primary"):
        item = {
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": log_date.isoformat(),
            "height": float(height),
            "weight": float(weight),
            "body_fat": float(body_fat),
            "bmi": bmi,
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)
        st.success("身体データを記録したよ。")
        st.rerun()

with right:
    st.subheader("最新データ")

    df = to_df(data)

    if df.empty:
        st.info("まだ記録がないよ。")
    else:
        latest = df.iloc[-1]

        st.metric("最新体重", f"{latest['weight']} kg")
        st.metric("最新体脂肪率", f"{latest['body_fat']} %")
        st.metric("最新BMI", latest["bmi"])

        st.info(f"BMI判定：{bmi_label(latest['bmi'])}")

        if latest.get("memo"):
            st.write(f"メモ：{latest['memo']}")

        st.divider()

        if len(df) >= 2:
            prev = df.iloc[-2]
            diff = round(latest["weight"] - prev["weight"], 1)

            if diff < 0:
                st.success(f"前回より {abs(diff)} kg 減少")
            elif diff > 0:
                st.warning(f"前回より {diff} kg 増加")
            else:
                st.info("前回と同じ体重")

st.divider()
st.subheader("推移グラフ")

df = to_df(data)

if df.empty:
    st.write("まだグラフ用データがないよ。")
else:
    chart_df = df.set_index("date")[["weight", "body_fat", "bmi"]]
    st.line_chart(chart_df)

st.divider()
st.subheader("履歴")

if not df.empty:
    st.dataframe(
        df[["date", "weight", "body_fat", "height", "bmi", "memo"]],
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
        file_name="day138_body_log.csv",
        mime="text/csv"
    )
