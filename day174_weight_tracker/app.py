import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day174：体重管理グラフ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day174_weight_tracker.json")


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "logs": [],
                    "settings": {
                        "height_cm": 170.0,
                        "target_weight": 65.0
                    }
                },
                f,
                ensure_ascii=False,
                indent=2
            )


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    if "settings" not in data:
        data["settings"] = {
            "height_cm": 170.0,
            "target_weight": 65.0
        }

    if "height_cm" not in data["settings"]:
        data["settings"]["height_cm"] = 170.0

    if "target_weight" not in data["settings"]:
        data["settings"]["target_weight"] = 65.0

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def calc_bmi(weight, height_cm):
    if height_cm <= 0:
        return 0

    height_m = height_cm / 100
    return round(weight / (height_m * height_m), 1)


def bmi_label(bmi):
    if bmi <= 0:
        return "未計算"

    if bmi < 18.5:
        return "低体重"

    if bmi < 25:
        return "普通体重"

    if bmi < 30:
        return "肥満1度"

    if bmi < 35:
        return "肥満2度"

    return "肥満3度以上"


def kg(value):
    return f"{float(value):.1f} kg"


def pct(value):
    return f"{float(value):.1f} %"


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "weight": float(x.get("weight", 0)),
            "body_fat": float(x.get("body_fat", 0)),
            "bmi": float(x.get("bmi", 0)),
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
    page_icon="📉",
    layout="wide"
)

st.title("📉 Day174：体重管理グラフ")
st.caption("体重・体脂肪率・BMIを記録して、推移を見える化するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("基本設定")

    height_cm = st.number_input(
        "身長（cm）",
        min_value=100.0,
        max_value=230.0,
        value=float(data["settings"].get("height_cm", 170.0)),
        step=0.1
    )

    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=30.0,
        max_value=200.0,
        value=float(data["settings"].get("target_weight", 65.0)),
        step=0.1
    )

    if st.button("設定を保存"):
        data["settings"]["height_cm"] = float(height_cm)
        data["settings"]["target_weight"] = float(target_weight)

        save_data(data)

        st.success("設定を保存したよ。")
        st.rerun()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    weight = st.number_input(
        "体重（kg）",
        min_value=20.0,
        max_value=250.0,
        value=70.0,
        step=0.1
    )

    body_fat = st.number_input(
        "体脂肪率（%）",
        min_value=0.0,
        max_value=80.0,
        value=25.0,
        step=0.1
    )

    bmi = calc_bmi(
        weight,
        float(data["settings"].get("height_cm", 170.0))
    )

    st.info(f"BMI：{bmi} / {bmi_label(bmi)}")

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：筋トレあり / 食べすぎた / むくみ気味"
    )

    if st.button("📉 記録する", type="primary"):
        item = {
            "id": f"weight_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": log_date.isoformat(),
            "weight": float(weight),
            "body_fat": float(body_fat),
            "bmi": float(bmi),
            "memo": memo.strip(),
        }

        data["logs"].append(item)
        save_data(data)

        st.success("体重記録を保存したよ。")
        st.rerun()

with right:
    st.subheader("現在の状況")

    df = to_df(data)
    target = float(data["settings"].get("target_weight", 65.0))

    if df.empty:
        st.info("まだ記録がないよ。")
    else:
        latest = df.iloc[-1]
        first = df.iloc[0]

        latest_weight = float(latest["weight"])
        first_weight = float(first["weight"])
        diff_from_first = latest_weight - first_weight
        diff_to_target = latest_weight - target

        c1, c2 = st.columns(2)

        with c1:
            st.metric("最新体重", kg(latest_weight))
            st.metric("体脂肪率", pct(latest["body_fat"]))

        with c2:
            st.metric("開始から", kg(diff_from_first))
            st.metric("目標まで", kg(diff_to_target))

        if diff_to_target <= 0:
            st.success("目標体重を達成してるよ！")
        else:
            st.info(f"目標まであと {kg(diff_to_target)}")

        st.divider()

        st.subheader("BMI")
        latest_bmi = float(latest["bmi"])
        st.metric("最新BMI", latest_bmi)
        st.info(bmi_label(latest_bmi))

st.divider()
st.subheader("グラフ")

df = to_df(data)

if df.empty:
    st.write("まだグラフ表示できる記録がないよ。")
else:
    chart_df = df.set_index("date")

    st.write("体重推移")
    st.line_chart(chart_df[["weight"]])

    st.write("体脂肪率推移")
    st.line_chart(chart_df[["body_fat"]])

    st.write("BMI推移")
    st.line_chart(chart_df[["bmi"]])

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    view = df.sort_values("date", ascending=False)

    st.dataframe(
        view[["date", "weight", "body_fat", "bmi", "memo"]],
        use_container_width=True,
        height=300
    )

    st.divider()
    st.subheader("詳細・削除")

    selected_id = st.selectbox(
        "記録を選ぶ",
        view["id"].tolist(),
        format_func=lambda x: f"{find_log(data, x)['date']} / {kg(find_log(data, x)['weight'])}"
    )

    selected = find_log(data, selected_id)

    if selected:
        st.markdown(f"## {selected['date']}")
        st.write(f"体重：{kg(selected['weight'])}")
        st.write(f"体脂肪率：{pct(selected['body_fat'])}")
        st.write(f"BMI：{selected['bmi']}")

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
        file_name="day174_weight_tracker.csv",
        mime="text/csv"
    )
