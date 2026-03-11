import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day91：AI人生コーチ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day91_ai_life_coach.json")


# ----------------------------
# storage
# ----------------------------
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
            "created_at": x.get("created_at"),
            "date": x.get("date"),
            "energy": x.get("energy"),
            "focus": x.get("focus"),
            "mood": x.get("mood"),
            "anxiety": x.get("anxiety"),
            "theme": x.get("theme"),
            "priority_action": x.get("priority_action"),
            "avoid_action": x.get("avoid_action"),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# coaching logic
# ----------------------------
def calc_mode(energy, focus, mood, anxiety):
    score = (energy + focus + mood) / 3 - (anxiety * 0.35)

    if score >= 6.5:
        return "攻め"
    elif score >= 3.8:
        return "守り"
    else:
        return "回復"


def coach_output(energy, focus, mood, anxiety, theme):
    mode = calc_mode(energy, focus, mood, anxiety)

    theme = (theme or "").strip()

    if mode == "攻め":
        coaching = (
            "今日は前に出られる日。完璧を狙うより、勢いを活かして"
            "“1つ形にする”ことを優先しよう。勢いがある日に着手できると、"
            "明日の自分がかなり楽になる。"
        )
        priority = "25分だけ、いま一番進めたい作業を触る"
        avoid = "細かい悩みで止まり続けること"
        luna = "ご主人、今日は進める日だよ。小さくでも着手したら勝ち。"

    elif mode == "守り":
        coaching = (
            "今日は整えながら進む日。大きな勝負より、"
            "小さな達成を積んで流れを作るほうが強い。"
            "“少しやる→終える”を繰り返そう。"
        )
        priority = "5〜15分で終わる小タスクを1つ片付ける"
        avoid = "一気に全部やろうとして固まること"
        luna = "ご主人、今日は丁寧に整えれば十分えらいよ。"

    else:
        coaching = (
            "今日は回復が最優先。休むことは後退じゃなく、"
            "次の一歩を守る行動。罪悪感を減らして、"
            "まず身体と心を静かに整えよう。"
        )
        priority = "休息か、5分で終わる超軽い行動を1つだけやる"
        avoid = "元気な日の基準で自分を責めること"
        luna = "ご主人、今日は守る日。回復も立派な前進だよ。"

    # テーマ別の一言補正
    if "開発" in theme or "アプリ" in theme or "python" in theme.lower():
        coaching += " 今日のテーマが開発なら、“新機能”より“1か所改善”が安定。"
    elif "収益" in theme or "お金" in theme:
        coaching += " 収益テーマの日は、“売れるか悩む”より“形にして見せる”を優先しよう。"
    elif "家族" in theme or "育児" in theme:
        coaching += " 家族テーマの日は、家族対応そのものを“今日の成果”に含めてOK。"
    elif "発信" in theme or "note" in theme.lower() or "ブログ" in theme:
        coaching += " 発信テーマの日は、完成よりも“タイトルと導入だけ”で十分前進。"

    return {
        "mode": mode,
        "coaching": coaching,
        "priority_action": priority,
        "avoid_action": avoid,
        "luna_message": luna,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🧠", layout="wide")
st.title("🧠 Day91：AI人生コーチ")
st.caption("今日の状態をもとに、コーチングと優先行動を返すアプリ。まずは確実に動く版。")

data = load_data()

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day91_ai_life_coach.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.subheader("今日の状態を入力")

    energy = st.slider("エネルギー", 0, 10, 5)
    focus = st.slider("集中", 0, 10, 5)
    mood = st.slider("気分", 0, 10, 5)
    anxiety = st.slider("不安度", 0, 10, 3)

    theme = st.text_input(
        "今日のテーマ",
        placeholder="例：アプリ開発 / 収益化 / 家族 / 発信 / 回復"
    )

    memo = st.text_area(
        "ひとこと相談メモ",
        placeholder="例：眠い。けど何か進めたい。焦りもある。"
    )

    if st.button("コーチングを受ける", type="primary"):
        result = coach_output(energy, focus, mood, anxiety, theme)

        log = {
            "created_at": now_str(),
            "date": today_str(),
            "energy": energy,
            "focus": focus,
            "mood": mood,
            "anxiety": anxiety,
            "theme": theme.strip(),
            "memo": memo.strip(),
            "mode": result["mode"],
            "coaching": result["coaching"],
            "priority_action": result["priority_action"],
            "avoid_action": result["avoid_action"],
            "luna_message": result["luna_message"],
        }

        data["logs"].append(log)
        save_data(data)
        st.session_state["latest_result"] = log
        st.rerun()

with right:
    st.subheader("今日のコーチング結果")

    latest = st.session_state.get("latest_result")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        mode_label = latest["mode"]
        if mode_label == "攻め":
            st.success(f"現在モード：{mode_label}")
        elif mode_label == "守り":
            st.info(f"現在モード：{mode_label}")
        else:
            st.warning(f"現在モード：{mode_label}")

        st.markdown("### コーチング")
        st.write(latest["coaching"])

        st.markdown("### 今日の優先行動")
        st.success(latest["priority_action"])

        st.markdown("### 今日やらないこと")
        st.error(latest["avoid_action"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna_message"])
    else:
        st.write("まだ診断していないよ。左で入力してみてね。")

st.divider()
st.subheader("履歴")

df_all = to_df(data)
if df_all.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(df_all, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        picked = st.selectbox("日時を選んでね", options=df_all["created_at"].tolist())
        chosen = None
        for row in data["logs"]:
            if row["created_at"] == picked:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['created_at']}")
            st.write(f"テーマ：{chosen.get('theme', '')}")
            st.write(f"相談メモ：{chosen.get('memo', '')}")
            st.write(f"モード：{chosen.get('mode', '')}")
            st.write("**コーチング**")
            st.write(chosen.get("coaching", ""))
            st.write("**優先行動**")
            st.success(chosen.get("priority_action", ""))
            st.write("**やらないこと**")
            st.error(chosen.get("avoid_action", ""))
            st.write("**ルナのひとこと**")
            st.info(chosen.get("luna_message", ""))
