import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day140：水分補給ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day140_water_log.json")

DRINK_TYPES = ["水", "お茶", "コーヒー", "プロテイン", "炭酸水", "その他"]
DEFAULT_GOAL = 2000


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


def luna_comment(total, goal):
    rate = total / goal if goal else 0

    if rate >= 1.0:
        return "ご主人、今日の水分いい感じ！身体も喜んでるよ。"
    elif rate >= 0.7:
        return "あと少しで目標だね。ここまでかなり良いよ。"
    elif rate >= 0.4:
        return "悪くないよ。もう1〜2回飲めると安心かな。"
    else:
        return "今日はまだ少なめかも。まず一口だけ飲もっか。"


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "drink_type": x["drink_type"],
            "amount_ml": x["amount_ml"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="💧", layout="wide")
st.title("💧 Day140：水分補給ログ")
st.caption("飲んだ量を記録して、今日の水分補給を見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("飲んだものを記録")

    log_date = st.date_input("日付", value=date.today())
    drink_type = st.selectbox("飲み物", DRINK_TYPES)

    amount_ml = st.number_input(
        "量（ml）",
        min_value=0,
        max_value=3000,
        value=250,
        step=50
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：朝起きてすぐ / 筋トレ後 / コーヒー"
    )

    if st.button("💧 記録する", type="primary"):
        if amount_ml <= 0:
            st.warning("量を入力してね。")
        else:
            item = {
                "id": f"water_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "drink_type": drink_type,
                "amount_ml": int(amount_ml),
                "memo": memo.strip(),
            }
            data["logs"].append(item)
            save_data(data)
            st.success("水分補給を記録したよ。")
            st.rerun()

with right:
    st.subheader("今日の水分")

    goal = st.number_input(
        "今日の目標（ml）",
        min_value=500,
        max_value=5000,
        value=DEFAULT_GOAL,
        step=100
    )

    today_logs = [x for x in data["logs"] if x["date"] == today_str()]
    total = sum(int(x.get("amount_ml", 0)) for x in today_logs)

    st.metric("今日の合計", f"{total} ml")

    progress = min(total / goal, 1.0)
    st.progress(progress)

    remaining = max(goal - total, 0)

    if remaining == 0:
        st.success("目標達成！")
    else:
        st.info(f"あと {remaining} ml")

    st.markdown("### ルナのひとこと")
    st.info(luna_comment(total, goal))

    st.divider()
    st.subheader("今日の内訳")

    if not today_logs:
        st.write("まだ今日の記録はないよ。")
    else:
        for x in sorted(today_logs, key=lambda y: y["created_at"]):
            st.write(f"{x['drink_type']}：{x['amount_ml']} ml")
            if x.get("memo"):
                st.caption(x["memo"])

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df[["date", "drink_type", "amount_ml", "memo"]],
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
        file_name="day140_water_log.csv",
        mime="text/csv"
    )
