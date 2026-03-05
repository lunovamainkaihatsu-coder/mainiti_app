import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd

APP_TITLE = "Day88：Life Level System（XP）"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day88_life_level.json")


# ---------- storage ----------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"days": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_key():
    return date.today().isoformat()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_day(data, dkey):
    for d in data["days"]:
        if d["date"] == dkey:
            return d
    return None


def get_or_create_today(data):
    dkey = today_key()
    d = find_day(data, dkey)
    if d is None:
        d = {
            "date": dkey,
            "created_at": now_str(),
            "updated_at": now_str(),
            "tasks": [],
            "bonus": {"streak_bonus": 0, "notes": ""},
            "total_xp": 0
        }
        data["days"].append(d)
        save_data(data)
    return d


def touch(day):
    day["updated_at"] = now_str()


# ---------- XP rules ----------
TASKS = [
    # (category, label, xp)
    ("開発", "コードを書く（15分）", 30),
    ("開発", "アプリ改善（UI/機能1つ）", 50),
    ("発信", "Note/ブログを投稿", 60),
    ("発信", "下書きだけ書く（10分）", 25),
    ("学習", "学習（20分）", 35),
    ("学習", "本を読む（10分）", 20),
    ("健康", "散歩/運動（10分）", 25),
    ("健康", "睡眠を優先した", 20),
    ("家族", "家族の用事を優先して支えた", 25),
    ("片付け", "片付け（5分）", 15),
    ("回復", "メンタルケア（深呼吸/入浴/休息）", 20),
    ("回復", "“自分責めしない”を守った", 10),
]

LEVEL_STEP = 200  # 1レベルに必要なXP（シンプルで分かりやすい）


def calc_level(total_xp: int):
    level = total_xp // LEVEL_STEP + 1
    into = total_xp % LEVEL_STEP
    pct = into / LEVEL_STEP
    return level, into, pct


def streak_days(dates: list[str]) -> int:
    """Compute current streak ending today (or ending at latest date if today missing)."""
    if not dates:
        return 0
    ds = sorted({date.fromisoformat(x) for x in dates})
    last = ds[-1]
    streak = 1
    for i in range(len(ds) - 2, -1, -1):
        if (last - ds[i]).days == 1:
            streak += 1
            last = ds[i]
        else:
            break
    # If today isn't the latest date, streak still computed from latest date in data.
    return streak


def to_df(data):
    rows = []
    for d in data["days"]:
        rows.append({
            "date": d["date"],
            "xp": d.get("total_xp", 0),
            "task_count": len(d.get("tasks", [])),
            "notes": d.get("bonus", {}).get("notes", ""),
            "updated_at": d.get("updated_at", "")
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="🆙", layout="wide")
st.title("🆙 Day88：Life Level System（XP）")
st.caption("人生をゲームにする。やった分だけレベルが上がる。")

data = load_data()
today = get_or_create_today(data)

# Sidebar: totals
df_all = to_df(data)
total_xp = int(df_all["xp"].sum()) if not df_all.empty else 0
level, into, pct = calc_level(total_xp)

with st.sidebar:
    st.subheader("📈 ステータス")
    st.metric("累計XP", total_xp)
    st.metric("レベル", level)
    st.progress(pct, text=f"次のレベルまで：{LEVEL_STEP - into} XP")

    dates_done = [d["date"] for d in data["days"] if int(d.get("total_xp", 0)) > 0]
    st.metric("連続記録（streak）", streak_days(dates_done))

    st.divider()
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    if st.button("📦 CSVでエクスポート"):
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSVをダウンロード", data=csv, file_name="day88_life_level.csv", mime="text/csv")

    st.divider()
    st.subheader("🧹 今日のリセット")
    if st.button("🗑️ 今日のXPをリセット", type="secondary"):
        today["tasks"] = []
        today["bonus"] = {"streak_bonus": 0, "notes": ""}
        today["total_xp"] = 0
        touch(today)
        save_data(data)
        st.warning("今日のXPをリセットしたよ。")
        st.rerun()


col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("✅ 今日のクエスト（チェックするだけ）")

    # Current checked set
    current = set(today.get("tasks", []))

    # Group by category
    categories = sorted(set([c for c, _, _ in TASKS]))
    selected = set()

    for cat in categories:
        st.markdown(f"### {cat}")
        for c, label, xp in [t for t in TASKS if t[0] == cat]:
            key = f"{cat}|{label}|{xp}"
            checked = key in current
            if st.checkbox(f"{label} (+{xp}XP)", value=checked, key=key):
                selected.add(key)

    st.divider()
    st.subheader("🎁 ボーナス")
    notes = st.text_area("ひとこと（任意）", value=today.get("bonus", {}).get("notes", ""),
                         placeholder="例：回復できた。明日は朝に15分だけコード。")

    # Save
    if st.button("💾 今日のXPを保存", type="primary"):
        today["tasks"] = sorted(list(selected))
        today["bonus"]["notes"] = notes.strip()
        # XP calc
        xp_sum = 0
        for key in today["tasks"]:
            try:
                xp_sum += int(key.split("|")[-1])
            except Exception:
                pass
        today["total_xp"] = xp_sum
        touch(today)
        save_data(data)
        st.success(f"保存した！ 今日のXP：{xp_sum}")
        st.rerun()

with col2:
    st.subheader("📅 直近7日（XP推移）")
    if df_all.empty:
        st.info("まだデータがないよ。今日チェックしてXPを貯めよう。")
    else:
        start = (date.today() - timedelta(days=6)).isoformat()
        w = df_all[df_all["date"] >= start].copy()
        w = w.sort_values("date", ascending=True)
        if w.empty:
            st.info("直近7日分のデータがまだないよ。")
        else:
            chart_df = w.set_index("date")[["xp"]]
            st.line_chart(chart_df)

    st.divider()
    st.subheader("📚 ログ（最新順）")
    if df_all.empty:
        st.write("ログがないよ。")
    else:
        st.dataframe(df_all[["date", "xp", "task_count"]], use_container_width=True, height=320)
