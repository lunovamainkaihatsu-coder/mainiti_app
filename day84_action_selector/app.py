import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd

APP_TITLE = "Day84：Action Selector（今日やるべき1つ）"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day84_action_selector.json")


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


def today_key():
    return date.today().isoformat()


def now_str():
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
            "mode": "未判定",
            "scores": {"energy": None, "focus": None, "mood": None},
            "selected_action": "",
            "selected_category": "",
            "why_this": "",
            "done": False,
            "review": "",
            "saved_at": "",
            "done_at": "",
        }
        data["entries"].append(e)
        save_data(data)
    return e


def touch(entry):
    entry["updated_at"] = now_str()


# ---------- logic ----------
def mode_from_scores(energy: int, focus: int, mood: int) -> tuple[str, float]:
    avg = (energy + focus + mood) / 3.0
    if avg >= 7.0:
        return "攻め", avg
    if avg >= 4.5:
        return "守り", avg
    return "回復", avg


ACTION_POOLS = {
    "攻め": [
        ("開発", "Day83/Day84を30分改善（UI/機能1つ）"),
        ("発信", "Note記事の見出し→導入だけ書く（15分）"),
        ("学習", "Python/Streamlitを1テーマだけ学ぶ（20分）"),
        ("整理", "タスク棚卸し→今日の最優先を決める（10分）"),
        ("家族", "家の用事を1つ片付けて心を軽くする（10分）"),
    ],
    "守り": [
        ("整理", "机の上を5分だけ片付ける"),
        ("学習", "軽い読書 or 動画を10分だけ"),
        ("発信", "一言投稿（気づき/学び/日記）を書くだけ"),
        ("開発", "バグ修正 or 1行改善だけやる"),
        ("回復", "ストレッチ＋水分補給＋深呼吸"),
    ],
    "回復": [
        ("回復", "睡眠/仮眠/横になる（最優先）"),
        ("回復", "入浴 or 温かい飲み物で整える"),
        ("整理", "“やらないこと”を3つ決めて脳を軽くする"),
        ("家族", "家族対応を“優先タスク”として認める（罪悪感0）"),
        ("超軽", "5分だけ：メモ1行 or タイトルだけ作る"),
    ],
}


def build_suggestions(mode: str, user_goals: list[str]) -> list[tuple[str, str]]:
    base = ACTION_POOLS.get(mode, [])
    # ゴールに寄せて軽く最適化（順序を少しだけ変える）
    # 例：ルナ/アプリ/発信が含まれるなら関連カテゴリを上へ
    boost_keywords = " ".join(user_goals).lower()

    def score(item):
        cat, text = item
        s = 0
        if any(k in boost_keywords for k in ["ルナ", "luna", "アプリ", "streamlit", "開発"]):
            if cat == "開発":
                s += 2
        if any(k in boost_keywords for k in ["note", "ブログ", "発信", "記事"]):
            if cat == "発信":
                s += 2
        if any(k in boost_keywords for k in ["勉強", "学習", "python"]):
            if cat == "学習":
                s += 1
        if mode == "回復" and cat in ["回復", "超軽"]:
            s += 1
        return -s  # smaller is higher priority

    return sorted(base, key=score)


