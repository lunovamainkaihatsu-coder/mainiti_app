from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st
from dateutil.relativedelta import relativedelta


APP_TITLE = "📅 支払い日リマインダー（Day74）"

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "payments.json"


# -----------------------------
# 保存/読込
# -----------------------------
def load_data() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_data(rows):
    DATA_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def yen(n: int):
    return f"¥{n:,}"


# -----------------------------
# 次回日計算
# -----------------------------
def calc_next(d: date, kind: str) -> date:
    today = date.today()

    while d < today:
        if kind == "毎月":
            d += relativedelta(months=1)
        elif kind == "毎年":
            d += relativedelta(years=1)
        else:
            break
    return d


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("📅 支払い日リマインダー")
st.caption("固定費を“見える化”して、安心して暮らす。")

rows = load_data()

st.divider()

# -----------------------------
# 追加フォーム
# -----------------------------
st.subheader("➕ 追加")

name = st.text_input("名前（例：家賃 / Netflix / 保険）")
amount = st.number_input("金額", min_value=0, step=1000)
next_date = st.date_input("次回日", value=date.today())
kind = st.selectbox("周期", ["毎月", "毎年", "1回のみ"])

if st.button("追加する"):
    if name:
        rows.append({
            "name": name,
            "amount": int(amount),
            "date": next_date.isoformat(),
            "kind": kind
        })
        save_data(rows)
        st.rerun()


st.divider()

# -----------------------------
# 表示
# -----------------------------
st.subheader("📋 一覧")

today = date.today()

display = []

for r in rows:
    d = date.fromisoformat(r["date"])
    d = calc_next(d, r["kind"])
    days = (d - today).days

    display.append({
        "name": r["name"],
        "amount": r["amount"],
        "date": d,
        "days": days,
        "kind": r["kind"]
    })

# 近い順
display.sort(key=lambda x: x["days"])

month_total = 0
next_month_total = 0

for item in display:
    if item["days"] <= 30:
        month_total += item["amount"]
    if 30 < item["days"] <= 60:
        next_month_total += item["amount"]

col1, col2 = st.columns(2)
col1.metric("今月予定", yen(month_total))
col2.metric("来月予定", yen(next_month_total))

st.divider()

for i, item in enumerate(display):
    color = "🔴" if item["days"] <= 3 else "🟡" if item["days"] <= 7 else "🟢"

    cols = st.columns([3, 2, 2, 1])

    cols[0].write(f"{color} **{item['name']}**")
    cols[1].write(yen(item["amount"]))
    cols[2].write(f"{item['date']}（{item['days']}日後）")

    if cols[3].button("削除", key=i):
        rows.pop(i)
        save_data(rows)
        st.rerun()

st.divider()

st.caption("🌙 近い順に並ぶから、もう忘れないよ。安心していい。")
