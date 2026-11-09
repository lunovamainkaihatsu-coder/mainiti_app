
import json
import uuid
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="これ、仕組み化できない？",
    page_icon="⚙️",
    layout="wide",
)

DATA_FILE = Path("data/systemize.json")
DATA_FILE.parent.mkdir(exist_ok=True)

CATEGORIES = [
    "💼 仕事", "🏠 家事", "📚 学習",
    "🏃 健康", "💰 お金",
    "💻 アプリ開発", "📦 その他",
]

METHODS = [
    "📄 テンプレート化",
    "🤖 自動化",
    "📦 まとめて処理",
    "🗑️ 作業をなくす",
    "🔀 手順を改善",
]

STATUSES = [
    "未着手", "準備中", "試行中",
    "完了", "見送り",
]


def empty_data():
    return {
        "tasks": [],
        "ideas": [],
        "attempts": [],
        "reviews": [],
    }


def load_data():
    if not DATA_FILE.exists():
        return empty_data()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            result = json.load(f)

        if not isinstance(result, dict):
            raise ValueError("データ形式が不正です")

        for key in empty_data():
            if not isinstance(result.get(key), list):
                raise ValueError(f"{key} が不正です")

        return result

    except (OSError, ValueError) as e:
        st.error(f"データを読み込めません：{e}")
        st.stop()


def save_data():
    temp = DATA_FILE.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp.replace(DATA_FILE)


def new_id():
    return str(uuid.uuid4())


def task_by_id(task_id):
    return next(
        (t for t in data["tasks"] if t["id"] == task_id),
        None,
    )


def task_options():
    return {
        f"{t['name']} [{t['id'][:8]}]": t["id"]
        for t in data["tasks"]
    }


def select_task(key):
    options = task_options()

    if not options:
        st.info("先に作業を登録しよう！")
        return None

    label = st.selectbox(
        "対象の作業",
        list(options),
        key=key,
    )
    return task_by_id(options[label])


def weekly_frequency(task):
    period = task["period"]
    count = task["frequency"]

    if period == "毎日":
        return count * 7
    if period == "毎月":
        return count * 12 / 52
    return count


def latest_actual(task_id):
    records = [
        a for a in data["attempts"]
        if a["task_id"] == task_id
        and a.get("actual_after") is not None
    ]

    if not records:
        return None

    records.sort(
        key=lambda a: (a["date"], a["id"])
    )
    return records[-1]["actual_after"]


def weekly_saving(task):
    actual = latest_actual(task["id"])

    if actual is None:
        return None

    return (
        task["before_minutes"] - actual
    ) * weekly_frequency(task)


def show_task(task):
    with st.container(border=True):
        st.markdown(f"### ⚙️ {task['name']}")
        st.caption(
            f"{task['category']} ｜ "
            f"{task['period']} {task['frequency']}回"
        )
        st.write(
            f"改善前：{task['before_minutes']}分/回"
        )
        st.write(
            f"面倒度：{'★' * task['annoyance']}"
        )

        if task.get("problem"):
            st.write(task["problem"])

        saving = weekly_saving(task)
        if saving is not None:
            st.metric(
                "週間削減見込み",
                f"{saving:.1f}分",
            )


data = load_data()

st.title("⚙️ これ、仕組み化できない？")
st.caption("Day316 / 365")
st.markdown(
    "**その面倒、毎回やらなくてもいいかもしれない。**"
)

tabs = st.tabs([
    "🏠 ホーム",
    "📝 作業を登録",
    "💡 改善アイデア",
    "⏱️ 時間削減",
    "🚀 改善チャレンジ",
    "📚 ライブラリ",
    "📊 分析",
    "🛠️ 管理",
])

# ==================================================
# 1. ホーム
# ==================================================

