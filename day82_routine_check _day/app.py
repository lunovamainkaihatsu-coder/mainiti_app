import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day82：Routine Check（朝・昼・夜版 C）"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "routine_check.json")


# ---------- utils ----------
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


def to_dataframe(data):
    rows = []
    for e in data["entries"]:
        base = {
            "date": e.get("date"),
            "created_at": e.get("created_at"),
            "updated_at": e.get("updated_at"),
        }

        def pick(block, prefix):
            return {
                f"{prefix}_goal": block.get("goal", ""),
                f"{prefix}_identity": block.get("identity", ""),
                f"{prefix}_emotion": block.get("emotion", ""),
                f"{prefix}_most_important": block.get("most_important", ""),
                f"{prefix}_state_yesno": block.get("state_yesno", ""),
                f"{prefix}_fix_words": block.get("fix_words", ""),
                f"{prefix}_progress": block.get("progress", ""),
                f"{prefix}_approval": block.get("approval", ""),
                f"{prefix}_future_fix": block.get("future_fix", ""),
                f"{prefix}_note": block.get("note", ""),
                f"{prefix}_done": bool(block.get("done", False)),
                f"{prefix}_saved_at": block.get("saved_at", ""),
            }

        row = {}
        row.update(base)
        row.update(pick(e.get("morning", {}), "morning"))
        row.update(pick(e.get("noon", {}), "noon"))
        row.update(pick(e.get("night", {}), "night"))
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df


def done_badge(done: bool) -> str:
    return "✅ 完了" if done else "⬜ 未完了"


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")
st.title(f"🌙 {APP_TITLE}")
st.caption("ご主人の“成功状態”を1日3回で整えるアプリ（ローカル保存）")

data = load_data()
entry = get_or_create_today(data)

# sidebar summary
with st.sidebar:
    st.subheader("📅 今日の状況")
    m_done = bool(entry.get("morning", {}).get("done", False))
    n_done = bool(entry.get("noon", {}).get("done", False))
    ni_done = bool(entry.get("night", {}).get("done", False))

    st.write(f"朝：{done_badge(m_done)}")
    st.write(f"昼：{done_badge(n_done)}")
    st.write(f"夜：{done_badge(ni_done)}")

    st.divider()
    st.subheader("💾 データ")
    st.code(DATA_PATH)
    if st.button("📦 CSVでエクスポート"):
        df = to_dataframe(data)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVをダウンロード",
            data=csv,
            file_name="routine_check.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("⚠️ 注意")
    st.write("これはローカル保存です。端末を変えるとデータは移りません。")


# ---------- forms ----------
col1, col2 = st.columns([1.15, 0.85], gap="large")

