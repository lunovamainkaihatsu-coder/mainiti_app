import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd
import matplotlib.pyplot as plt

APP_TITLE = "Day83：Energy Meter（体力・集中・気分）"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day83_energy_meter.json")


# ---------- storage ----------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"entries": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_key() -> str:
    return date.today().isoformat()


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_entry(data, dkey):
    for e in data["entries"]:
        if e["date"] == dkey:
            return e
    return None


def get_or_create_today(data):
    dkey = today_key()
    e = find_entry(data, dkey)
    if e is None:
        e = {
            "date": dkey,
            "created_at": now_str(),
            "updated_at": now_str(),
            "morning": {},
            "noon": {},
            "night": {},
        }
        data["entries"].append(e)
        save_data(data)
    return e


def set_updated(entry):
    entry["updated_at"] = now_str()


# ---------- logic ----------
def avg_score(block: dict) -> float | None:
    if not block or not block.get("done"):
        return None
    vals = [block.get("energy"), block.get("focus"), block.get("mood")]
    if any(v is None for v in vals):
        return None
    return sum(vals) / 3.0


def day_mode(m: dict, n: dict, ni: dict) -> tuple[str, str, float | None]:
    """Return (mode_label, reason, day_avg)."""
    scores = [s for s in [avg_score(m), avg_score(n), avg_score(ni)] if s is not None]
    if not scores:
        return ("未判定", "まだ記録が足りないよ。朝だけでも入れてみてね。", None)

    day_avg = sum(scores) / len(scores)

    # ざっくり判定（分かりやすさ優先）
    if day_avg >= 7.0:
        return ("攻め", "エネルギー高め。前進タスクを1つ決めて踏み出せる日。", day_avg)
    if day_avg >= 4.5:
        return ("守り", "普通〜やや低め。小さく進めて、無理せず整える日。", day_avg)
    return ("回復", "低め。休養・整理・睡眠優先。回復こそ前進。", day_avg)


def to_dataframe(data):
    rows = []
    for e in data["entries"]:
        row = {"date": e.get("date"), "updated_at": e.get("updated_at")}
        for part in ["morning", "noon", "night"]:
            b = e.get(part, {})
            row[f"{part}_done"] = bool(b.get("done", False))
            row[f"{part}_energy"] = b.get("energy")
            row[f"{part}_focus"] = b.get("focus")
            row[f"{part}_mood"] = b.get("mood")
            row[f"{part}_note"] = b.get("note", "")
            row[f"{part}_saved_at"] = b.get("saved_at", "")
            row[f"{part}_avg"] = avg_score(b)
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df


def week_df(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    if df.empty:
        return df
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    w = df[df["date"] >= start].copy()
    w = w.sort_values("date", ascending=True)
    # 日平均（入ってる分だけ平均）
    w["day_avg"] = w[["morning_avg", "noon_avg", "night_avg"]].mean(axis=1, skipna=True)
    return w


def done_badge(done: bool) -> str:
    return "✅" if done else "⬜"


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="⚡", layout="wide")
st.title(f"⚡ {APP_TITLE}")
st.caption("朝・昼・夜の“状態”を測って、今日の勝ち筋（攻め/守り/回復）を決めるアプリ。")

data = load_data()
entry = get_or_create_today(data)

m = entry.get("morning", {})
n = entry.get("noon", {})
ni = entry.get("night", {})

mode, reason, day_avg = day_mode(m, n, ni)

with st.sidebar:
    st.subheader("📅 今日の状況")
    st.write(f"朝 {done_badge(bool(m.get('done')))} / 昼 {done_badge(bool(n.get('done')))} / 夜 {done_badge(bool(ni.get('done')))}")
    st.divider()
    st.subheader("🎯 今日のモード")
    if day_avg is None:
        st.write(f"**{mode}**")
    else:
        st.write(f"**{mode}**（平均 {day_avg:.1f}/10）")
    st.caption(reason)

    st.divider()
    st.subheader("💾 データ")
    st.code(DATA_PATH)
    df_all = to_dataframe(data)
    if st.button("📦 CSVでエクスポート"):
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSVをダウンロード", data=csv, file_name="day83_energy_meter.csv", mime="text/csv")

    st.divider()
    st.subheader("🧹 今日のリセット")
    if st.button("🗑️ 今日の朝・昼・夜を全部リセット", type="secondary"):
        entry["morning"] = {}
        entry["noon"] = {}
        entry["night"] = {}
        set_updated(entry)
        save_data(data)
        st.warning("今日の入力をリセットしたよ。必要ならもう一度入れてね。")


