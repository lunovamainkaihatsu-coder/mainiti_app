import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day181：夢・目標ロードマップ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day181_goal_roadmap.json")

CATEGORIES = [
    "仕事",
    "お金",
    "健康",
    "移住",
    "LuNova",
    "勉強",
    "家族",
    "アプリ",
    "その他",
]

PRIORITIES = [
    "🔴 最優先",
    "🟠 高",
    "🟡 普通",
    "🟢 低",
]

STATUS = [
    "構想中",
    "進行中",
    "達成",
    "保留",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"goals": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "goals" not in data:
        data["goals"] = []

    for goal in data["goals"]:
        if "steps" not in goal:
            goal["steps"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def progress_rate(goal):
    steps = goal.get("steps", [])

    if not steps:
        return 0

    done = len([x for x in steps if x.get("done", False)])
    total = len(steps)

    return round(done / total * 100, 1)


def progress_text(goal):
    steps = goal.get("steps", [])

    if not steps:
        return "0 / 0"

    done = len([x for x in steps if x.get("done", False)])
    total = len(steps)

    return f"{done} / {total}"


def days_left(target_date):
    try:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
        return (d - date.today()).days
    except:
        return None


def due_label(days):
    if days is None:
        return "期限なし"

    if days < 0:
        return "期限超過"

    if days == 0:
        return "今日"

    if days <= 7:
        return "7日以内"

    if days <= 30:
        return "30日以内"

    return "余裕あり"


def to_df(data):
    rows = []

    for x in data["goals"]:
        rate = progress_rate(x)
        days = days_left(x.get("target_date", ""))

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "category": x["category"],
            "priority": x["priority"],
            "status": x.get("status", "構想中"),
            "target_date": x.get("target_date", ""),
            "days_left": days if days is not None else "",
            "due": due_label(days),
            "progress": rate,
            "steps": progress_text(x),
            "description": x.get("description", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        priority_order = {
            "🔴 最優先": 0,
            "🟠 高": 1,
            "🟡 普通": 2,
            "🟢 低": 3,
        }

        df["priority_order"] = df["priority"].map(priority_order)
        df = df.sort_values(["status", "priority_order", "target_date"], ascending=[True, True, True])

    return df


def find_goal(data, goal_id):
    for x in data["goals"]:
        if x["id"] == goal_id:
            return x

    return None


def find_step(goal, step_id):
    for x in goal.get("steps", []):
        if x["id"] == step_id:
            return x

    return None


def add_template_goals(data):
    if data["goals"]:
        return False

    templates = [
        {
            "title": "LuNova設立",
            "category": "LuNova",
            "priority": "🔴 最優先",
            "status": "進行中",
            "target_date": date.today().replace(year=date.today().year + 3).isoformat(),
            "description": "AIと人が共に成長する未来を作る。",
            "memo": "長期目標。焦らず積み上げる。",
            "steps": [
                "毎日アプリを継続する",
                "LUNAPOCKETの設計を進める",
                "月5万円の副収入を作る",
                "法人化の準備をする",
            ],
        },
        {
            "title": "東京・神奈川方面への移住",
            "category": "移住",
            "priority": "🟠 高",
            "status": "構想中",
            "target_date": date.today().replace(year=date.today().year + 1).isoformat(),
            "description": "生活と仕事の拠点を広げる。",
            "memo": "相模大野、町田、北区など候補。",
            "steps": [
                "候補地を調べる",
                "家賃相場を見る",
                "移住資金を貯める",
                "現地を歩いてみる",
            ],
        },
        {
            "title": "健康を整える",
            "category": "健康",
            "priority": "🟡 普通",
            "status": "進行中",
            "target_date": date.today().replace(year=date.today().year + 1).isoformat(),
            "description": "筋トレ・睡眠・食事を整えて、動ける体を作る。",
            "memo": "無理せず継続。",
            "steps": [
                "筋トレ記録を続ける",
                "水分補給を意識する",
                "睡眠記録をつける",
                "体重を記録する",
            ],
        },
    ]

    for t in templates:
        goal = {
            "id": f"goal_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "title": t["title"],
            "category": t["category"],
            "priority": t["priority"],
            "status": t["status"],
            "target_date": t["target_date"],
            "description": t["description"],
            "memo": t["memo"],
            "steps": [],
        }

        for step_name in t["steps"]:
            goal["steps"].append({
                "id": f"step_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{len(goal['steps'])}",
                "title": step_name,
                "done": False,
                "created_at": now_str(),
            })

        data["goals"].append(goal)

    return True


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Day181：夢・目標ロードマップ")
st.caption("大きな夢を小さなステップに分解して、進捗を見える化するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("初期テンプレート")

    if st.button("テンプレート目標を追加"):
        added = add_template_goals(data)

        if added:
            save_data(data)
            st.success("テンプレートを追加したよ。")
            st.rerun()
        else:
            st.info("すでに目標があるので追加しなかったよ。")

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("目標を登録")

    title = st.text_input(
        "目標タイトル",
        placeholder="例：東京移住 / LuNova設立 / 月収50万円"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    priority = st.selectbox(
        "優先度",
        PRIORITIES
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    target_date = st.date_input(
        "目標日",
        value=date.today().replace(year=date.today().year + 1)
    )

    description = st.text_area(
        "説明",
        height=90,
        placeholder="この目標をなぜ叶えたい？"
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="補足、期限、関連アイデアなど"
    )

    if st.button("🚀 目標を保存", type="primary"):
        if not title.strip():
            st.warning("目標タイトルを入れてね。")
        else:
            item = {
                "id": f"goal_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "category": category,
                "priority": priority,
                "status": status,
                "target_date": target_date.isoformat(),
                "description": description.strip(),
                "memo": memo.strip(),
                "steps": [],
            }

            data["goals"].append(item)
            save_data(data)

            st.success("目標を保存したよ。")
            st.rerun()

with right:
    st.subheader("ロードマップ状況")

    df = to_df(data)

    if df.empty:
        st.info("まだ目標がないよ。")
    else:
        total = len(df)
        achieved = len(df[df["status"] == "達成"])
        active = len(df[df["status"].isin(["構想中", "進行中"])])
        avg_progress = round(float(df["progress"].mean()), 1)

        c1, c2 = st.columns(2)

        with c1:
            st.metric("目標数", total)
            st.metric("進行中", active)

        with c2:
            st.metric("達成", achieved)
            st.metric("平均達成率", f"{avg_progress}%")

        st.progress(min(avg_progress / 100, 1.0))

        st.divider()

        st.subheader("期限が近い目標")

        near = df[df["due"].isin(["期限超過", "今日", "7日以内", "30日以内"])]

        if near.empty:
            st.success("期限が近すぎる目標は少なそう。")
        else:
            st.dataframe(
                near[["title", "category", "target_date", "due", "progress", "status"]],
                use_container_width=True,
                height=220
            )

st.divider()
st.subheader("目標一覧")

df = to_df(data)

if df.empty:
    st.write("まだロードマップが空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="目標名・説明・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        status_filter = st.selectbox(
            "状態で絞る",
            ["すべて"] + STATUS
        )

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["description"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    st.dataframe(
        view[[
            "title",
            "category",
            "priority",
            "status",
            "target_date",
            "due",
            "progress",
            "steps",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・ステップ管理")

    if view.empty:
        st.write("条件に合う目標がないよ。")
    else:
        selected_goal_id = st.selectbox(
            "目標を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_goal(data, x)['title']} / {find_goal(data, x)['category']}"
        )

        goal = find_goal(data, selected_goal_id)

        if goal:
            st.markdown(f"## {goal['title']}")
            st.write(f"カテゴリ：{goal['category']}")
            st.write(f"優先度：{goal['priority']}")
            st.write(f"状態：{goal.get('status', '構想中')}")
            st.write(f"目標日：{goal.get('target_date', '')}")

            rate = progress_rate(goal)

            st.progress(rate / 100)
            st.info(f"達成率：{rate}%（{progress_text(goal)}）")

            if goal.get("description"):
                st.markdown("### 説明")
                st.write(goal["description"])

            if goal.get("memo"):
                st.markdown("### メモ")
                st.info(goal["memo"])

            st.divider()
            st.subheader("ステップ追加")

            new_step = st.text_input(
                "新しいステップ",
                placeholder="例：引っ越し資金を10万円貯める"
            )

            if st.button("➕ ステップを追加"):
                if not new_step.strip():
                    st.warning("ステップ内容を入れてね。")
                else:
                    goal["steps"].append({
                        "id": f"step_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                        "title": new_step.strip(),
                        "done": False,
                        "created_at": now_str(),
                    })

                    goal["updated_at"] = now_str()
                    save_data(data)

                    st.success("ステップを追加したよ。")
                    st.rerun()

            st.divider()
            st.subheader("ステップ一覧")

            steps = goal.get("steps", [])

            if not steps:
                st.write("まだステップがないよ。")
            else:
                for step in steps:
                    done = st.checkbox(
                        step["title"],
                        value=bool(step.get("done", False)),
                        key=f"step_{step['id']}"
                    )

                    step["done"] = done

                if st.button("📝 ステップ状態を保存"):
                    goal["updated_at"] = now_str()

                    if progress_rate(goal) >= 100 and goal.get("status") != "達成":
                        goal["status"] = "達成"

                    save_data(data)

                    st.success("ステップを更新したよ。")
                    st.rerun()

                delete_step_id = st.selectbox(
                    "削除するステップ",
                    [s["id"] for s in steps],
                    format_func=lambda x: find_step(goal, x)["title"]
                )

                if st.button("🗑️ ステップを削除", type="secondary"):
                    goal["steps"] = [
                        s for s in goal["steps"]
                        if s["id"] != delete_step_id
                    ]

                    goal["updated_at"] = now_str()
                    save_data(data)

                    st.warning("ステップを削除したよ。")
                    st.rerun()

            st.divider()
            st.subheader("目標の更新・削除")

            c1, c2 = st.columns(2)

            with c1:
                new_status = st.selectbox(
                    "状態を更新",
                    STATUS,
                    index=STATUS.index(goal.get("status", "構想中")),
                    key=f"status_{goal['id']}"
                )

            with c2:
                new_priority = st.selectbox(
                    "優先度を更新",
                    PRIORITIES,
                    index=PRIORITIES.index(goal.get("priority", "🟡 普通")),
                    key=f"priority_{goal['id']}"
                )

            if st.button("📝 目標を更新"):
                goal["status"] = new_status
                goal["priority"] = new_priority
                goal["updated_at"] = now_str()

                save_data(data)

                st.success("目標を更新したよ。")
                st.rerun()

            if st.button("🗑️ この目標を削除", type="secondary"):
                data["goals"] = [
                    x for x in data["goals"]
                    if x["id"] != selected_goal_id
                ]

                save_data(data)
                st.warning("目標を削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day181_goal_roadmap.csv",
        mime="text/csv"
    )
