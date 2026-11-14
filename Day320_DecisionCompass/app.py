import json
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="何を大切にして選ぶ？", page_icon="🧭", layout="wide")
DATA_PATH = Path(__file__).parent / "data" / "decisions.json"
CATEGORIES = ["仕事・キャリア", "暮らし・引っ越し", "買い物", "学習", "人間関係", "その他"]


def empty_data():
    return {"decisions": []}


def validate(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("decisions"), list):
        raise ValueError("decisions 配列が必要です")
    for d in payload["decisions"]:
        if not isinstance(d, dict) or not isinstance(d.get("id"), str) or not isinstance(d.get("title"), str):
            raise ValueError("意思決定データの形式が正しくありません")
        if not isinstance(d.get("options"), list) or not isinstance(d.get("criteria"), list):
            raise ValueError("options と criteria は配列にしてください")
        if not all(isinstance(o, dict) and isinstance(o.get("id"), str) and isinstance(o.get("name"), str) for o in d["options"]):
            raise ValueError("選択肢の形式が正しくありません")
        if not all(isinstance(c, dict) and isinstance(c.get("id"), str) and isinstance(c.get("name"), str) for c in d["criteria"]):
            raise ValueError("判断基準の形式が正しくありません")
    return payload


def load():
    if not DATA_PATH.exists():
        return empty_data()
    try:
        return validate(json.loads(DATA_PATH.read_text(encoding="utf-8")))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        st.error(f"保存データを読み込めませんでした: {exc}。バックアップを確認してください。")
        st.stop()


def save():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(st.session_state.db, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DATA_PATH)


def uid():
    return uuid.uuid4().hex


def rerun_saved(message="保存しました！"):
    save()
    st.toast(message)
    st.rerun()


def current_decision():
    decisions = st.session_state.db["decisions"]
    if not decisions:
        st.info("まず「📝 迷いを登録」からテーマを作成しよう！")
        return None
    ids = [d["id"] for d in decisions]
    selected = st.selectbox("対象の意思決定", ids, format_func=lambda x: next(d["title"] for d in decisions if d["id"] == x), key="active_decision")
    return next(d for d in decisions if d["id"] == selected)


def score(d, weights=None):
    criteria = d["criteria"]
    weights = weights or {c["id"]: c["weight"] for c in criteria}
    denom = sum(weights.get(c["id"], 0) for c in criteria)
    results = []
    for opt in d["options"]:
        ratings = opt.get("ratings", {})
        value = sum(float(ratings.get(c["id"], 3)) * weights.get(c["id"], 0) for c in criteria) / denom if denom else None
        results.append((opt["name"], value, opt["id"]))
    return sorted(results, key=lambda x: x[1] if x[1] is not None else -1, reverse=True)


if "db" not in st.session_state:
    st.session_state.db = load()

st.title("🧭 何を大切にして選ぶ？")
st.caption("Day320 / 365 | 自分の価値観で比較する意思決定サポート")
tabs = st.tabs(["🏠 ホーム", "📝 迷いを登録", "⚖️ 判断基準", "📊 比較・採点", "🏆 ランキング", "🔄 シナリオ分析", "💭 決定と振り返り", "🛠️ 管理"])

with tabs[0]:
    decisions = st.session_state.db["decisions"]
    a, b, c = st.columns(3)
    a.metric("登録テーマ", len(decisions))
    b.metric("検討中", sum(d.get("status") == "検討中" for d in decisions))
    c.metric("決定済み", sum(d.get("status") == "決定済み" for d in decisions))
    if decisions:
        for d in reversed(decisions):
            with st.container(border=True):
                st.subheader(d["title"])
                st.write(f"{d.get('category','その他')} / {d.get('status','検討中')} / 期限: {d.get('deadline','未設定')}")
                st.caption(f"選択肢 {len(d['options'])} 件・判断基準 {len(d['criteria'])} 件")
    else:
        st.info("選択に迷っていることを登録してみよう。")

