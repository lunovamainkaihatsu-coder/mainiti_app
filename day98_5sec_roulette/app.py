import streamlit as st
import json
import os
import random
import time
from datetime import datetime
import pandas as pd

APP_TITLE = "Day98：5秒ルーレット"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day98_5sec_roulette.json")

TASKS = {
    "通常": [
        ("水をひとくち飲む", "それだけでも流れが変わることあるよ。"),
        ("深呼吸を3回する", "呼吸を整えると、心も少し戻ってくるよ。"),
        ("机の上を1か所だけ整える", "小さな整理って、思ったより効くんだよね。"),
        ("今日やることを1行だけ書く", "1行で十分。見える化は強いよ。"),
        ("肩を回して体をほぐす", "体がゆるむと、気持ちも少しゆるむよ。"),
    ],
    "回復": [
        ("目を閉じて30秒休む", "今日は守ることが大事な日かも。"),
        ("温かい飲み物を用意する", "落ち着く準備って、立派な行動だよ。"),
        ("“今日はこれでいい”と1回つぶやく", "自分を許すのも大事な力だよ。"),
        ("スマホを置いて5秒ぼーっとする", "情報を止めるだけで楽になる時あるよ。"),
        ("楽な姿勢に座り直す", "まず身体から整えよっか。"),
    ],
    "前進": [
        ("5分だけ作業を始める", "始めると流れが変わること、多いよ。"),
        ("次のアプリ名を1つ考える", "小さな発想も、未来の種だよ。"),
        ("メモ帳を開いて1行書く", "1行でいい。ゼロじゃなくなるから。"),
        ("1ファイルだけ開く", "開くだけでも着手だよ。十分えらい。"),
        ("後回しを1つだけ触る", "完了じゃなくて接触でOK。"),
    ],
}


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


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x.get("id"),
            "created_at": x.get("created_at"),
            "mode": x.get("mode"),
            "task": x.get("task"),
            "comment": x.get("comment"),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def roll_task(mode: str):
    task, comment = random.choice(TASKS[mode])
    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mode": mode,
        "task": task,
        "comment": comment,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🎯", layout="wide")
st.title("🎯 Day98：5秒ルーレット")
st.caption("5秒後に、今日の超軽タスクが1つ出るお遊び系アプリ。")

data = load_data()

if "latest_result" not in st.session_state:
    st.session_state["latest_result"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day98_5sec_roulette.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest_result"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([0.95, 1.05], gap="large")

with left:
    st.subheader("ルーレットを回す")

    mode = st.radio("モード", ["通常", "回復", "前進"], horizontal=True)

    if st.button("🎲 5秒ルーレット開始", type="primary"):
        countdown_area = st.empty()
        for i in range(5, 0, -1):
            countdown_area.markdown(f"## {i}...")
            time.sleep(1)
        countdown_area.markdown("## ✨ 決定！")

        result = roll_task(mode)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest_result"] = result
        st.rerun()

with right:
    st.subheader("今回の結果")

    latest = st.session_state.get("latest_result")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["mode"] == "通常":
            st.info(f"モード：{latest['mode']}")
        elif latest["mode"] == "回復":
            st.warning(f"モード：{latest['mode']}")
        else:
            st.success(f"モード：{latest['mode']}")

        st.markdown("### 今日の超軽タスク")
        st.success(latest["task"])

        st.markdown("### ルナのひとこと")
        st.write(latest["comment"])

        fav = st.checkbox("⭐ お気に入りにする", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row.get("id") == latest.get("id"):
                    row["favorite"] = fav
                    break
            save_data(data)
            st.toast("お気に入り更新！")
    else:
        st.write("まだ回してないよ。左のボタンを押してみてね。")

st.divider()
st.subheader("履歴")

df_all = to_df(data)
if df_all.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ お気に入りだけ表示", value=False)
    view = df_all.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        pick_id = st.selectbox("結果を選んでね", options=view["id"].tolist())
        chosen = None
        for row in data["logs"]:
            if row["id"] == pick_id:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['created_at']}")
            st.write(f"モード：{chosen['mode']}")
            st.write("**タスク**")
            st.success(chosen["task"])
            st.write("**ルナのひとこと**")
            st.info(chosen["comment"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
