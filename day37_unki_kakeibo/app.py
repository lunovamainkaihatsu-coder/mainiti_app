import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="まいにち運気家計簿", page_icon="🌙", layout="centered")

# =========================
# 華やか背景（CSS）
# =========================
st.markdown("""
<style>
/* =========================
   selectbox（カテゴリ）の文字
   ========================= */

/* プルダウン未展開時 */
div[data-baseweb="select"] > div {
  background-color: rgba(255,255,255,0.95) !important;
  color: #1a1a1a !important;
}

/* 選択中の文字 */
div[data-baseweb="select"] span {
  color: #1a1a1a !important;
}

/* プルダウン展開後のリスト */
div[data-baseweb="popover"] div {
  background-color: #ffffff !important;
  color: #1a1a1a !important;
}

/* =========================
   file_uploader（レシート）
   ========================= */

section[data-testid="stFileUploader"] {
  background-color: rgba(255,255,255,0.95) !important;
  color: #1a1a1a !important;
  border-radius: 12px;
}

/* file_uploader 内のテキスト */
section[data-testid="stFileUploader"] * {
  color: #1a1a1a !important;
}

/* =========================
   保存ボタン
   ========================= */

button[kind="primary"] {
  background: linear-gradient(135deg, #6dd5fa, #2980b9) !important;
  color: #ffffff !important;
  border-radius: 14px !important;
  font-weight: 700;
  padding: 0.6em 1.4em;
}

/* hover時 */
button[kind="primary"]:hover {
  background: linear-gradient(135deg, #81ecec, #3498db) !important;
  color: #ffffff !important;
}

/* =========================
   radio（支出・収入）の文字
   ========================= */

label[data-baseweb="radio"] span {
  color: rgba(255,255,255,0.95) !important;
}

/* =========================
   数値入力 + - ボタン
   ========================= */

button[aria-label="Increment"],
button[aria-label="Decrement"] {
  color: #1a1a1a !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# パス・定数
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LEDGER_PATH = DATA_DIR / "ledger.csv"

EXPENSE_CATEGORIES = ["食費", "日用品", "交通", "娯楽", "自己投資", "固定費", "医療", "その他"]
INCOME_CATEGORIES = ["給料", "副収入", "臨時収入", "返金", "その他"]

# レシート保存先
RECEIPTS_DIR = DATA_DIR / "receipts"
RECEIPTS_DIR.mkdir(exist_ok=True)

# CSV列（レシート列追加）
COLUMNS = ["date", "type", "amount", "category", "memo", "unki", "receipt_path"]

# =========================
# 運気ロジック（ルールベース）
# - 曜日（主）
# - 月（味付け）
# - 季節/イベント（味付け）
# =========================
def get_unki_rule_based(d: date) -> dict:
    wd = d.weekday()  # Mon=0 ... Sun=6
    month = d.month
    day = d.day

    # 曜日ベース
    if wd == 0:
        unki_type = "🌱 節約運"
        base_hint = "週の始まりは整える日。小さな支出を見直すと強い。"
    elif wd == 1:
        unki_type = "🌕 自己投資向き"
        base_hint = "学び・改善に使うと回収しやすい日。"
    elif wd == 2:
        unki_type = "💎 使ってOK"
        base_hint = "小さなご褒美で気持ちを整えると流れが良くなる日。"
    elif wd == 3:
        unki_type = "🌱 節約運"
        base_hint = "固定費・習慣の見直しに向く日。"
    elif wd == 4:
        unki_type = "💎 使ってOK（上限つき）"
        base_hint = "楽しむのはOK。ただし“上限”を決めると運気が安定。"
    elif wd == 5:
        unki_type = "🔥 浪費注意"
        base_hint = "衝動が増えやすい日。買う前に一回深呼吸がおすすめ。"
    else:
        unki_type = "🌕 自己投資向き"
        base_hint = "来週の準備にお金を使うと心が軽くなる日。"

    # 月の味付け（軽め）
    if month in (1, 4, 9):
        month_hint = "新しい流れの月。まずは“整える支出”が吉。"
    elif month in (2, 6, 11):
        month_hint = "積み上げの月。小さな節約が大きく効いてくるよ。"
    elif month in (3, 7, 12):
        month_hint = "出入りが大きくなりやすい月。記録でブレを抑えよう。"
    else:
        month_hint = "安定しやすい月。無理なく“続ける”が勝ち。"

    # イベント味付け
    event_hint = ""
    if month == 12:
        event_hint = "年末は出費が増えがち。『予定された出費』に強くしよう。"
    if month == 1 and day <= 10:
        event_hint = "年始は“今年の方針”を決めるとお金の流れが整うよ。"
    if day >= 28:
        event_hint = (event_hint + " " if event_hint else "") + "月末は締めの日。まとめて見直すと◎"

    hint = base_hint + " " + month_hint + (" " + event_hint if event_hint else "")
    return {"type": unki_type, "hint": hint.strip()}

def luna_message(unki_type: str, entry_type: str) -> str:
    if entry_type == "収入":
        return "入ってきた…！流れが来てるよ✨ ちゃんと記録できてえらい。"

    # 支出向け
    if "節約運" in unki_type:
        return "えらい…！今日の節約は“運を貯金”してるみたいだよ🌱"
    if "上限つき" in unki_type:
        return "ご褒美OKの日✨ でも上限を決めたら勝ちだよ。"
    if "使ってOK" in unki_type:
        return "うん、その使い方なら素敵✨ちゃんと心が満ちてる。"
    if "浪費注意" in unki_type:
        return "記録できたのが勝ち！次は買う前に3秒止まろ？🔥"
    if "自己投資" in unki_type:
        return "未来のご主人にプレゼントだね🌕すごくいい使い方。"
    return "今日も記録できたね。ちゃんと前に進んでるよ🌙"

# =========================
# データ読み書き
# =========================
def load_ledger() -> pd.DataFrame:
    if not LEDGER_PATH.exists():
        return pd.DataFrame(columns=COLUMNS)

    df = pd.read_csv(LEDGER_PATH)

    # 欠け列対策（旧CSVでも落ちない）
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = ""

    # 型の安全
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0).astype(int)
    df["date"] = df["date"].astype(str)
    df["type"] = df["type"].astype(str)
    df["category"] = df["category"].astype(str)
    df["memo"] = df["memo"].astype(str)
    df["unki"] = df["unki"].astype(str)
    df["receipt_path"] = df["receipt_path"].astype(str)

    return df[COLUMNS]

def append_row(row: dict):
    df = load_ledger()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(LEDGER_PATH, index=False)

def save_receipt_image(uploaded_file, d: date) -> str:
    """画像を data/receipts/YYYY-MM/ に保存し、BASE_DIR相対パスを返す"""
    if uploaded_file is None:
        return ""

    ym = d.strftime("%Y-%m")
    save_dir = RECEIPTS_DIR / ym
    save_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"

    file_path = save_dir / f"{ts}{ext}"
    file_path.write_bytes(uploaded_file.getbuffer())

    # app.py基準の相対パスとして保存（移動しても強い）
    rel_path = file_path.relative_to(BASE_DIR)
    return str(rel_path)

# =========================
# UI
# =========================
st.title("🌙 まいにち運気家計簿")
today = date.today()
unki_today = get_unki_rule_based(today)

st.caption(f"今日：{today.isoformat()}")

# 今日の金運カード
st.subheader("🔮 今日の金運")
with st.container(border=True):
    st.markdown(f"### {unki_today['type']}")
    st.write(unki_today["hint"])

st.divider()

# 入力フォーム
st.subheader("🧾 収入・支出を記録する")
with st.form("add_entry", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input("日付", value=today)
    with col2:
        entry_type = st.radio("種別", ["支出", "収入"], horizontal=True)

    if entry_type == "支出":
        category = st.selectbox("カテゴリ（支出）", EXPENSE_CATEGORIES)
        amount = st.number_input("金額（円）", min_value=0, step=100, value=0)
        memo = st.text_input("メモ（任意）", placeholder="例：コンビニ / ランチ / 電車 など")
        receipt = st.file_uploader("レシート画像（任意）", type=["png", "jpg", "jpeg", "webp"])
    else:
        category = st.selectbox("カテゴリ（収入）", INCOME_CATEGORIES)
        amount = st.number_input("金額（円）", min_value=0, step=100, value=0)
        memo = st.text_input("メモ（任意）", placeholder="例：給料 / 返金 / 臨時 など")
        receipt = None  # 収入には今は付けない

    submitted = st.form_submit_button("保存する")

if submitted:
    if amount <= 0:
        st.error("金額が0円だと保存できないよ。1円以上で入れてね！")
    else:
        unki_for_date = get_unki_rule_based(d)

        receipt_path = ""
        if entry_type == "支出" and receipt is not None:
            receipt_path = save_receipt_image(receipt, d)

        row = {
            "date": d.isoformat(),
            "type": entry_type,
            "amount": int(amount),
            "category": category,
            "memo": memo.strip(),
            "unki": unki_for_date["type"],
            "receipt_path": receipt_path,
        }
        append_row(row)
        st.success("保存したよ！")
        st.info(luna_message(unki_for_date["type"], entry_type))

st.divider()

# データロード（ここから下で使う）
df = load_ledger()

# 今日のまとめ
st.subheader("📌 今日のまとめ")
if df.empty:
    st.caption("まだデータがないよ。最初の1件を入れてみてね！")
else:
    df_today = df[df["date"] == today.isoformat()].copy()

    income_today = int(df_today[df_today["type"] == "収入"]["amount"].sum()) if not df_today.empty else 0
    expense_today = int(df_today[df_today["type"] == "支出"]["amount"].sum()) if not df_today.empty else 0
    balance_today = income_today - expense_today

    c1, c2, c3 = st.columns(3)
    c1.metric("収入", f"{income_today:,} 円")
    c2.metric("支出", f"{expense_today:,} 円")
    c3.metric("差額", f"{balance_today:,} 円")

    st.write("カテゴリ別（支出）")
    df_exp = df_today[df_today["type"] == "支出"]
    if df_exp.empty:
        st.caption("今日の支出はまだないよ。")
    else:
        by_cat = df_exp.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.dataframe(by_cat.reset_index(), use_container_width=True, hide_index=True)

st.divider()

# 月まとめ
st.subheader("🗓️ 月まとめ")
if df.empty:
    st.caption("記録が増えると月まとめが効いてくる🌙")
else:
    df_dt = df.copy()
    df_dt["date_dt"] = pd.to_datetime(df_dt["date"], errors="coerce")
    df_dt["year_month"] = df_dt["date_dt"].dt.strftime("%Y-%m")

    ym_list = sorted(df_dt["year_month"].dropna().unique().tolist(), reverse=True)
    selected_ym = st.selectbox("表示する月（YYYY-MM）", ym_list, index=0)

    mdf = df_dt[df_dt["year_month"] == selected_ym].copy()

    income_m = int(mdf[mdf["type"] == "収入"]["amount"].sum())
    expense_m = int(mdf[mdf["type"] == "支出"]["amount"].sum())
    balance_m = income_m - expense_m

    c1, c2, c3 = st.columns(3)
    c1.metric("月の収入", f"{income_m:,} 円")
    c2.metric("月の支出", f"{expense_m:,} 円")
    c3.metric("月の差額", f"{balance_m:,} 円")

    st.write("カテゴリ別（支出）")
    exp = mdf[mdf["type"] == "支出"]
    if exp.empty:
        st.caption("この月の支出はまだないよ。")
    else:
        by_cat_m = exp.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.dataframe(by_cat_m.reset_index(), use_container_width=True, hide_index=True)

st.divider()

# 履歴（直近）
st.subheader("📚 履歴（直近）")
if df.empty:
    st.caption("履歴がここに出るよ。")
else:
    df_show = df.copy()
    df_show["date_dt"] = pd.to_datetime(df_show["date"], errors="coerce")
    df_show = df_show.sort_values("date_dt", ascending=False).drop(columns=["date_dt"]).head(30)
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSVをダウンロード",
        data=csv_bytes,
        file_name="ledger.csv",
        mime="text/csv",
    )

st.divider()

# レシート表示
st.subheader("🧾 レシート表示（直近から選択）")
if df.empty:
    st.caption("レシート付きの記録が増えると、ここで見れるよ！")
else:
    df_r = df.copy()
    df_r["date_dt"] = pd.to_datetime(df_r["date"], errors="coerce")
    df_r = df_r.sort_values("date_dt", ascending=False).head(50)

    options = []
    for _, r in df_r.iterrows():
        label = f"{r['date']} | {r['type']} | {r['amount']:,}円 | {r['category']} | {r.get('memo','')}"
        options.append((label, r.get("receipt_path", "")))

    selected = st.selectbox("選ぶ", options, format_func=lambda x: x[0])

    path = selected[1]
    if path and path.strip() and path != "nan":
        img_path = BASE_DIR / path
        if img_path.exists():
            st.image(str(img_path), caption=path, use_container_width=True)
        else:
            st.warning("画像が見つからなかったよ（保存先や相対パスがずれてるかも）")
    else:
        st.caption("この記録にはレシートが付いてないよ。")