with tabs[0]:
    st.subheader("🏠 仕組み化ダッシュボード")

    total_saving = sum(
        weekly_saving(t) or 0
        for t in data["tasks"]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("登録作業", len(data["tasks"]))
    c2.metric("改善アイデア", len(data["ideas"]))
    c3.metric("試行回数", len(data["attempts"]))
    c4.metric(
        "週間削減見込み",
        f"{total_saving:.1f}分",
    )

    st.divider()
    st.subheader("最近の作業")

    for task in reversed(data["tasks"][-5:]):
        show_task(task)

    if not data["tasks"]:
        st.info("最初の面倒な作業を登録してみよう！")


# ==================================================
# 2. 作業登録
# ==================================================

with tabs[1]:
    st.subheader("📝 面倒な作業を登録")

    with st.form("task_form", clear_on_submit=True):
        name = st.text_input("作業名")

        category = st.selectbox(
            "カテゴリー", CATEGORIES
        )

        period = st.selectbox(
            "頻度の単位",
            ["毎日", "毎週", "毎月"],
            index=1,
        )

        frequency = st.number_input(
            "その期間に何回？",
            min_value=1,
            value=5,
        )

        before = st.number_input(
            "1回の所要時間（分）",
            min_value=0.0,
            value=15.0,
        )

        annoyance = st.slider(
            "面倒度", 1, 5, 4
        )

        priority = st.slider(
            "優先度", 1, 5, 3
        )

        problem = st.text_area("何が面倒？")
        memo = st.text_area("改善のアイデア")

        if st.form_submit_button(
            "⚙️ 保存", type="primary"
        ):
            if not name.strip():
                st.warning("作業名を入力してね")
            else:
                data["tasks"].append({
                    "id": new_id(),
                    "name": name.strip(),
                    "category": category,
                    "period": period,
                    "frequency": frequency,
                    "before_minutes": before,
                    "annoyance": annoyance,
                    "priority": priority,
                    "problem": problem,
                    "memo": memo,
                    "created_at": date.today().isoformat(),
                })
                save_data()
                st.rerun()


# ==================================================
# 3. 改善アイデア
# ==================================================

with tabs[2]:
    st.subheader("💡 改善アイデア")

    task = select_task("idea_task")

    if task:
        with st.form("idea_form", clear_on_submit=True):
            method = st.selectbox(
                "改善方法", METHODS
            )

            title = st.text_input("アイデア名")
            description = st.text_area("具体的な内容")

            difficulty = st.slider(
                "難易度", 1, 5, 2
            )

            preparation = st.number_input(
                "準備時間（分）",
                min_value=0.0,
                value=30.0,
            )

            expected_after = st.number_input(
                "改善後の予想時間（分）",
                min_value=0.0,
                value=5.0,
            )

            status = st.selectbox(
                "進捗", STATUSES
            )

            if st.form_submit_button("💡 保存"):
                if not title.strip():
                    st.warning("アイデア名を入力してね")
                else:
                    data["ideas"].append({
                        "id": new_id(),
                        "task_id": task["id"],
                        "method": method,
                        "title": title.strip(),
                        "description": description,
                        "difficulty": difficulty,
                        "preparation": preparation,
                        "expected_after": expected_after,
                        "status": status,
                    })
                    save_data()
                    st.rerun()

        st.divider()

        for idea in data["ideas"]:
            if idea["task_id"] == task["id"]:
                with st.container(border=True):
                    st.write(f"**{idea['title']}**")
                    st.caption(
                        f"{idea['method']} ｜ {idea['status']}"
                    )
                    st.write(idea["description"])


# ==================================================
# 4. 時間削減シミュレーター
# ==================================================

with tabs[3]:
    st.subheader("⏱️ 時間削減シミュレーター")

    task = select_task("calculator_task")

    if task:
        before = st.number_input(
            "改善前（分/回）",
            min_value=0.0,
            value=float(task["before_minutes"]),
        )

        after = st.number_input(
            "改善後（分/回）",
            min_value=0.0,
            value=5.0,
        )

        frequency = st.number_input(
            "週の作業回数",
            min_value=0.1,
            value=max(
                0.1,
                float(weekly_frequency(task)),
            ),
        )

        preparation = st.number_input(
            "改善準備時間（分）",
            min_value=0.0,
            value=30.0,
        )

        saving = (before - after) * frequency

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "週間削減",
            f"{saving:.1f}分",
        )

        c2.metric(
            "年間削減",
            f"{saving * 52 / 60:.1f}時間",
        )

        rate = (
            (before - after) / before * 100
            if before > 0 else 0
        )

        c3.metric(
            "時間短縮率",
            f"{rate:.1f}%",
        )

        if saving > 0:
            st.success(
                f"準備時間の回収目安："
                f"{preparation / saving:.1f}週間"
            )
        else:
            st.info(
                "削減時間が0以下なので、"
                "回収期間は計算できません。"
            )

        st.caption(
            "※年間52週、作業頻度が一定の場合の試算。"
        )


