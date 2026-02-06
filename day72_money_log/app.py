from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st

APP_TITLE = "💰 1行家計簿（Day72）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "money_log.json"

DISCLAIMER = "※これは簡易ログです。まず“記録できた”を勝ちにします。"


# -------------------------
# 保存/読込
# -------------------------
def load_rows() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_rows(rows: List[Dict[str, Any]]) -> None:
    DATA_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def yen(n: int) -> str:
    return f"¥{n:,}"


def month_key(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("💰 1行家計簿")
st.caption("今日いくら使った？ それだけでOK。")
st.info(DISCLAIMER)

rows = load_rows()

st.divider()

# 入力
st.subheader("✍️ 追加")
col1, col2 = st.columns([2, 1])

with col1:
    dt = st.date_input("日付", value=date.today())
with col2:
    amount = st.number_input("金額（円）", min_value=0, step=100, value=0)

category = st.selectbox(
    "カテゴリ",
    ["食費", "日用品", "交通", "娯楽", "医療", "子ども", "仕事/学習", "その他"],
)
memo = st.text_input("メモ（任意）", placeholder="例：マグロ丼、カフェ、薬…")

cA, cB = st.columns(2)
with cA:
    if st.button("➕ 追加する", use_container_width=True):
        if amount <= 0:
            st.warning("金額が0円だよ。0円を記録したい場合はメモに理由を書いてね。")
        else:
            rows.append(
                {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "date": dt.isoformat(),
                    "amount": int(amount),
                    "category": category,
                    "memo": memo.strip(),
                }
            )
            save_rows(rows)
            st.success("追加したよ。")
            st.rerun()

with cB:
    if st.button("🧹 入力クリア", use_container_width=True):
        st.rerun()

st.divider()

# 集計
today_key = date.today().isoformat()
this_month = month_key(date.today())

today_sum = sum(r["amount"] for r in rows if r.get("date") == today_key)
month_sum = sum(r["amount"] for r in rows if month_key(date.fromisoformat(r["date"])) == this_month)

st.subheader("📊 サマリー")
colS1, colS2 = st.columns(2)
with colS1:
    st.metric("今日の合計", yen(int(today_sum)))
with colS2:
    st.metric("今月の合計", yen(int(month_sum)))

# カテゴリ別（今月）
cat_sum = {}
for r in rows:
    try:
        d = date.fromisoformat(r["date"])
    except Exception:
        continue
    if month_key(d) != this_month:
        continue
    cat_sum[r["category"]] = cat_sum.get(r["category"], 0) + int(r["amount"])

if cat_sum:
    st.caption("今月のカテゴリ別（合計）")
    # 見やすいように大きい順
    for k, v in sorted(cat_sum.items(), key=lambda x: x[1], reverse=True):
        st.write(f"・{k}: {yen(int(v))}")
else:
    st.caption("今月の記録がまだないよ。")

st.divider()

# 表示・フィルタ
st.subheader("🗂 ログ")
show_month = st.selectbox(
    "表示する月",
    sorted({month_key(date.fromisoformat(r["date"])) for r in rows} | {this_month}, reverse=True),
)

filtered = []
for r in rows:
    try:
        d = date.fromisoformat(r["date"])
    except Exception:
        continue
    if month_key(d) == show_month:
        filtered.append(r)

# 日付降順
filtered.sort(key=lambda x: x.get("date", ""), reverse=True)

if not filtered:
    st.write("この月の記録はまだないよ。")
else:
    for i, r in enumerate(filtered[:60]):  # 表示負荷を抑える
        d = r.get("date", "")
        a = yen(int(r.get("amount", 0)))
        c = r.get("category", "")
        m = r.get("memo", "")
        st.markdown(f"**{d}**  |  **{a}**  |  {c}")
        if m:
            st.caption(m)
        st.write("---")

st.divider()

# 危険じゃない範囲で“気づき”を出す（固定ルール）
st.subheader("🌙 ひとこと")
if month_sum == 0:
    st.write("まだゼロ。いまは“記録できたら勝ち”でいこう。")
else:
    if month_sum < 5000:
        st.write("いい感じ。小さく記録を続けるだけで強くなる。")
    elif month_sum < 20000:
        st.write("順調。今月は“カテゴリで増えやすいもの”を見つけられそう。")
    else:
        st.write("記録が増えてきたね。まずは“見える化”できてるのが勝ち。")