with tabs[1]:
    st.subheader("新しい意思決定を登録")
    with st.form("new_decision", clear_on_submit=True):
        title = st.text_input("何について迷っている？ *")
        category = st.selectbox("カテゴリー", CATEGORIES)
        deadline = st.date_input("決めたい期限", value=date.today())
        feeling = st.text_area("今の気持ち")
        names = st.text_area("選択肢（1行に1つ、2つ以上）", placeholder="A社に転職する\nB社に転職する\n現職を続ける")
        if st.form_submit_button("テーマを登録", type="primary"):
            options = [x.strip() for x in names.splitlines() if x.strip()]
            if not title.strip() or len(options) < 2 or len(set(options)) != len(options):
                st.error("タイトルと、重複のない選択肢を2つ以上入力してね。")
            else:
                st.session_state.db["decisions"].append({"id": uid(), "title": title.strip(), "category": category, "deadline": deadline.isoformat(), "feeling": feeling, "status": "検討中", "options": [{"id": uid(), "name": n, "ratings": {}} for n in options], "criteria": [], "intuition": "", "concerns": "", "nonnegotiable": "", "chosen": "", "reason": "", "satisfaction": None, "reflection": "", "created": datetime.now().isoformat(timespec="seconds")})
                rerun_saved("テーマを登録したよ！")
    st.divider()
    d = current_decision()
    if d:
        st.subheader("選択肢を追加")
        with st.form("add_option", clear_on_submit=True):
            name = st.text_input("新しい選択肢")
            if st.form_submit_button("追加"):
                if name.strip() and name.strip() not in [o["name"] for o in d["options"]]:
                    d["options"].append({"id": uid(), "name": name.strip(), "ratings": {}})
                    rerun_saved()
                else:
                    st.warning("未入力または重複しているよ。")
        st.write("現在の選択肢：", " / ".join(o["name"] for o in d["options"]))

with tabs[2]:
    d = current_decision()
    if d:
        st.subheader("判断基準を登録")
        with st.form("add_criterion", clear_on_submit=True):
            name = st.text_input("判断基準名", placeholder="収入、成長、自由時間など")
            weight = st.slider("重要度", 1, 5, 3)
            description = st.text_input("評価するときの目安（任意）")
            if st.form_submit_button("判断基準を追加"):
                if name.strip() and name.strip() not in [c["name"] for c in d["criteria"]]:
                    d["criteria"].append({"id": uid(), "name": name.strip(), "weight": weight, "description": description})
                    rerun_saved()
                else:
                    st.warning("未入力または重複しているよ。")
        st.divider()
        for c in d["criteria"]:
            with st.expander(f"{c['name']}（重要度 {c['weight']}）"):
                with st.form(f"criterion_{c['id']}"):
                    n = st.text_input("基準名", value=c["name"])
                    w = st.slider("重要度", 1, 5, int(c["weight"]))
                    desc = st.text_input("評価の目安", value=c.get("description", ""))
                    if st.form_submit_button("変更を保存"):
                        if n.strip():
                            c.update(name=n.strip(), weight=w, description=desc)
                            rerun_saved()
                        else:
                            st.error("名前を入力してね。")

with tabs[3]:
    d = current_decision()
    if d:
        if not d["criteria"]:
            st.info("先に「⚖️ 判断基準」で基準を登録してね。")
        else:
            st.caption("各選択肢を1〜5点で評価。未評価の項目は初期値3点として計算されるよ。")
            with st.form(f"ratings_{d['id']}"):
                pending = {}
                for opt in d["options"]:
                    st.subheader(opt["name"])
                    pending[opt["id"]] = {}
                    cols = st.columns(min(3, max(1, len(d["criteria"]))))
                    for i, criterion in enumerate(d["criteria"]):
                        with cols[i % len(cols)]:
                            pending[opt["id"]][criterion["id"]] = st.slider(criterion["name"], 1, 5, int(opt.get("ratings", {}).get(criterion["id"], 3)), key=f"rate_{d['id']}_{opt['id']}_{criterion['id']}")
                if st.form_submit_button("評価を保存", type="primary"):
                    for opt in d["options"]:
                        opt["ratings"] = pending[opt["id"]]
                    rerun_saved()
            st.subheader("重み付き総合点")
            for name, value, _ in score(d):
                st.write(f"**{name}：{value:.2f} / 5**")
                st.progress(value / 5)

with tabs[4]:
    d = current_decision()
    if d:
        if not d["criteria"]:
            st.info("判断基準を登録するとランキングを表示できるよ。")
        else:
            results = score(d)
            st.dataframe(pd.DataFrame([{"順位": i + 1, "選択肢": n, "総合点": round(v, 2)} for i, (n, v, _) in enumerate(results)]), hide_index=True, use_container_width=True)
            st.bar_chart(pd.DataFrame({"選択肢": [r[0] for r in results], "総合点": [r[1] for r in results]}).set_index("選択肢"))
            st.subheader("強みと弱み")
            for opt in d["options"]:
                ratings = opt.get("ratings", {})
                ordered = sorted(d["criteria"], key=lambda c: int(ratings.get(c["id"], 3)), reverse=True)
                with st.expander(opt["name"]):
                    for c in ordered:
                        st.write(f"{c['name']}：{ratings.get(c['id'], 3)} / 5（重要度 {c['weight']}）")
            st.caption("スコアは判断の参考。数字に表せない条件や直感も大切にしてね。")