# ==================================================
# 5. 改善チャレンジ
# ==================================================

with tabs[4]:
    st.subheader("🚀 改善チャレンジ")

    task = select_task("attempt_task")

    if task:
        ideas = [
            i for i in data["ideas"]
            if i["task_id"] == task["id"]
        ]

        if not ideas:
            st.info("先に改善アイデアを登録しよう！")
        else:
            options = {
                f"{i['title']} [{i['id'][:8]}]": i["id"]
                for i in ideas
            }

            with st.form("attempt_form"):
                selected = st.selectbox(
                    "試すアイデア",
                    list(options),
                )

                attempt_date = st.date_input(
                    "実施日",
                    max_value=date.today(),
                )

                status = st.selectbox(
                    "進捗",
                    STATUSES,
                    index=2,
                )

                action = st.text_area("試した内容")

                measured = st.checkbox(
                    "実際に時間を測定した",
                    value=True,
                )

                actual_after = st.number_input(
                    "実測時間（分/回）",
                    min_value=0.0,
                    value=5.0,
                )

                result = st.text_area("結果・課題")

                if st.form_submit_button(
                    "🚀 記録する"
                ):
                    data["attempts"].append({
                        "id": new_id(),
                        "task_id": task["id"],
                        "idea_id": options[selected],
                        "date": str(attempt_date),
                        "status": status,
                        "action": action,
                        "actual_after": (
                            actual_after
                            if measured else None
                        ),
                        "result": result,
                    })
                    save_data()
                    st.rerun()

        st.divider()

        for attempt in data["attempts"]:
            if attempt["task_id"] == task["id"]:
                with st.container(border=True):
                    st.write(
                        f"**{attempt['date']}｜"
                        f"{attempt['status']}**"
                    )
                    st.write(attempt["action"])
                    st.write(attempt["result"])


# ==================================================
# 6. ライブラリ
# ==================================================

with tabs[5]:
    st.subheader("📚 仕組み化ライブラリ")

    search = st.text_input("🔍 検索")

    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="library_category",
    )

    for task in data["tasks"]:
        if search.lower() not in (
            task["name"] + task.get("problem", "")
        ).lower():
            continue

        if (
            category_filter != "すべて"
            and task["category"] != category_filter
        ):
            continue

        show_task(task)

        with st.expander(
            f"🔁 {task['name']} を振り返る"
        ):
            with st.form(
                f"review_form_{task['id']}"
            ):
                review_date = st.date_input(
                    "振り返り日",
                    max_value=date.today(),
                )

                current_minutes = st.number_input(
                    "現在の所要時間（分/回）",
                    min_value=0.0,
                    value=float(
                        task["before_minutes"]
                    ),
                )

                ease = st.slider(
                    "使いやすさ", 1, 5, 3
                )

                continuing = st.checkbox(
                    "継続利用している",
                    value=True,
                )

                issue = st.text_area("問題点")
                next_idea = st.text_area(
                    "次の改善案"
                )

                if st.form_submit_button(
                    "🔁 振り返りを保存"
                ):
                    data["reviews"].append({
                        "id": new_id(),
                        "task_id": task["id"],
                        "date": str(review_date),
                        "current_minutes": current_minutes,
                        "ease": ease,
                        "continuing": continuing,
                        "issue": issue,
                        "next_idea": next_idea,
                    })
                    save_data()
                    st.rerun()

            for review in data["reviews"]:
                if review["task_id"] == task["id"]:
                    st.caption(
                        f"{review['date']}｜"
                        f"{review['current_minutes']}分｜"
                        f"使いやすさ {review['ease']}/5"
                    )
                    if review["issue"]:
                        st.write(review["issue"])


