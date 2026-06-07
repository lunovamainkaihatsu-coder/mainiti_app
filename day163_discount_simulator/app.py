import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day163：割引計算シミュレーター"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day163_discount_simulator.json")

MODES = [
    "① 単品割引",
    "② 全品割引",
    "③ 単品・全品 複合割引",
    "④ 複数回割引",
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


def discount_price(price, rate):
    return round(price * (1 - rate / 100))


def yen(n):
    return f"{int(n):,} 円"


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "date": x["date"],
            "mode": x["mode"],
            "original_total": x["original_total"],
            "discount_total": x["discount_total"],
            "saved": x["saved"],
            "memo": x.get("memo", ""),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🛒", layout="wide")
st.title("🛒 Day163：割引計算シミュレーター")
st.caption("単品割引・全品割引・複合割引・複数回割引を計算するアプリ。")

data = load_data()

mode = st.radio("計算モード", MODES, horizontal=True)

st.divider()

# ----------------------------
# ① 単品割引
# ----------------------------
if mode == "① 単品割引":
    st.subheader("① 単品割引")

    price = st.number_input("元の金額", min_value=0, value=1000, step=100)
    rate = st.number_input("割引率（％）", min_value=0.0, max_value=100.0, value=10.0, step=1.0)

    result = discount_price(price, rate)
    saved = price - result

    c1, c2, c3 = st.columns(3)
    c1.metric("元の金額", yen(price))
    c2.metric("割引後", yen(result))
    c3.metric("お得額", yen(saved))

    st.success(f"{yen(price)} の {rate:g}%OFF → {yen(result)}")

    memo = st.text_input("メモ", placeholder="例：服、家電、セール品")

    if st.button("保存する", type="primary"):
        data["logs"].append({
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "mode": mode,
            "original_total": int(price),
            "discount_total": int(result),
            "saved": int(saved),
            "memo": memo,
        })
        save_data(data)
        st.success("保存したよ。")
        st.rerun()

# ----------------------------
# ② 全品割引
# ----------------------------
elif mode == "② 全品割引":
    st.subheader("② 全品割引")

    st.write("複数商品の合計に、同じ割引率をかける。")

    item_text = st.text_area(
        "商品の金額を1行ずつ入力",
        height=160,
        placeholder="例：\n1200\n980\n3500"
    )

    rate = st.number_input("全品割引率（％）", min_value=0.0, max_value=100.0, value=10.0, step=1.0)

    prices = []
    for line in item_text.splitlines():
        line = line.strip().replace(",", "")
        if line.isdigit:
            try:
                prices.append(int(line))
            except:
                pass

    original_total = sum(prices)
    discount_total = discount_price(original_total, rate)
    saved = original_total - discount_total

    c1, c2, c3 = st.columns(3)
    c1.metric("合計金額", yen(original_total))
    c2.metric("割引後", yen(discount_total))
    c3.metric("お得額", yen(saved))

    if prices:
        df_items = pd.DataFrame({
            "商品No": list(range(1, len(prices) + 1)),
            "元の金額": prices,
            "割引後目安": [discount_price(p, rate) for p in prices],
        })
        st.dataframe(df_items, use_container_width=True)

    memo = st.text_input("メモ", placeholder="例：スーパー全品10%OFF")

    if st.button("保存する", type="primary"):
        data["logs"].append({
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "mode": mode,
            "original_total": int(original_total),
            "discount_total": int(discount_total),
            "saved": int(saved),
            "memo": memo,
        })
        save_data(data)
        st.success("保存したよ。")
        st.rerun()

# ----------------------------
# ③ 単品・全品 複合割引
# ----------------------------
elif mode == "③ 単品・全品 複合割引":
    st.subheader("③ 単品・全品 複合割引")

    st.write("まず単品割引をかけて、その後に全品割引をかける。")

    item_text = st.text_area(
        "商品を1行ずつ入力：金額,単品割引率",
        height=180,
        placeholder="例：\n1200,10\n980,0\n3500,20"
    )

    all_rate = st.number_input("さらに全品割引率（％）", min_value=0.0, max_value=100.0, value=10.0, step=1.0)

    rows = []
    original_total = 0
    after_single_total = 0
    final_total = 0

    for i, line in enumerate(item_text.splitlines(), start=1):
        parts = [p.strip().replace(",", "") for p in line.split(",")]
        if len(parts) >= 1:
            try:
                price = int(parts[0])
                single_rate = float(parts[1]) if len(parts) >= 2 and parts[1] else 0.0

                after_single = discount_price(price, single_rate)
                final = discount_price(after_single, all_rate)

                original_total += price
                after_single_total += after_single
                final_total += final

                rows.append({
                    "商品No": i,
                    "元の金額": price,
                    "単品割引率": single_rate,
                    "単品割引後": after_single,
                    "全品割引後": final,
                    "お得額": price - final,
                })
            except:
                pass

    saved = original_total - final_total

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("元合計", yen(original_total))
    c2.metric("単品割引後", yen(after_single_total))
    c3.metric("最終金額", yen(final_total))
    c4.metric("お得額", yen(saved))

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    memo = st.text_input("メモ", placeholder="例：単品20%OFF＋全品10%OFF")

    if st.button("保存する", type="primary"):
        data["logs"].append({
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "mode": mode,
            "original_total": int(original_total),
            "discount_total": int(final_total),
            "saved": int(saved),
            "memo": memo,
        })
        save_data(data)
        st.success("保存したよ。")
        st.rerun()

# ----------------------------
# ④ 複数回割引
# ----------------------------
elif mode == "④ 複数回割引":
    st.subheader("④ 複数回割引")

    st.write("例：15%OFFの後に、さらに10%OFF。足し算ではなく順番に割引する。")

    price = st.number_input("元の金額", min_value=0, value=10000, step=100)

    rate_text = st.text_input(
        "割引率を順番に入力（カンマ区切り）",
        placeholder="例：15,10,5",
        value="15,10"
    )

    rates = []
    for x in rate_text.split(","):
        try:
            r = float(x.strip())
            if 0 <= r <= 100:
                rates.append(r)
        except:
            pass

    current = price
    rows = []

    for i, r in enumerate(rates, start=1):
        before = current
        current = discount_price(current, r)
        rows.append({
            "回数": i,
            "割引率": r,
            "割引前": before,
            "割引後": current,
            "この回のお得額": before - current,
        })

    saved = price - current

    c1, c2, c3 = st.columns(3)
    c1.metric("元の金額", yen(price))
    c2.metric("最終金額", yen(current))
    c3.metric("合計お得額", yen(saved))

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    simple_sum = sum(rates)
    if rates:
        st.info(f"割引率を足すと {simple_sum:g}% だけど、実際は順番に割引するから最終額が変わるよ。")

    memo = st.text_input("メモ", placeholder="例：セール＋クーポン")

    if st.button("保存する", type="primary"):
        data["logs"].append({
            "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "mode": mode,
            "original_total": int(price),
            "discount_total": int(current),
            "saved": int(saved),
            "memo": memo,
        })
        save_data(data)
        st.success("保存したよ。")
        st.rerun()

st.divider()
st.subheader("計算履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df[["date", "mode", "original_total", "discount_total", "saved", "memo"]],
        use_container_width=True,
        height=280
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day163_discount_simulator.csv",
        mime="text/csv"
    )
