import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day168：買うか悩むチェッカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day168_buy_or_not.json")

CATEGORIES = [
    "本",
    "ガジェット",
    "服",
    "健康",
    "学習",
    "趣味",
    "仕事",
    "家族",
    "その他",
]

RESULTS = {
    "buy": {
        "label": "🟢 今買うべし",
        "comment": "必要度も使用頻度も高め。買って活かせる可能性が高いよ。",
    },
    "wait": {
        "label": "🟡 30日待とう",
        "comment": "欲しい気持ちはあるけど、少し冷却期間を置くと判断しやすいよ。",
    },
    "skip": {
        "label": "🔴 見送り推奨",
        "comment": "今は優先度が低め。買わない選択も立派な節約だよ。",
    },
}


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


def current_month():
    return date.today().strftime("%Y-%m")


def yen(value):
    return f"{int(value):,} 円"


def judge(price, desire, need, frequency, wait_days):
    score = desire * 0.25 + need * 0.35 + frequency * 0.30 + min(wait_days, 30) / 30 * 1.0

    if price >= 30000:
        score -= 2
    elif price >= 10000:
        score -= 1
    elif price <= 2000:
        score += 0.5

    if need >= 8 and frequency >= 7:
        score += 1

    if desire >= 9 and need <= 4:
        score -= 1.5

    if score >= 7:
        return "buy", round(score, 1)

    if score >= 4.5:
        return "wait", round(score, 1)

    return "skip", round(score, 1)


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "month": x["date"][:7],
            "item": x["item"],
            "category": x["category"],
            "price": int(x.get("price", 0)),
            "desire": int(x.get("desire", 0)),
            "need": int(x.get("need", 0)),
            "frequency": int(x.get("frequency", 0)),
            "wait_days": int(x.get("wait_days", 0)),
            "score": float(x.get("score", 0)),
            "result": x.get("result_label", ""),
            "bought": bool(x.get("bought", False)),
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
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Day168：買うか悩むチェッカー")
st.caption("価格・欲しい度・必要度・使用頻度から、買うか待つか見送りかを判定するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("買うか判定する")

    item = st.text_input(
        "商品名",
        placeholder="例：本、ガジェット、服、教材"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    price = st.number_input(
        "価格",
        min_value=0,
        value=3000,
        step=100
    )

    desire = st.slider(
        "欲しい度",
        min_value=1,
        max_value=10,
        value=5
    )

    need = st.slider(
        "必要度",
        min_value=1,
        max_value=10,
        value=5
    )

    frequency = st.slider(
        "使用頻度",
        min_value=1,
        max_value=10,
        value=5
    )

    wait_days = st.slider(
        "待てる日数",
        min_value=0,
        max_value=30,
        value=7
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：本当に使う？代用品はある？今月の予算は？"
    )

    if st.button("🛒 判定する", type="primary"):
        if not item.strip():
            st.warning("商品名を入れてね。")
        else:
            result_key, score = judge(
                price,
                desire,
                need,
                frequency,
                wait_days
            )

            result = RESULTS[result_key]

            log = {
                "id": f"buy_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "item": item.strip(),
                "category": category,
                "price": int(price),
                "desire": int(desire),
                "need": int(need),
                "frequency": int(frequency),
                "wait_days": int(wait_days),
                "score": score,
                "result_key": result_key,
                "result_label": result["label"],
                "comment": result["comment"],
                "memo": memo.strip(),
                "bought": False,
            }

            data["logs"].append(log)
            save_data(data)

            st.session_state["latest"] = log
            st.rerun()

with right:
    st.subheader("判定結果")

    latest = st.session_state.get("latest")

    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"## {latest['result_label']}")
        st.metric("判定スコア", latest["score"])
        st.write(f"商品：{latest['item']}")
        st.write(f"価格：{yen(latest['price'])}")
        st.info(latest.get("comment", ""))

        st.divider()

        st.write(f"欲しい度：{latest['desire']} / 10")
        st.progress(latest["desire"] / 10)

        st.write(f"必要度：{latest['need']} / 10")
        st.progress(latest["need"] / 10)

        st.write(f"使用頻度：{latest['frequency']} / 10")
        st.progress(latest["frequency"] / 10)

        if latest["result_key"] == "wait":
            st.warning("迷うなら一度ほしいものリストに入れて、30日後に再判定しよう。")
        elif latest["result_key"] == "skip":
            st.success(f"買わなければ {yen(latest['price'])} 守れるよ。")
        else:
            st.success("買うなら、使い倒す前提でいこう。")

    else:
        st.info("まだ判定してないよ。")

st.divider()
st.subheader("判定履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="商品名・メモ")

    with col_b:
        category_filter = st.selectbox("カテゴリで絞る", ["すべて"] + CATEGORIES)

    with col_c:
        result_filter = st.selectbox(
            "判定で絞る",
            ["すべて"] + [x["label"] for x in RESULTS.values()]
        )

    bought_only = st.checkbox("✅ 買ったものだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["item"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if result_filter != "すべて":
        view = view[view["result"] == result_filter]

    if bought_only:
        view = view[view["bought"] == True]

    st.dataframe(
        view[["date", "item", "category", "price", "score", "result", "bought", "memo"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う履歴がないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['date']} / {row['item']} / {yen(row['price'])} / {row['result']}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "記録を選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        record = find_log(data, selected_id)

        if record:
            st.markdown(f"## {record['item']}")
            st.write(f"価格：{yen(record['price'])}")
            st.write(f"判定：{record['result_label']}")
            st.write(f"スコア：{record['score']}")

            if record.get("memo"):
                st.info(record["memo"])

            bought = st.checkbox(
                "✅ 実際に買った",
                value=bool(record.get("bought", False)),
                key=f"bought_{record['id']}"
            )

            if st.button("📝 更新する"):
                record["bought"] = bought
                record["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ この記録を削除", type="secondary"):
                data["logs"] = [x for x in data["logs"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day168_buy_or_not.csv",
        mime="text/csv"
    )
