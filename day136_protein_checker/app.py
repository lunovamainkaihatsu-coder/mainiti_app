import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day136：たんぱく質チェッカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day136_protein_checker.json")

PROTEIN_ITEMS = {
    "ゆで卵 1個": 6,
    "卵 2個": 12,
    "サラダチキン 1個": 25,
    "プロテインドリンク": 20,
    "Oikos系プロテイン": 18,
    "納豆 1パック": 8,
    "豆腐 半丁": 10,
    "鶏むね肉 100g": 23,
    "ツナ缶 1個": 13,
    "牛乳 200ml": 7,
    "ヨーグルト": 5,
    "鮭 1切れ": 20,
    "豚肉 100g": 20,
    "牛肉 100g": 20,
}

TARGET_PROTEIN = 100


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
            "meal_type": x["meal_type"],
            "items": ", ".join(x["items"]),
            "custom_item": x.get("custom_item", ""),
            "protein": x["protein"],
            "memo": x.get("memo", ""),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="💪", layout="wide")
st.title("💪 Day136：たんぱく質チェッカー")
st.caption("今日のたんぱく質をざっくり記録するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("食べたものを記録")

    meal_date = st.date_input("日付", value=date.today())
    meal_type = st.radio("区分", ["朝食", "昼食", "夕食", "間食"], horizontal=True)

    selected_items = st.multiselect(
        "食べたもの",
        list(PROTEIN_ITEMS.keys())
    )

    custom_item = st.text_input("その他の食品名（任意）")
    custom_protein = st.number_input("その他のたんぱく質量(g)", min_value=0, max_value=200, value=0)

    memo = st.text_area("メモ", placeholder="例：朝に卵2個、昼にサラダチキン")

    protein_sum = sum(PROTEIN_ITEMS[x] for x in selected_items) + custom_protein

    st.metric("今回のたんぱく質", f"{protein_sum} g")

    if st.button("💪 記録する", type="primary"):
        if not selected_items and not custom_item.strip():
            st.warning("食品を1つ選ぶか、その他食品を入力してね。")
        else:
            item = {
                "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": meal_date.isoformat(),
                "meal_type": meal_type,
                "items": selected_items,
                "custom_item": custom_item.strip(),
                "protein": int(protein_sum),
                "memo": memo.strip(),
            }
            data["logs"].append(item)
            save_data(data)
            st.success("たんぱく質を記録したよ。")
            st.rerun()

with right:
    st.subheader("今日の合計")

    today_logs = [x for x in data["logs"] if x["date"] == today_str()]
    today_total = sum(x["protein"] for x in today_logs)

    st.metric("今日のたんぱく質", f"{today_total} g")

    progress = min(today_total / TARGET_PROTEIN, 1.0)
    st.progress(progress)

    remaining = max(TARGET_PROTEIN - today_total, 0)

    if today_total >= TARGET_PROTEIN:
        st.success("目標達成！今日はかなりいい感じだよ。")
    elif today_total >= 70:
        st.info(f"あと {remaining}g。かなり近い！")
    elif today_total >= 40:
        st.warning(f"あと {remaining}g。もう一品たんぱく質を足したいね。")
    else:
        st.warning(f"あと {remaining}g。卵・鶏肉・プロテインを足すとよさそう。")

    st.divider()
    st.subheader("今日の内訳")

    if not today_logs:
        st.write("まだ今日の記録はないよ。")
    else:
        for x in sorted(today_logs, key=lambda y: y["created_at"]):
            st.markdown(f"**{x['meal_type']}：{x['protein']}g**")
            if x["items"]:
                st.write(", ".join(x["items"]))
            if x.get("custom_item"):
                st.write(x["custom_item"])
            if x.get("memo"):
                st.caption(x["memo"])

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df[["date", "meal_type", "items", "custom_item", "protein", "memo"]],
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
        file_name="day136_protein_checker.csv",
        mime="text/csv"
    )