col1, col2 = st.columns([1.2, 0.8], gap="large")

with col1:
    st.subheader("🧪 入力（朝・昼・夜）")

    tabs = st.tabs(["☀️ 朝", "🕛 昼", "🌙 夜"])

    def part_form(part_key: str, title: str):
        block = entry.get(part_key, {})
        with st.form(f"{part_key}_form", clear_on_submit=False):
            st.markdown(f"**{title}：体力/集中/気分 を0〜10で入力**")

            energy = st.slider("体力（Energy）", 0, 10, int(block.get("energy", 5)))
            focus = st.slider("集中（Focus）", 0, 10, int(block.get("focus", 5)))
            mood = st.slider("気分（Mood）", 0, 10, int(block.get("mood", 5)))

            note = st.text_area("メモ（任意）", value=block.get("note", ""), placeholder="例：寝不足／運動した／嫌なことがあった など")

            submitted = st.form_submit_button("💾 保存して完了にする")
            if submitted:
                entry[part_key] = {
                    "energy": int(energy),
                    "focus": int(focus),
                    "mood": int(mood),
                    "note": note.strip(),
                    "done": True,
                    "saved_at": now_str(),
                }
                set_updated(entry)
                save_data(data)
                st.success(f"{title}を保存したよ。ナイス測定！")

        if block.get("done"):
            a = avg_score(block)
            if a is not None:
                st.info(f"保存済み：{block.get('saved_at','')}（平均 {a:.1f}/10）")
            else:
                st.info(f"保存済み：{block.get('saved_at','')}")

    with tabs[0]:
        part_form("morning", "☀️ 朝")
    with tabs[1]:
        part_form("noon", "🕛 昼")
    with tabs[2]:
        part_form("night", "🌙 夜")

    st.divider()
    st.subheader("🧭 今日のアドバイス（モード別）")
    if mode == "攻め":
        st.markdown("- **前進タスクを1つ**（30〜90分）\n- 連絡/作業/学習は“重め”でもOK\n- 仕上げより“着手”を重視")
    elif mode == "守り":
        st.markdown("- **小タスクを3つ**（各5〜15分）\n- 片付け・整理・軽い学習が勝ち\n- 無理に気合いで押さない")
    elif mode == "回復":
        st.markdown("- **睡眠・食事・入浴・散歩**が最優先\n- “やるなら”超軽いタスク1つ（5分）\n- 自分責め禁止。回復＝前進")
    else:
        st.markdown("- 朝だけでも入力すると、今日の方針が決まるよ。")


with col2:
    st.subheader("📈 直近7日グラフ")
    df_all = to_dataframe(data)
    w = week_df(df_all, days=7)

    if w.empty:
        st.write("まだデータが少ないよ。今日の朝から入れてみてね。")
    else:
        fig = plt.figure()
        plt.plot(w["date"], w["day_avg"], marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, 10)
        plt.xlabel("date")
        plt.ylabel("day average (0-10)")
        st.pyplot(fig)

        st.caption("日平均は、入力された時間帯（朝/昼/夜）の平均で計算してるよ。")

    st.divider()
    st.subheader("📚 過去ログ（最新順）")
    if df_all.empty:
        st.write("ログがないよ。")
    else:
        show_cols = [
            "date", "morning_done", "noon_done", "night_done",
            "morning_avg", "noon_avg", "night_avg"
        ]
        show_cols = [c for c in show_cols if c in df_all.columns]
        st.dataframe(df_all[show_cols], use_container_width=True, height=320)