def to_df(data):
    rows = []
    for e in data["entries"]:
        rows.append({
            "date": e.get("date"),
            "mode": e.get("mode"),
            "energy": e.get("scores", {}).get("energy"),
            "focus": e.get("scores", {}).get("focus"),
            "mood": e.get("scores", {}).get("mood"),
            "selected_category": e.get("selected_category"),
            "selected_action": e.get("selected_action"),
            "why_this": e.get("why_this"),
            "done": bool(e.get("done", False)),
            "review": e.get("review", ""),
            "updated_at": e.get("updated_at", ""),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="🎯", layout="wide")
st.title(f"🎯 {APP_TITLE}")
st.caption("“迷い”を消して、今日の最重要1つを決める。決めたら勝ち。")

data = load_data()
entry = get_or_create_today(data)

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if st.button("📦 CSVでエクスポート"):
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSVをダウンロード", data=csv, file_name="day84_action_selector.csv", mime="text/csv")

    st.divider()
    st.subheader("🧹 今日のリセット")
    if st.button("🗑️ 今日の選択をリセット", type="secondary"):
        entry["selected_action"] = ""
        entry["selected_category"] = ""
        entry["why_this"] = ""
        entry["done"] = False
        entry["review"] = ""
        entry["saved_at"] = ""
        entry["done_at"] = ""
        touch(entry)
        save_data(data)
        st.warning("今日の選択をリセットしたよ。")


col1, col2 = st.columns([1.15, 0.85], gap="large")

with col1:
    st.subheader("① 今日の状態を決める")

    mode_choice = st.radio(
        "モードの決め方",
        options=["スコアから自動判定（おすすめ）", "手動で選ぶ"],
        horizontal=True
    )

    if mode_choice.startswith("スコア"):
        c1, c2, c3 = st.columns(3)
        with c1:
            energy = st.slider("体力", 0, 10, int(entry["scores"]["energy"] if entry["scores"]["energy"] is not None else 5))
        with c2:
            focus = st.slider("集中", 0, 10, int(entry["scores"]["focus"] if entry["scores"]["focus"] is not None else 5))
        with c3:
            mood = st.slider("気分", 0, 10, int(entry["scores"]["mood"] if entry["scores"]["mood"] is not None else 5))

        mode, avg = mode_from_scores(energy, focus, mood)
        st.info(f"今日のモード：**{mode}**（平均 {avg:.1f}/10）")

        entry["mode"] = mode
        entry["scores"] = {"energy": int(energy), "focus": int(focus), "mood": int(mood)}
    else:
        mode = st.selectbox("今日のモードを選んでね", options=["攻め", "守り", "回復"], index=0)
        entry["mode"] = mode

    st.divider()
    st.subheader("② 今日の“優先テーマ”を入れる（任意）")
    st.caption("入力すると提案が少しだけ“ご主人寄り”に並び替わるよ。")

    default_goals = ["ルナ/アプリ開発", "Note/ブログ発信", "学習（Python/AI）"]
    goals = st.multiselect("優先テーマ", options=default_goals, default=default_goals)

    suggestions = build_suggestions(entry["mode"], goals)

    st.divider()
    st.subheader("③ 今日やる“たった1つ”を選ぶ")

    option_labels = [f"[{cat}] {text}" for cat, text in suggestions]
    picked = st.radio("おすすめから1つ選んでね", options=option_labels, index=0)

    picked_cat, picked_text = suggestions[option_labels.index(picked)]
    why = st.text_area("なぜこれを選ぶ？（1行でOK）", value=entry.get("why_this", ""), placeholder="例：今日は守り。小さく進めて自己効力感を戻す")

    if st.button("✅ 今日の最重要1つとして保存", type="primary"):
        entry["selected_category"] = picked_cat
        entry["selected_action"] = picked_text
        entry["why_this"] = why.strip()
        entry["saved_at"] = now_str()
        touch(entry)
        save_data(data)
        st.success("保存したよ。あとは“やるだけ”だね。")

    st.divider()
    st.subheader("④ 夜：達成チェック（締め）")
    st.caption("できた/できなかった、どっちでもOK。記録が習慣を作る。")

    done = st.checkbox("今日の“最重要1つ”をやれた", value=bool(entry.get("done", False)))
    review = st.text_area("ひとこと振り返り（任意）", value=entry.get("review", ""), placeholder="例：5分でも手を付けたから勝ち。明日は朝にやる。")

    if st.button("🌙 今日を締めて保存"):
        entry["done"] = bool(done)
        entry["review"] = review.strip()
        entry["done_at"] = now_str()
        touch(entry)
        save_data(data)
        st.success("今日を締めたよ。積み上げ完了。")


with col2:
    st.subheader("📌 今日のカード")
    if entry.get("selected_action"):
        st.markdown(f"### {entry['date']}")
        st.markdown(f"- モード：**{entry.get('mode','未判定')}**")
        st.markdown(f"- 今日の最重要：**[{entry.get('selected_category')}] {entry.get('selected_action')}**")
        if entry.get("why_this"):
            st.markdown(f"- 理由：{entry.get('why_this')}")
        st.markdown(f"- 保存：{entry.get('saved_at','')}")
        st.markdown(f"- 達成：{'✅' if entry.get('done') else '⬜'}")
        if entry.get("done_at"):
            st.markdown(f"- 締め：{entry.get('done_at')}")
    else:
        st.info("まだ“今日の最重要1つ”が決まってないよ。左で選んで保存してね。")

    st.divider()
    st.subheader("📚 過去ログ")
    df_all = to_df(data)
    if df_all.empty:
        st.write("まだログがないよ。")
    else:
        st.dataframe(df_all[["date", "mode", "selected_category", "selected_action", "done"]], use_container_width=True, height=360)