with col1:
    st.subheader("🟡 今日の入力（朝・昼・夜）")

    tabs = st.tabs(["☀️ 朝（起動）", "🕛 昼（修正）", "🌙 夜（固定）"])

    # ---- Morning ----
    with tabs[0]:
        block = entry.get("morning", {})
        with st.form("morning_form", clear_on_submit=False):
            st.markdown("**目的：成功者として1日を開始する**")

            goal = st.text_area("① 目標確認（30秒）", value=block.get("goal", ""),
                                placeholder="例：ルナを現実にする／資産を築く／自由な人生…")
            identity = st.text_area("② 自己定義（30秒）", value=block.get("identity", ""),
                                    placeholder="例：自分は成功者／創造者／正しい道にいる…")
            emotion = st.text_input("③ 感情設定（30秒）", value=block.get("emotion", ""),
                                    placeholder="例：落ち着き／自信／流れに乗っている")
            most_important = st.text_input("④ 今日の最重要行動（30秒・1つ）", value=block.get("most_important", ""),
                                           placeholder="例：ブログを書く／アプリを進める／学ぶ…")
            note = st.text_area("メモ（任意）", value=block.get("note", ""))

            submitted = st.form_submit_button("💾 朝を保存して完了にする")
            if submitted:
                entry["morning"] = {
                    "goal": goal.strip(),
                    "identity": identity.strip(),
                    "emotion": emotion.strip(),
                    "most_important": most_important.strip(),
                    "note": note.strip(),
                    "done": True,
                    "saved_at": now_str(),
                }
                set_updated(entry)
                save_data(data)
                st.success("朝のRoutine Checkを保存したよ。いい起動！🌞")

        if block.get("done"):
            st.info(f"保存済み：{block.get('saved_at','')}")


    # ---- Noon ----
    with tabs[1]:
        block = entry.get("noon", {})
        with st.form("noon_form", clear_on_submit=False):
            st.markdown("**目的：ズレを修正し、成功状態に戻る**")

            state_yesno = st.radio(
                "① 今の自分は“成功者の状態”？（YES/NO）",
                options=["YES", "NO"],
                index=0 if block.get("state_yesno", "YES") == "YES" else 1,
                horizontal=True
            )
            fix_words = st.text_area(
                "② ズレていたら修正（言葉で戻す）",
                value=block.get("fix_words", ""),
                placeholder="例：大丈夫、すべて順調／自分は正しい道にいる／流れは来ている…"
            )
            goal_recheck = st.text_input(
                "③ 目標を再確認（10秒）",
                value=block.get("goal", ""),
                placeholder="今の方向（短く）"
            )
            note = st.text_area("メモ（任意）", value=block.get("note", ""))

            submitted = st.form_submit_button("💾 昼を保存して完了にする")
            if submitted:
                entry["noon"] = {
                    "state_yesno": state_yesno,
                    "fix_words": fix_words.strip(),
                    "goal": goal_recheck.strip(),
                    "note": note.strip(),
                    "done": True,
                    "saved_at": now_str(),
                }
                set_updated(entry)
                save_data(data)
                st.success("昼のRoutine Checkを保存したよ。ズレ修正、えらい。🕛")

        if block.get("done"):
            st.info(f"保存済み：{block.get('saved_at','')}")


    # ---- Night ----
    with tabs[2]:
        block = entry.get("night", {})
        with st.form("night_form", clear_on_submit=False):
            st.markdown("**目的：成功者として1日を完了させる**")

            progress = st.text_area(
                "① 今日の前進（小さくてOK）",
                value=block.get("progress", ""),
                placeholder="例：学んだ／考えた／休んだ（回復も前進）…"
            )
            approval = st.text_area(
                "② 自分を承認する言葉",
                value=block.get("approval", ""),
                placeholder="例：よくやった／確実に進んでいる／自分は成長している…"
            )
            future_fix = st.text_area(
                "③ 未来を固定（数秒のイメージ＋言語化）",
                value=block.get("future_fix", ""),
                placeholder="例：成功して安心している自分／満たされている生活…"
            )
            note = st.text_area("メモ（任意）", value=block.get("note", ""))

            submitted = st.form_submit_button("💾 夜を保存して完了にする")
            if submitted:
                entry["night"] = {
                    "progress": progress.strip(),
                    "approval": approval.strip(),
                    "future_fix": future_fix.strip(),
                    "note": note.strip(),
                    "done": True,
                    "saved_at": now_str(),
                }
                set_updated(entry)
                save_data(data)
                st.success("夜のRoutine Checkを保存したよ。今日を勝ちで閉じたね。🌙")

        if block.get("done"):
            st.info(f"保存済み：{block.get('saved_at','')}")


with col2:
    st.subheader("📚 過去ログ")
    df = to_dataframe(data)

    if df.empty:
        st.write("まだログがないよ。今日の朝から入れてみてね。")
    else:
        st.caption("最新の日付が上に表示されるよ。")
        show_cols = [
            "date",
            "morning_done", "noon_done", "night_done",
            "morning_most_important",
            "noon_state_yesno",
            "night_progress",
            "updated_at"
        ]
        # 列が無い場合でも落ちないように
        show_cols = [c for c in show_cols if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, height=420)

        with st.expander("🔎 1日分を詳細表示"):
            pick = st.selectbox("日付を選んでね", options=df["date"].tolist())
            e = find_entry(data, pick)
            if e:
                st.markdown(f"### {pick}")
                st.write(f"作成：{e.get('created_at','')} / 更新：{e.get('updated_at','')}")
                st.divider()

                def render_block(title, b):
                    st.markdown(f"**{title}**")
                    if not b:
                        st.write("（未入力）")
                        return
                    st.write(f"状態：{done_badge(bool(b.get('done', False)))} / 保存：{b.get('saved_at','')}")
                    for k, label in [
                        ("goal", "目標"),
                        ("identity", "自己定義"),
                        ("emotion", "感情"),
                        ("most_important", "最重要行動"),
                        ("state_yesno", "成功者の状態？"),
                        ("fix_words", "修正の言葉"),
                        ("progress", "前進"),
                        ("approval", "承認"),
                        ("future_fix", "未来固定"),
                        ("note", "メモ"),
                    ]:
                        if b.get(k):
                            st.markdown(f"- **{label}**：{b.get(k)}")

                render_block("☀️ 朝（起動）", e.get("morning", {}))
                st.divider()
                render_block("🕛 昼（修正）", e.get("noon", {}))
                st.divider()
                render_block("🌙 夜（固定）", e.get("night", {}))

    st.divider()
    st.subheader("🧹 今日のリセット")
    st.caption("間違えて入力したとき用（今日だけ）")
    if st.button("🗑️ 今日の朝・昼・夜を全部リセット", type="secondary"):
        entry["morning"] = {}
        entry["noon"] = {}
        entry["night"] = {}
        set_updated(entry)
        save_data(data)
        st.warning("今日の入力をリセットしたよ。必要ならもう一度入れてね。")
