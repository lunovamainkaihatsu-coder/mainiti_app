import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ひらめきの賞味期限", page_icon="💡", layout="wide")
DATA_FILE = Path(__file__).parent / "data" / "ideas.json"
CATEGORIES = ["アプリ開発", "仕事", "生活", "学習", "趣味", "その他"]
STATUSES = ["育てたい", "温め中", "保留", "実行中", "アーカイブ"]
TASK_STATUSES = ["未着手", "進行中", "完了"]


def uid():
    return uuid.uuid4().hex


def today():
    return date.today().isoformat()


def read_data():
    if not DATA_FILE.exists():
        return {"ideas": [], "reviews": [], "tasks": []}
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return validate(raw)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        st.error(f"データを読み込めませんでした: {exc}")
        st.stop()


def validate(raw):
    if not isinstance(raw, dict):
        raise ValueError("JSONの最上位はオブジェクトにしてください。")
    result = {}
    for name in ("ideas", "reviews", "tasks"):
        values = raw.get(name, [])
        if not isinstance(values, list) or any(not isinstance(v, dict) for v in values):
            raise ValueError(f"{name} はオブジェクトの配列にしてください。")
        result[name] = values
    for kind in result:
        for item in result[kind]:
            if not isinstance(item.get("id"), str) or not item["id"]:
                raise ValueError(f"{kind} に有効な id が必要です。")
    idea_ids = {x["id"] for x in result["ideas"]}
    if len(idea_ids) != len(result["ideas"]):
        raise ValueError("アイデアIDが重複しています。")
    for kind in ("reviews", "tasks"):
        ids = [x["id"] for x in result[kind]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{kind} のIDが重複しています。")
        if any(x.get("idea_id") not in idea_ids for x in result[kind]):
            raise ValueError(f"{kind} に存在しないアイデアへの参照があります。")
    return result


def save():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(st.session_state.db, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(DATA_FILE)


def refresh():
    save()
    st.rerun()


def idea_name(idea_id):
    return next((i.get("title", "名称未設定") for i in db["ideas"] if i["id"] == idea_id), "削除済み")


def idea_options():
    return {i["id"]: i.get("title", "名称未設定") for i in db["ideas"]}


def latest_score(idea):
    rev = sorted((r for r in db["reviews"] if r["idea_id"] == idea["id"]), key=lambda r: (r.get("date", ""), r["id"]))
    return int(rev[-1].get("expectation", idea.get("expectation", 3))) if rev else int(idea.get("expectation", 3))


def date_input_safe(label, value, key):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        parsed = date.today()
    return st.date_input(label, parsed, key=key)


if "db" not in st.session_state:
    st.session_state.db = read_data()
db = st.session_state.db
st.title("💡⏳ ひらめきの賞味期限")
st.caption("アイデアを保存し、時間を置いて見直し、育てたい発想を見つけるアプリ。データはこのPCにJSONで保存されます。")

tabs = st.tabs(["🏠 ホーム", "💡 アイデア登録", "⏳ 賞味期限", "🔄 再評価", "🗂️ アイデア図鑑", "🚀 実行計画", "📊 アイデア分析", "🛠️ 管理"])

with tabs[0]:
    due = [i for i in db["ideas"] if i.get("status") != "アーカイブ" and i.get("review_date", "9999-12-31") <= today()]
    cols = st.columns(4)
    for col, label, val in zip(cols, ["登録アイデア", "再評価待ち", "育てたい", "実行中"], [len(db["ideas"]), len(due), sum(i.get("status") == "育てたい" for i in db["ideas"]), sum(i.get("status") == "実行中" for i in db["ideas"]) ]):
        col.metric(label, val)
    st.subheader("⏳ 再評価が必要なアイデア")
    if due:
        for i in sorted(due, key=lambda x: x.get("review_date", ""))[:10]:
            st.write(f"**{i.get('title', '無題')}** — 予定日 {i.get('review_date', '未設定')} / 現在の期待度 {latest_score(i)}")
    else:
        st.info("今のところ再評価待ちはありません。")
    st.subheader("最近のアイデア")
    for i in sorted(db["ideas"], key=lambda x: x.get("created", ""), reverse=True)[:5]:
        st.write(f"💡 {i.get('title', '無題')}　·　{i.get('category', 'その他')}　·　{i.get('status', '温め中')}")

with tabs[1]:
    st.subheader("新しいひらめきを記録")
    with st.form("add_idea", clear_on_submit=True):
        title = st.text_input("アイデア名 *")
        category = st.selectbox("カテゴリー", CATEGORIES)
        summary = st.text_area("概要")
        trigger = st.text_area("思いついたきっかけ")
        value = st.text_area("どんな価値がある？")
        c1, c2 = st.columns(2)
        expectation = c1.slider("初期期待度", 1, 5, 4)
        difficulty = c2.slider("実現難易度", 1, 5, 3)
        review_date = st.date_input("次回再評価日", date.today() + timedelta(days=7))
        status = st.selectbox("状態", STATUSES, index=1)
        favorite = st.checkbox("お気に入り")
        memo = st.text_area("メモ")
        if st.form_submit_button("💾 アイデアを保存", type="primary"):
            if not title.strip():
                st.error("アイデア名を入力してね。")
            else:
                db["ideas"].append({"id": uid(), "title": title.strip(), "category": category, "summary": summary, "trigger": trigger, "value": value, "expectation": expectation, "difficulty": difficulty, "review_date": review_date.isoformat(), "status": status, "favorite": favorite, "memo": memo, "created": today()})
                refresh()

with tabs[2]:
    st.subheader("賞味期限＝次の見直し日")
    st.info("日付を過ぎてもアイデアは消えません。見直しのきっかけとして使ってね。")
    active = [i for i in db["ideas"] if i.get("status") != "アーカイブ"]
    if active:
        for i in sorted(active, key=lambda x: x.get("review_date", "9999-12-31")):
            overdue = i.get("review_date", "9999-12-31") <= today()
            st.write(f"{'🔔' if overdue else '🗓️'} **{i.get('title', '無題')}** — {i.get('review_date', '未設定')}　{'再評価待ち' if overdue else '予定あり'}")
        selected = st.selectbox("再評価日を変更するアイデア", list(idea_options()), format_func=lambda x: idea_options()[x], key="due_select")
        target = next(i for i in db["ideas"] if i["id"] == selected)
        new_due = date_input_safe("新しい再評価日", target.get("review_date"), "due_date")
        if st.button("再評価日を更新", key="due_update"):
            target["review_date"] = new_due.isoformat()
            refresh()
    else:
        st.info("アイデアを登録するとここに表示されるよ。")

with tabs[3]:
    st.subheader("アイデアを再評価")
    if db["ideas"]:
        options = idea_options()
        selected = st.selectbox("アイデアを選ぶ", list(options), format_func=lambda x: options[x], key="review_idea")
        target = next(i for i in db["ideas"] if i["id"] == selected)
        st.write(f"初期期待度：**{target.get('expectation', 3)} / 5**　最新期待度：**{latest_score(target)} / 5**")
        with st.form("review_form", clear_on_submit=True):
            review_date = st.date_input("評価日", date.today(), key="review_date_form")
            c1, c2 = st.columns(2)
            expectation = c1.slider("現在の期待度", 1, 5, latest_score(target))
            feasibility = c2.slider("実現可能性", 1, 5, 3)
            reason = st.text_area("今も魅力的だと思う理由・気づき")
            improvements = st.text_area("改善案")
            next_date = st.date_input("次回再評価日", date.today() + timedelta(days=7), key="review_next")
            status = st.selectbox("今後の扱い", STATUSES, index=STATUSES.index(target.get("status", "温め中")))
            if st.form_submit_button("🔄 再評価を記録", type="primary"):
                db["reviews"].append({"id": uid(), "idea_id": selected, "date": review_date.isoformat(), "expectation": expectation, "feasibility": feasibility, "reason": reason, "improvements": improvements})
                target["review_date"] = next_date.isoformat()
                target["status"] = status
                refresh()
    else:
        st.info("まずアイデアを登録してね。")

with tabs[4]:
    st.subheader("アイデア図鑑")
    query = st.text_input("キーワード検索", key="search")
    c1, c2, c3 = st.columns(3)
    category_filter = c1.selectbox("カテゴリー", ["すべて"] + CATEGORIES)
    status_filter = c2.selectbox("状態", ["すべて"] + STATUSES)
    favorites_only = c3.checkbox("お気に入りのみ")
    filtered = [i for i in db["ideas"] if (not query or query.casefold() in (i.get("title", "") + " " + i.get("summary", "")).casefold()) and (category_filter == "すべて" or i.get("category") == category_filter) and (status_filter == "すべて" or i.get("status") == status_filter) and (not favorites_only or i.get("favorite", False))]
    if not filtered:
        st.info("条件に一致するアイデアがありません。")
    for i in filtered:
        with st.expander(f"{'⭐ ' if i.get('favorite') else ''}{i.get('title', '無題')} ｜ {i.get('status', '温め中')} ｜ 期待度 {latest_score(i)}/5"):
            st.write(i.get("summary", ""))
            st.caption(f"カテゴリー：{i.get('category', 'その他')} ｜ 作成日：{i.get('created', '')} ｜ 再評価日：{i.get('review_date', '')}")
            st.write("**思いついたきっかけ**", i.get("trigger", ""))
            st.write("**想定する価値**", i.get("value", ""))
            st.write("**メモ**", i.get("memo", ""))
            history = sorted([r for r in db["reviews"] if r["idea_id"] == i["id"]], key=lambda r: r.get("date", ""))
            if history:
                frame = pd.DataFrame([{"日付": r.get("date", ""), "期待度": r.get("expectation", 0), "実現可能性": r.get("feasibility", 0)} for r in history])
                st.dataframe(frame, hide_index=True, use_container_width=True)
                chart_data = pd.DataFrame([{"日付": i.get("created", ""), "期待度": i.get("expectation", 3)}] + [{"日付": r.get("date", ""), "期待度": r.get("expectation", 3)} for r in history])
                st.line_chart(chart_data.set_index("日付"))

with tabs[5]:
    st.subheader("実行計画")
    if db["ideas"]:
        options = idea_options()
        with st.form("add_task", clear_on_submit=True):
            idea_id = st.selectbox("関連アイデア", list(options), format_func=lambda x: options[x])
            task_title = st.text_input("小さな行動 *")
            due_date = st.date_input("期限", date.today() + timedelta(days=7), key="task_due")
            minutes = st.number_input("所要時間（分）", min_value=0, max_value=100000, value=30, step=5)
            notes = st.text_area("メモ")
            if st.form_submit_button("タスクを追加"):
                if task_title.strip():
                    db["tasks"].append({"id": uid(), "idea_id": idea_id, "title": task_title.strip(), "due": due_date.isoformat(), "minutes": int(minutes), "status": "未着手", "notes": notes})
                    refresh()
                else:
                    st.error("行動名を入力してね。")
        st.divider()
        for task in sorted(db["tasks"], key=lambda t: t.get("due", "")):
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{task.get('title', '')}**　·　{idea_name(task['idea_id'])}　·　期限 {task.get('due', '')}")
            current_status = task.get("status", "未着手")
            new_status = c2.selectbox("進捗", TASK_STATUSES, index=TASK_STATUSES.index(current_status) if current_status in TASK_STATUSES else 0, key=f"task_{task['id']}", label_visibility="collapsed")
            if new_status != current_status:
                task["status"] = new_status
                refresh()
    else:
        st.info("アイデアを登録するとタスクを作れるよ。")

with tabs[6]:
    st.subheader("アイデア分析")
    if db["ideas"]:
        df = pd.DataFrame(db["ideas"])
        c1, c2, c3 = st.columns(3)
        c1.metric("アイデア総数", len(df))
        c2.metric("再評価回数", len(db["reviews"]))
        c3.metric("タスク達成率", f"{sum(t.get('status') == '完了' for t in db['tasks']) / len(db['tasks']) * 100:.0f}%" if db["tasks"] else "—")
        st.write("**カテゴリー別アイデア数**")
        st.bar_chart(df["category"].value_counts())
        st.write("**状態別アイデア数**")
        st.bar_chart(df["status"].value_counts())
        score_df = pd.DataFrame([{"アイデア": i.get("title", "無題"), "初期": int(i.get("expectation", 3)), "最新": latest_score(i), "変化": latest_score(i) - int(i.get("expectation", 3))} for i in db["ideas"]])
        st.write("**期待度の比較**")
        st.dataframe(score_df.sort_values("変化", ascending=False), hide_index=True, use_container_width=True)
    else:
        st.info("データを登録するとグラフが表示されるよ。")

with tabs[7]:
    st.subheader("編集・削除・バックアップ")
    st.caption("削除は取り消せないため、先にバックアップをおすすめするよ。")
    if db["ideas"]:
        options = idea_options()
        selected = st.selectbox("編集するアイデア", list(options), format_func=lambda x: options[x], key="manage_idea")
        target = next(i for i in db["ideas"] if i["id"] == selected)
        with st.form(f"edit_idea_{selected}"):
            title = st.text_input("アイデア名", target.get("title", ""))
            category = st.selectbox("カテゴリー", CATEGORIES, index=CATEGORIES.index(target.get("category")) if target.get("category") in CATEGORIES else 0)
            summary = st.text_area("概要", target.get("summary", ""))
            trigger = st.text_area("きっかけ", target.get("trigger", ""))
            value = st.text_area("想定価値", target.get("value", ""))
            expectation = st.slider("初期期待度", 1, 5, int(target.get("expectation", 3)))
            difficulty = st.slider("難易度", 1, 5, int(target.get("difficulty", 3)))
            review_date = date_input_safe("再評価日", target.get("review_date"), f"edit_due_{selected}")
            status = st.selectbox("状態", STATUSES, index=STATUSES.index(target.get("status")) if target.get("status") in STATUSES else 1)
            favorite = st.checkbox("お気に入り", bool(target.get("favorite", False)))
            memo = st.text_area("メモ", target.get("memo", ""))
            if st.form_submit_button("変更を保存"):
                if title.strip():
                    target.update(title=title.strip(), category=category, summary=summary, trigger=trigger, value=value, expectation=expectation, difficulty=difficulty, review_date=review_date.isoformat(), status=status, favorite=favorite, memo=memo)
                    refresh()
                else:
                    st.error("名前は空欄にできないよ。")
        st.write("**アイデアを削除**")
        confirm = st.checkbox("このアイデアと関連する再評価・タスクを削除する", key=f"confirm_{selected}")
        if st.button("🗑️ アイデアを削除", disabled=not confirm):
            db["ideas"] = [i for i in db["ideas"] if i["id"] != selected]
            db["reviews"] = [r for r in db["reviews"] if r["idea_id"] != selected]
            db["tasks"] = [t for t in db["tasks"] if t["idea_id"] != selected]
            refresh()
    st.divider()
    if db["reviews"]:
        st.write("**再評価履歴の編集・削除**")
        review_ids = {r["id"]: f"{idea_name(r['idea_id'])} / {r.get('date', '')} / {r.get('expectation', '')}点" for r in db["reviews"]}
        review_id = st.selectbox("履歴を選択", list(review_ids), format_func=lambda x: review_ids[x])
        review = next(r for r in db["reviews"] if r["id"] == review_id)
        with st.form(f"edit_review_{review_id}"):
            rdate = date_input_safe("評価日", review.get("date"), f"rdate_{review_id}")
            rex = st.slider("期待度", 1, 5, int(review.get("expectation", 3)))
            rfe = st.slider("実現可能性", 1, 5, int(review.get("feasibility", 3)))
            rreason = st.text_area("理由", review.get("reason", ""))
            rimp = st.text_area("改善案", review.get("improvements", ""))
            if st.form_submit_button("履歴を更新"):
                review.update(date=rdate.isoformat(), expectation=rex, feasibility=rfe, reason=rreason, improvements=rimp)
                refresh()
        if st.button("この履歴を削除", key=f"del_review_{review_id}"):
            db["reviews"] = [r for r in db["reviews"] if r["id"] != review_id]
            refresh()
    if db["tasks"]:
        st.write("**タスクの編集・削除**")
        task_ids = {t["id"]: f"{idea_name(t['idea_id'])} / {t.get('title', '')}" for t in db["tasks"]}
        task_id = st.selectbox("タスクを選択", list(task_ids), format_func=lambda x: task_ids[x], key="manage_task")
        task = next(t for t in db["tasks"] if t["id"] == task_id)
        with st.form(f"edit_task_{task_id}"):
            ttitle = st.text_input("行動名", task.get("title", ""))
            tdue = date_input_safe("期限", task.get("due"), f"tdue_{task_id}")
            tminutes = st.number_input("所要時間（分）", 0, 100000, int(task.get("minutes", 30)), step=5)
            tstatus = st.selectbox("状態", TASK_STATUSES, index=TASK_STATUSES.index(task.get("status")) if task.get("status") in TASK_STATUSES else 0)
            tnotes = st.text_area("メモ", task.get("notes", ""))
            if st.form_submit_button("タスクを更新"):
                if ttitle.strip():
                    task.update(title=ttitle.strip(), due=tdue.isoformat(), minutes=int(tminutes), status=tstatus, notes=tnotes)
                    refresh()
                else:
                    st.error("行動名は空欄にできないよ。")
        if st.button("このタスクを削除", key=f"del_task_{task_id}"):
            db["tasks"] = [t for t in db["tasks"] if t["id"] != task_id]
            refresh()
    st.divider()
    st.download_button("📥 JSONバックアップをダウンロード", data=json.dumps(db, ensure_ascii=False, indent=2), file_name=f"idea_backup_{today()}.json", mime="application/json")
    upload = st.file_uploader("JSONバックアップを復元", type="json")
    if upload is not None:
        try:
            restored = validate(json.loads(upload.getvalue().decode("utf-8")))
            st.success(f"読み込み可能：アイデア {len(restored['ideas'])}件、再評価 {len(restored['reviews'])}件、タスク {len(restored['tasks'])}件")
            if st.checkbox("現在のデータを上書きすることに同意します"):
                if st.button("📤 復元を実行"):
                    st.session_state.db = restored
                    refresh()
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            st.error(f"復元ファイルを確認してね：{exc}")