with tabs[5]:
    d = current_decision()
    if d:
        if not d["criteria"]:
            st.info("先に判断基準を登録してね。")
        else:
            st.subheader("重要度を変えたら順位はどうなる？")
            weights = {}
            for c in d["criteria"]:
                weights[c["id"]] = st.slider(c["name"], 0, 5, int(c["weight"]), key=f"scenario_{d['id']}_{c['id']}")
            if not sum(weights.values()):
                st.warning("少なくとも1つの重要度を1以上にしてね。")
            else:
                base = score(d)
                alternate = score(d, weights)
                st.dataframe(pd.DataFrame([{"選択肢": n, "現在の点数": round(next(x[1] for x in base if x[2] == oid), 2), "変更後の点数": round(v, 2), "変更後の順位": i + 1} for i, (n, v, oid) in enumerate(alternate)]), hide_index=True, use_container_width=True)
                st.caption("この画面の重要度変更は試算のみ。元の判断基準は変更されないよ。")

with tabs[6]:
    d = current_decision()
    if d:
        st.subheader("直感と気持ちを記録")
        with st.form(f"feelings_{d['id']}"):
            intuition = st.text_area("本当はどれを選びたい？", value=d.get("intuition", ""))
            concerns = st.text_area("何が不安？", value=d.get("concerns", ""))
            nonnegotiable = st.text_area("譲れない条件は？", value=d.get("nonnegotiable", ""))
            if st.form_submit_button("気持ちを保存"):
                d.update(intuition=intuition, concerns=concerns, nonnegotiable=nonnegotiable)
                rerun_saved()
        st.divider()
        st.subheader("決定と振り返り")
        with st.form(f"decision_result_{d['id']}"):
            options = ["未決定"] + [o["name"] for o in d["options"]]
            chosen = d.get("chosen", "")
            selected = st.selectbox("実際に選んだもの", options, index=options.index(chosen) if chosen in options else 0)
            reason = st.text_area("選んだ理由", value=d.get("reason", ""))
            satisfaction = st.slider("決定後の満足度（未評価なら0）", 0, 5, int(d.get("satisfaction") or 0))
            reflection = st.text_area("結果・予想と違ったこと・学び", value=d.get("reflection", ""))
            if st.form_submit_button("決定を保存", type="primary"):
                d.update(chosen="" if selected == "未決定" else selected, reason=reason, satisfaction=satisfaction or None, reflection=reflection, status="検討中" if selected == "未決定" else "決定済み")
                rerun_saved()

with tabs[7]:
    st.subheader("バックアップと復元")
    raw = json.dumps(st.session_state.db, ensure_ascii=False, indent=2)
    st.download_button("📥 JSONバックアップを保存", raw, file_name="decision_compass_backup.json", mime="application/json")
    uploaded = st.file_uploader("バックアップJSONを選択", type=["json"])
    if uploaded and st.button("バックアップから復元（現在のデータを上書き）"):
        try:
            restored = validate(json.loads(uploaded.getvalue().decode("utf-8")))
            st.session_state.db = restored
            st.session_state.pop("active_decision", None)
            rerun_saved("復元したよ！")
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
            st.error(f"復元できませんでした: {exc}")
    st.divider()
    d = current_decision()
    if d:
        st.subheader("テーマを編集")
        with st.form(f"edit_decision_{d['id']}"):
            title = st.text_input("タイトル", value=d["title"])
            category = st.selectbox("カテゴリー", CATEGORIES, index=CATEGORIES.index(d.get("category", "その他")) if d.get("category") in CATEGORIES else len(CATEGORIES) - 1)
            feeling = st.text_area("今の気持ち", value=d.get("feeling", ""))
            if st.form_submit_button("テーマを更新"):
                if title.strip():
                    d.update(title=title.strip(), category=category, feeling=feeling)
                    rerun_saved()
                else:
                    st.error("タイトルを入力してね。")
        st.subheader("選択肢・判断基準の削除")
        for opt in list(d["options"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"選択肢：{opt['name']}")
            if col2.button("削除", key=f"delete_option_{opt['id']}", disabled=len(d["options"]) <= 2):
                d["options"].remove(opt)
                if d.get("chosen") == opt["name"]:
                    d.update(chosen="", status="検討中")
                rerun_saved()
        for c in list(d["criteria"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"判断基準：{c['name']}")
            if col2.button("削除", key=f"delete_criterion_{c['id']}"):
                d["criteria"].remove(c)
                for opt in d["options"]:
                    opt.get("ratings", {}).pop(c["id"], None)
                rerun_saved()
        st.divider()
        st.warning("テーマを削除すると、その選択肢・判断基準・評価・振り返りもすべて消えるよ。")
        confirm = st.checkbox("このテーマを削除することを確認しました", key=f"confirm_{d['id']}")
        if st.button("🗑️ テーマを削除", disabled=not confirm):
            st.session_state.db["decisions"] = [x for x in st.session_state.db["decisions"] if x["id"] != d["id"]]
            st.session_state.pop("active_decision", None)
            rerun_saved("テーマを削除したよ。")
