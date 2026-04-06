import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day103：きっかけボタン"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day103_kikkake_button.json")

TRIGGERS = {
    "やさしく": [
        {
            "title": "まずは呼吸から",
            "message": "いま全部やらなくていいよ。まずは呼吸を1回整えよ。",
            "action": "深呼吸を3回する",
            "luna": "ご主人、始める前にちょっとだけ落ち着こっか。"
        },
        {
            "title": "1行だけでいい",
            "message": "完璧じゃなくていい。1行書けたら今日は前進。",
            "action": "メモを1行だけ書く",
            "luna": "1行って、小さく見えて案外すごいんだよ。"
        },
        {
            "title": "ここに来た時点で再起動",
            "message": "押した時点で、もう止まりっぱなしじゃないよ。",
            "action": "次にやることを1つだけ決める",
            "luna": "ちゃんと戻ってきたね、ご主人。えらい。"
        },
    ],
    "ふつう": [
        {
            "title": "5分だけ着手",
            "message": "やる気を待たず、5分だけ始めよう。",
            "action": "5分だけ作業する",
            "luna": "ご主人、最初の5分を超えると流れ変わるかも。"
        },
        {
            "title": "1ファイル開く",
            "message": "完成はまだ先でいい。まず触れよう。",
            "action": "アプリかメモ帳を1つ開く",
            "luna": "開くだけでも“着手”だよ。十分強い。"
        },
        {
            "title": "後回しに接触",
            "message": "終わらせなくていい。触るだけでいい。",
            "action": "後回しを1つだけ開いて見る",
            "luna": "ゼロ距離より、一歩近づくだけで全然違うよ。"
        },
    ],
    "強め": [
        {
            "title": "迷う前に動く",
            "message": "考えすぎ終了。まず1操作しよう。",
            "action": "今すぐ1クリックか1入力する",
            "luna": "ご主人、今日は“考える”より“触る”でいこう。"
        },
        {
            "title": "小さく進軍",
            "message": "気分はあとでついてくる。先に前へ。",
            "action": "25分タイマーをセットする",
            "luna": "いけるいける。最初の一歩だけ踏み出そ。"
        },
        {
            "title": "今日はゼロで終わらせない",
            "message": "大きな成果はいらない。ゼロ回避が勝ち。",
            "action": "今日の進捗を1つ作る",
            "luna": "ご主人、ほんの少しでも積めたら今日は勝ちだよ。"
        },
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
            "id": x["id"],
            "created_at": x["created_at"],
            "mode": x["mode"],
            "title": x["title"],
            "action": x["action"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def draw_trigger(mode: str):
    item = random.choice(TRIGGERS[mode])
    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mode": mode,
        "title": item["title"],
        "message": item["message"],
        "action": item["action"],
        "luna": item["luna"],
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🔘", layout="wide")
st.title("🔘 Day103：きっかけボタン")
st.caption("動けない時に押して、最初の一歩を受け取るための軽めアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day103_kikkake_button.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([0.95, 1.05], gap="large")

with left:
    st.subheader("きっかけを受け取る")

    mode = st.radio("モード", ["やさしく", "ふつう", "強め"], horizontal=True)

    if st.button("🔘 きっかけボタンを押す", type="primary"):
        result = draw_trigger(mode)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日のきっかけ")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["mode"] == "やさしく":
            st.success(f"モード：{latest['mode']}")
        elif latest["mode"] == "ふつう":
            st.info(f"モード：{latest['mode']}")
        else:
            st.warning(f"モード：{latest['mode']}")

        st.markdown(f"### {latest['title']}")
        st.write(latest["message"])

        st.markdown("**今日の小さな行動**")
        st.success(latest["action"])

        st.markdown("**ルナのひとこと**")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
                    break
            save_data(data)
            st.toast("お気に入り更新！")
    else:
        st.write("まだ押してないよ。左のボタンからどうぞ。")

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
            st.markdown(f"### {chosen['title']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"モード：{chosen['mode']}")
            st.write("**メッセージ**")
            st.write(chosen["message"])
            st.write("**今日の小さな行動**")
            st.success(chosen["action"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