# ==================================================
# 7. 分析
# ==================================================

with tabs[6]:
    st.subheader("📊 改善分析")

    if not data["tasks"]:
        st.info("作業を登録すると分析できるよ")
    else:
        category_counts = pd.Series(
            [t["category"] for t in data["tasks"]]
        ).value_counts()

        st.markdown("### カテゴリー別")
        st.bar_chart(category_counts)

        if data["ideas"]:
            st.markdown("### 改善方法別")

            method_counts = pd.Series(
                [i["method"] for i in data["ideas"]]
            ).value_counts()

            st.bar_chart(method_counts)

        rows = []

        for task in data["tasks"]:
            saving = weekly_saving(task)

            if saving is not None:
                rows.append({
                    "作業": task["name"],
                    "週間削減見込み（分）": round(
                        saving, 1
                    ),
                })

        if rows:
            st.markdown("### 削減時間ランキング")
            st.dataframe(
                pd.DataFrame(rows).sort_values(
                    "週間削減見込み（分）",
                    ascending=False,
                ),
                hide_index=True,
                use_container_width=True,
            )


# ==================================================
# 8. 管理
# ==================================================

with tabs[7]:
    st.subheader("🛠️ データ管理")

    task = select_task("manage_task")

    if task:
        with st.form(f"edit_{task['id']}"):
            name = st.text_input(
                "作業名", value=task["name"]
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=CATEGORIES.index(
                    task["category"]
                ),
            )

            before = st.number_input(
                "改善前の時間",
                min_value=0.0,
                value=float(task["before_minutes"]),
            )

            problem = st.text_area(
                "問題点",
                value=task.get("problem", ""),
            )

            if st.form_submit_button(
                "💾 変更を保存"
            ):
                if name.strip():
                    task.update({
                        "name": name.strip(),
                        "category": category,
                        "before_minutes": before,
                        "problem": problem,
                    })
                    save_data()
                    st.rerun()
                else:
                    st.warning("作業名を入力してね")

        st.warning(
            "作業を削除すると、関連する改善アイデア・"
            "試行・振り返りも削除されます。"
        )

        confirm = st.checkbox(
            "この作業を削除する"
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=not confirm,
        ):
            task_id = task["id"]

            data["tasks"] = [
                x for x in data["tasks"]
                if x["id"] != task_id
            ]

            for key in (
                "ideas", "attempts", "reviews"
            ):
                data[key] = [
                    x for x in data[key]
                    if x["task_id"] != task_id
                ]

            save_data()
            st.rerun()

    st.divider()
    st.subheader("💾 バックアップ")

    st.download_button(
        "⬇️ JSONをダウンロード",
        data=json.dumps(
            data, ensure_ascii=False, indent=2
        ),
        file_name="systemize_backup.json",
        mime="application/json",
    )

    st.subheader("📤 データを復元")

    uploaded = st.file_uploader(
        "バックアップJSON",
        type=["json"],
    )

    if uploaded:
        try:
            restored = json.loads(
                uploaded.getvalue().decode("utf-8")
            )

            if not isinstance(restored, dict):
                raise ValueError(
                    "JSON全体の形式が不正です"
                )

            for key in empty_data():
                if not isinstance(
                    restored.get(key), list
                ):
                    raise ValueError(
                        f"{key} が不正です"
                    )

            st.success("JSON形式を確認しました")

            confirm_restore = st.checkbox(
                "現在のデータを上書きする"
            )

            if st.button(
                "📤 復元",
                disabled=not confirm_restore,
            ):
                data = restored
                save_data()
                st.rerun()

        except (ValueError, UnicodeDecodeError) as e:
            st.error(f"復元できません：{e}")


st.divider()
st.caption(
    "DAY 316 / 365 — "
    "人生の余白は、仕組みで増やせる。⚙️✨"
)
