import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
import random

APP_TITLE = "Day131：ルナの作戦会議室"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day131_luna_strategy_room.json")

MODES = ["攻め", "守り", "回復", "整理", "遊び"]

LUNA_COMMENTS = {
    "攻め": [
        "ご主人、今日は少し前に出られそう。最優先を1つに絞って進もう。",
        "今日は“形にする”を意識していい日かも。小さくても成果を残そう。"
    ],
    "守り": [
        "今日は無理に攻めなくていいよ。整えながら、1つだけ進めよう。",
        "守りの日は、崩れないことが勝ち。小さく安定させよう。"
    ],
    "回復": [
        "ご主人、今日は回復も作戦のうち。自分を責めずに戻す日だよ。",
        "今日は休むことも任務。小さな行動だけで十分。"
    ],
    "整理": [
        "頭の中を整えると、次の一手が見えやすくなるよ。",
        "今日は片付け・メモ・分類が強い日。ごちゃごちゃを少し減らそう。"
    ],
    "遊び": [
        "遊びも大事な燃料だよ。楽しいことを1つ混ぜていこう。",
        "ご主人、今日は軽さを味方にしよう。楽しい一手で流れを作ろう。"
    ],
}


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"plans": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["plans"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "mode": x["mode"],
            "main_goal": x["main_goal"],
            "priority_action": x["priority_action"],
            "status": x.get("status", "未完了"),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🧭", layout="wide")
st.title("🧭 Day131：ルナの作戦会議室")
st.caption("今日の最優先・やらないこと・ごほうび・振り返りを決めるアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の作戦を立てる")

    mode = st.radio("今日のモード", MODES, horizontal=True)

    main_goal = st.text_input(
        "今日の目的",
        placeholder="例：少しでも前に進む / 体を休める / アプリを1つ作る"
    )

    priority_action = st.text_input(
        "最優先の1つ",
        placeholder="例：Day131をGitHubにpushする"
    )

    do_not = st.text_area(
        "今日はやらないこと",
        placeholder="例：完璧主義で止まらない / YouTubeをだらだら見すぎない"
    )

    reward = st.text_input(
        "終わったらごほうび",
        placeholder="例：コーヒーを飲む / 好きな動画を1本見る"
    )

    memo = st.text_area("作戦メモ", placeholder="今の気分や注意点など")

    if st.button("🧭 作戦を保存", type="primary"):
        if not priority_action.strip():
            st.warning("最優先の1つだけは入れてね。")
        else:
            comment = random.choice(LUNA_COMMENTS[mode])

            item = {
                "id": f"plan_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "mode": mode,
                "main_goal": main_goal.strip(),
                "priority_action": priority_action.strip(),
                "do_not": do_not.strip(),
                "reward": reward.strip(),
                "memo": memo.strip(),
                "luna_comment": comment,
                "status": "未完了",
                "review": "",
                "favorite": False,
            }

            data["plans"].append(item)
            save_data(data)
            st.session_state["latest_plan"] = item
            st.success("今日の作戦を保存したよ。")
            st.rerun()

with right:
    st.subheader("今日の作戦カード")

    latest = st.session_state.get("latest_plan")
    if latest is None and data["plans"]:
        latest = data["plans"][-1]

    if latest:
        st.markdown(f"## {latest['mode']}モード")
        st.write(f"目的：{latest.get('main_goal', '')}")

        st.markdown("### 最優先の1つ")
        st.success(latest["priority_action"])

        st.markdown("### 今日はやらないこと")
        st.warning(latest.get("do_not", ""))

        st.markdown("### ごほうび")
        st.info(latest.get("reward", ""))

        st.markdown("### ルナの作戦コメント")
        st.info(latest.get("luna_comment", ""))

        new_status = st.selectbox(
            "状態",
            ["未完了", "進行中", "完了"],
            index=["未完了", "進行中", "完了"].index(latest.get("status", "未完了"))
        )

        review = st.text_area("夜の振り返り", value=latest.get("review", ""))

        fav = st.checkbox("⭐ 大事な作戦", value=bool(latest.get("favorite", False)))

        if st.button("🌙 作戦カードを更新"):
            latest["status"] = new_status
            latest["review"] = review.strip()
            latest["favorite"] = fav

            for x in data["plans"]:
                if x["id"] == latest["id"]:
                    x.update(latest)
                    break

            save_data(data)
            st.success("更新したよ。")
            st.rerun()
    else:
        st.info("まだ作戦がないよ。左から立ててみてね。")

st.divider()
st.subheader("作戦履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ 大事な作戦だけ表示", value=False)
    view = df.copy()

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        selected = st.selectbox("作戦を選ぶ", view["id"].tolist())
        chosen = next((x for x in data["plans"] if x["id"] == selected), None)

        if chosen:
            st.markdown(f"### {chosen['date']} / {chosen['mode']}モード")
            st.write(f"目的：{chosen.get('main_goal', '')}")
            st.write(f"最優先：{chosen.get('priority_action', '')}")
            st.write(f"やらないこと：{chosen.get('do_not', '')}")
            st.write(f"ごほうび：{chosen.get('reward', '')}")
            st.write(f"メモ：{chosen.get('memo', '')}")
            st.info(chosen.get("luna_comment", ""))
            st.write(f"状態：{chosen.get('status', '')}")
            st.write(f"振り返り：{chosen.get('review', '')}")

            if st.button("🗑️ この作戦を削除", type="secondary"):
                data["plans"] = [x for x in data["plans"] if x["id"] != selected]
                save_data(data)
                st.rerun()

csv = df.to_csv(index=False).encode("utf-8-sig") if not df.empty else None
if csv:
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day131_luna_strategy_room.csv",
        mime="text/csv"
    )
