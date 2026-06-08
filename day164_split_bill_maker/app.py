import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import math

APP_TITLE = "Day164：割り勘メーカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day164_split_bill_maker.json")

ROUND_OPTIONS = [
    "1円単位",
    "10円単位",
    "100円単位",
    "500円単位",
    "1000円単位",
]

ROUND_METHODS = [
    "四捨五入",
    "切り上げ",
    "切り捨て",
]

PAY_TYPES = [
    "全員同額",
    "幹事多め",
    "子ども少なめ",
    "個別調整あり",
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


def yen(value):
    return f"{int(value):,} 円"


def round_unit(option):
    return {
        "1円単位": 1,
        "10円単位": 10,
        "100円単位": 100,
        "500円単位": 500,
        "1000円単位": 1000,
    }.get(option, 1)


def apply_round(value, unit, method):
    if unit <= 1:
        return int(round(value))

    if method == "切り上げ":
        return int(math.ceil(value / unit) * unit)

    if method == "切り捨て":
        return int(math.floor(value / unit) * unit)

    return int(round(value / unit) * unit)


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "total": x["total"],
            "people": x["people"],
            "pay_type": x["pay_type"],
            "per_person": x["per_person"],
            "collected_total": x["collected_total"],
            "difference": x["difference"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="👥",
    layout="wide"
)

st.title("👥 Day164：割り勘メーカー")
st.caption("合計金額・人数・端数処理を入れると、1人いくらかをすぐ計算するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("割り勘条件")

    title = st.text_input(
        "タイトル",
        placeholder="例：飲み会 / 家族外食 / 旅行費"
    )

    total = st.number_input(
        "合計金額",
        min_value=0,
        value=5000,
        step=100
    )

    people = st.number_input(
        "人数",
        min_value=1,
        value=2,
        step=1
    )

    pay_type = st.selectbox(
        "計算タイプ",
        PAY_TYPES
    )

    round_option = st.selectbox(
        "端数単位",
        ROUND_OPTIONS,
        index=2
    )

    round_method = st.selectbox(
        "端数処理",
        ROUND_METHODS,
        index=1
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：幹事が多めに払う / 子どもは半額"
    )

with right:
    st.subheader("計算結果")

    unit = round_unit(round_option)
    base = total / people if people else 0

    rows = []

    if pay_type == "全員同額":
        per_person = apply_round(base, unit, round_method)

        for i in range(1, people + 1):
            rows.append({
                "名前": f"人{i}",
                "支払額": per_person,
                "備考": "同額",
            })

    elif pay_type == "幹事多め":
        organizer_extra = st.number_input(
            "幹事が多めに払う金額",
            min_value=0,
            value=500,
            step=100
        )

        normal_people = max(people - 1, 1)
        normal_base = max((total - organizer_extra) / people, 0)
        normal_pay = apply_round(normal_base, unit, round_method)
        organizer_pay = total - normal_pay * (people - 1)

        rows.append({
            "名前": "幹事",
            "支払額": organizer_pay,
            "備考": "多め",
        })

        for i in range(2, people + 1):
            rows.append({
                "名前": f"人{i}",
                "支払額": normal_pay,
                "備考": "通常",
            })

    elif pay_type == "子ども少なめ":
        child_count = st.number_input(
            "子どもの人数",
            min_value=0,
            max_value=int(people),
            value=1 if people >= 2 else 0,
            step=1
        )

        child_rate = st.slider(
            "子どもの負担割合",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1
        )

        adult_count = people - child_count

        weight_total = adult_count + child_count * child_rate
        adult_pay_raw = total / weight_total if weight_total else 0
        child_pay_raw = adult_pay_raw * child_rate

        adult_pay = apply_round(adult_pay_raw, unit, round_method)
        child_pay = apply_round(child_pay_raw, unit, round_method)

        for i in range(1, adult_count + 1):
            rows.append({
                "名前": f"大人{i}",
                "支払額": adult_pay,
                "備考": "大人",
            })

        for i in range(1, child_count + 1):
            rows.append({
                "名前": f"子ども{i}",
                "支払額": child_pay,
                "備考": f"{child_rate:g}倍",
            })

    elif pay_type == "個別調整あり":
        st.write("人ごとに加算・減算を入れるタイプ。")

        names = []
        adjustments = []

        for i in range(1, people + 1):
            c1, c2 = st.columns([2, 1])
            with c1:
                name = st.text_input(
                    f"名前 {i}",
                    value=f"人{i}",
                    key=f"name_{i}"
                )
            with c2:
                adj = st.number_input(
                    f"調整 {i}",
                    value=0,
                    step=100,
                    key=f"adj_{i}"
                )

            names.append(name)
            adjustments.append(adj)

        adjusted_total = total + sum(adjustments)
        base_pay = apply_round(adjusted_total / people, unit, round_method)

        for name, adj in zip(names, adjustments):
            pay = max(base_pay - adj, 0)
            rows.append({
                "名前": name,
                "支払額": pay,
                "備考": f"調整 {adj:+,}円",
            })

    result_df = pd.DataFrame(rows)

    if not result_df.empty:
        collected_total = int(result_df["支払額"].sum())
    else:
        collected_total = 0

    difference = collected_total - total
    per_person_display = int(result_df["支払額"].mean()) if not result_df.empty else 0

    c1, c2, c3 = st.columns(3)

    c1.metric("1人目安", yen(per_person_display))
    c2.metric("回収合計", yen(collected_total))
    c3.metric("差額", yen(difference))

    if difference > 0:
        st.info(f"合計より {yen(difference)} 多く集まるよ。")
    elif difference < 0:
        st.warning(f"合計より {yen(abs(difference))} 足りないよ。")
    else:
        st.success("ぴったり！")

    st.dataframe(
        result_df,
        use_container_width=True,
        height=260
    )

    if st.button("👥 計算結果を保存", type="primary"):
        data["logs"].append({
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "title": title.strip(),
            "total": int(total),
            "people": int(people),
            "pay_type": pay_type,
            "round_option": round_option,
            "round_method": round_method,
            "per_person": int(per_person_display),
            "collected_total": int(collected_total),
            "difference": int(difference),
            "details": result_df.to_dict(orient="records"),
            "memo": memo.strip(),
        })

        save_data(data)
        st.success("割り勘結果を保存したよ。")
        st.rerun()

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df[["date", "title", "total", "people", "pay_type", "per_person", "collected_total", "difference", "memo"]],
        use_container_width=True,
        height=300
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day164_split_bill_maker.csv",
        mime="text/csv"
    )
