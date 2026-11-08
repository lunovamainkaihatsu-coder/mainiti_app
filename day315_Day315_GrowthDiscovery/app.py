import json
import os
import uuid
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="いつの間にかできてた！", page_icon="🌱", layout="wide")
FILE = Path(__file__).resolve().parent / "data" / "growth.json"
CATEGORIES = ["💻 学習", "💼 仕事", "🏃 健康", "🏠 生活", "🤝 人間関係", "🧠 メンタル", "🎨 趣味", "📦 その他"]
ACTIONS = ["毎日の練習", "繰り返し挑戦", "人に教わった", "本・動画で学んだ", "環境を変えた", "休息を取った", "その他"]
EVIDENCE_TYPES = ["自分でできた", "数値・記録", "他者からの評価", "作品・成果物", "その他"]


def new_id():
    return uuid.uuid4().hex


def stamp():
    return datetime.now().isoformat(timespec="seconds")


def blank():
    return {"growths": [], "evidences": [], "reviews": []}


def validate(obj):
    if not isinstance(obj, dict) or any(not isinstance(obj.get(k), list) for k in blank()):
        raise ValueError("growths / evidences / reviews の配列が必要です")
    ids = set()
    for group in blank():
        for item in obj[group]:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                raise ValueError("記録のIDが不正です")
            if item["id"] in ids:
                raise ValueError("IDが重複しています")
            ids.add(item["id"])
    gids = {g["id"] for g in obj["growths"]}
    for g in obj["growths"]:
        if not isinstance(g.get("title"), str) or not g["title"].strip():
            raise ValueError("成長のタイトルが不正です")
        if type(g.get("impact")) is not int or not 1 <= g["impact"] <= 5:
            raise ValueError("成長実感度は1～5で指定してください")
        for k in ("before_value", "after_value"):
            if g.get(k) is not None and (type(g[k]) not in (float, int) or not -1e12 <= g[k] <= 1e12):
                raise ValueError("比較数値が不正です")
    for group in ("evidences", "reviews"):
        for item in obj[group]:
            if item.get("growth_id") not in gids:
                raise ValueError("紐づく成長記録が存在しません")
            if group == "reviews":
                for k in ("skill", "confidence"):
                    if type(item.get(k)) is not int or not 1 <= item[k] <= 5:
                        raise ValueError("再評価スコアは1～5です")
    return obj


def save(obj):
    validate(obj)
    FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = FILE.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(temp, FILE)


def load():
    if not FILE.exists():
        result = blank()
        save(result)
        return result
    try:
        with FILE.open(encoding="utf-8") as f:
            return validate(json.load(f))
    except (OSError, ValueError, TypeError) as e:
        st.error(f"データを読み込めません。元ファイルは上書きしていません: {e}")
        st.stop()


def get_growth(gid):
    return next((g for g in db["growths"] if g["id"] == gid), None)


def related(group, gid):
    return sorted((x for x in db[group] if x["growth_id"] == gid), key=lambda x: (x.get("day", ""), x.get("created_at", "")), reverse=True)


def choices():
    return {f"{g['title']} [{g['id'][:7]}]": g["id"] for g in db["growths"]}


def selection(label, key):
    opts = choices()
    return opts[st.selectbox(label, list(opts), key=key)]


def safe_date(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return date.today()


def idx(options, value):
    return options.index(value) if value in options else 0


def improvement(g):
    a, b = g.get("before_value"), g.get("after_value")
    if a is None or b is None or a == 0:
        return None
    if g.get("direction") == "小さいほど良い":
        return (a - b) / abs(a) * 100
    return (b - a) / abs(a) * 100


def show_growth(g, detail=True):
    with st.container(border=True):
        st.markdown(f"#### {'❤️ ' if g.get('favorite') else '🌱 '}{g['title']}")
        st.caption(f"{g.get('category', '')} ｜ 発見日 {g.get('day', '')} ｜ 成長実感 {'★' * g['impact']}{'☆' * (5-g['impact'])}")
        left, right = st.columns(2)
        with left:
            st.markdown("**🌧️ 以前**")
            st.write(g.get("before") or "未記入")
        with right:
            st.markdown("**☀️ 今**")
            st.write(g.get("after") or "未記入")
        pct = improvement(g)
        if pct is not None:
            st.metric("数値で見た改善率", f"{pct:+.1f}%")
        if detail:
            for name, key in (("気づいたきっかけ", "trigger"), ("役立った行動", "actions"), ("メモ", "note")):
                val = g.get(key)
                if val:
                    st.write(f"**{name}：** {', '.join(val) if isinstance(val, list) else val}")
            st.caption(f"📸 証拠 {len(related('evidences', g['id']))}件 ｜ 🔁 再評価 {len(related('reviews', g['id']))}件")


db = load()
growths = db["growths"]
st.markdown("""
<style>
.block-container {max-width:1280px;padding-top:1.5rem}
.hero {padding:30px 20px;border-radius:20px;text-align:center;background:linear-gradient(115deg,rgba(64,180,125,.16),rgba(255,200,95,.14));margin-bottom:22px}
</style>
<div class="hero"><small>👣✨ DAY 315 / 365</small><h1>いつの間にかできてた！</h1>
<p>昨日までの自分が、今日の自分を見たら驚くかもしれない。</p></div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🏠 ホーム", "🌱 成長を登録", "🔄 Before / After", "📸 成長の証拠", "📖 成長アルバム", "🔁 再評価", "📊 分析", "🛠️ 管理"])

with tabs[0]:
    st.subheader("🏠 成長ダッシュボード")
    metrics = [len(growths), len(db["evidences"]), sum(bool(g.get("favorite")) for g in growths), len(db["reviews"])]
    for col, name, n in zip(st.columns(4), ["🌱 発見した成長", "📸 成長の証拠", "❤️ お気に入り", "🔁 再評価"], metrics):
        col.metric(name, n)
    if not growths:
        st.info("まずは『🌱 成長を登録』から、小さな成長をひとつ残してみよう！")
    else:
        st.markdown("### 最近の発見")
        for g in sorted(growths, key=lambda x: x.get("created_at", ""), reverse=True)[:3]:
            show_growth(g, False)

with tabs[1]:
    st.subheader("🌱 成長を発見した！")
    with st.form("new_growth", clear_on_submit=True):
        title = st.text_input("成長のタイトル *", placeholder="例：Pythonのfor文を自分で書けた")
        cat = st.selectbox("カテゴリー", CATEGORIES)
        day = st.date_input("気づいた日", value=date.today(), max_value=date.today())
        c1, c2 = st.columns(2)
        with c1:
            before = st.text_area("🌧️ 以前の自分", placeholder="前はどうだった？")
        with c2:
            after = st.text_area("☀️ 今の自分", placeholder="今は何ができる？")
        trigger = st.text_area("成長に気づいた瞬間")
        actions = st.multiselect("成長に役立った行動", ACTIONS)
        impact = st.slider("成長実感度", 1, 5, 4)
        note = st.text_area("自由メモ")
        favorite = st.checkbox("❤️ お気に入りにする")
        numeric = st.checkbox("数値でも比較する")
        if numeric:
            n1, n2 = st.columns(2)
            with n1:
                before_value = st.number_input("以前の数値", value=30.0)
            with n2:
                after_value = st.number_input("今の数値", value=10.0)
            unit = st.text_input("単位", value="分")
            direction = st.radio("改善の方向", ["小さいほど良い", "大きいほど良い"], horizontal=True)
        else:
            before_value = after_value = None
            unit, direction = "", "大きいほど良い"
        if st.form_submit_button("🌱 成長を保存", type="primary", use_container_width=True):
            if not title.strip():
                st.warning("タイトルを入力してね。")
            else:
                growths.append(dict(id=new_id(), title=title.strip(), category=cat, day=str(day), before=before.strip(), after=after.strip(), trigger=trigger.strip(), actions=actions, impact=impact, note=note.strip(), favorite=favorite, before_value=before_value, after_value=after_value, unit=unit.strip(), direction=direction, created_at=stamp(), updated_at=stamp()))
                save(db)
                st.rerun()

with tabs[2]:
    st.subheader("🔄 昔の自分と今の自分")
    if not growths:
        st.info("まず成長を登録しよう。")
    else:
        gid = selection("比較する成長", "compare_choice")
        g = get_growth(gid)
        show_growth(g)
        a, b = g.get("before_value"), g.get("after_value")
        if a is not None and b is not None:
            st.markdown("### 数値比較")
            c1, c2 = st.columns(2)
            c1.metric("以前", f"{a:g} {g.get('unit','')}")
            c2.metric("今", f"{b:g} {g.get('unit','')}")
            pct = improvement(g)
            if pct is None:
                st.caption("以前の数値が0のため、割合は算出できません。")
            else:
                st.success(f"改善率：{pct:+.1f}%（{g.get('direction')}）" if pct >= 0 else f"変化率：{pct:+.1f}%（改善方向とは逆の変化）")
        else:
            st.caption("数値比較は未登録。文章での成長も大切な記録だよ。")

with tabs[3]:
    st.subheader("📸 成長の証拠")
    if not growths:
        st.info("まず成長を登録しよう。")
    else:
        gid = selection("証拠を残す成長", "evidence_choice")
        with st.form("new_evidence", clear_on_submit=True):
            kind = st.selectbox("証拠の種類", EVIDENCE_TYPES)
            day = st.date_input("証拠を確認した日", value=date.today(), max_value=date.today())
            content = st.text_area("具体的な証拠 *", placeholder="例：練習問題をヒントなしで解けた")
            link = st.text_input("関連リンク（任意）", placeholder="https://...")
            if st.form_submit_button("📸 証拠を保存", type="primary"):
                if not content.strip():
                    st.warning("証拠の内容を入力してね。")
                else:
                    db["evidences"].append(dict(id=new_id(), growth_id=gid, kind=kind, day=str(day), content=content.strip(), link=link.strip(), created_at=stamp()))
                    save(db)
                    st.rerun()
        st.markdown("### 保存した証拠")
        for e in related("evidences", gid):
            with st.container(border=True):
                st.caption(f"{e.get('kind', '')} ｜ {e.get('day', '')}")
                st.write(e.get("content", ""))
                if e.get("link"):
                    st.code(e["link"], language=None)

with tabs[4]:
    st.subheader("📖 成長アルバム")
    if not growths:
        st.info("記録した成長がここに並ぶよ。")
    else:
        query = st.text_input("🔍 キーワード検索")
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("カテゴリー", ["すべて"] + CATEGORIES)
        fav = c2.checkbox("❤️ お気に入りのみ")
        order = c3.selectbox("並べ替え", ["新しい順", "古い順", "成長実感度順"])
        filtered = [g for g in growths if (cat == "すべて" or g.get("category") == cat) and (not fav or g.get("favorite")) and query.lower() in " ".join(str(g.get(k, "")) for k in ("title", "before", "after", "trigger", "note")).lower()]
        if order == "成長実感度順":
            filtered.sort(key=lambda g: (g["impact"], g.get("day", "")), reverse=True)
        else:
            filtered.sort(key=lambda g: (g.get("day", ""), g.get("created_at", "")), reverse=(order == "新しい順"))
        st.caption(f"{len(filtered)}件")
        for g in filtered:
            show_growth(g)

with tabs[5]:
    st.subheader("🔁 成長の再評価")
    if not growths:
        st.info("まず成長を登録しよう。")
    else:
        gid = selection("再評価する成長", "review_choice")
        show_growth(get_growth(gid), False)
        with st.form("new_review", clear_on_submit=True):
            day = st.date_input("振り返った日", value=date.today(), max_value=date.today())
            c1, c2 = st.columns(2)
            skill = c1.slider("今の習熟度", 1, 5, 3)
            confidence = c2.slider("自信の程度", 1, 5, 3)
            progress = st.text_area("さらにできるようになったこと")
            next_goal = st.text_area("次の目標")
            if st.form_submit_button("🔁 再評価を保存", type="primary"):
                db["reviews"].append(dict(id=new_id(), growth_id=gid, day=str(day), skill=skill, confidence=confidence, progress=progress.strip(), next_goal=next_goal.strip(), created_at=stamp()))
                save(db)
                st.rerun()
        st.markdown("### 再評価履歴")
        for r in related("reviews", gid):
            with st.container(border=True):
                st.caption(r.get("day", ""))
                a, b = st.columns(2)
                a.metric("習熟度", f"{r['skill']} / 5")
                b.metric("自信", f"{r['confidence']} / 5")
                if r.get("progress"):
                    st.write("**新しい成長：**", r["progress"])
                if r.get("next_goal"):
                    st.write("**次の目標：**", r["next_goal"])

with tabs[6]:
    st.subheader("📊 成長の分析")
    if not growths:
        st.info("記録が増えるとグラフが表示されるよ。")
    else:
        c1, c2 = st.columns(2)
        c1.metric("平均成長実感度", f"{sum(g['impact'] for g in growths)/len(growths):.1f} / 5")
        c2.metric("数値比較できる成長", sum(improvement(g) is not None for g in growths))
        st.markdown("### カテゴリー別")
        st.bar_chart(pd.Series(Counter(g.get("category", "その他") for g in growths), name="件数"))
        st.markdown("### 月別の発見")
        months = Counter(g.get("day", "")[:7] for g in growths if g.get("day"))
        st.bar_chart(pd.Series(dict(sorted(months.items())), name="件数"))
        st.markdown("### 成長実感度")
        impacts = Counter(g["impact"] for g in growths)
        st.bar_chart(pd.Series({str(i): impacts.get(i, 0) for i in range(1, 6)}, name="件数"))
        st.markdown("### 成長に役立った行動")
        actions_count = Counter(a for g in growths for a in g.get("actions", []))
        if actions_count:
            st.bar_chart(pd.Series(actions_count, name="記録数"))
        else:
            st.caption("まだ行動タグの記録はありません。")
        st.markdown("### 再評価の推移")
        if db["reviews"]:
            df = pd.DataFrame(db["reviews"])
            df["day"] = pd.to_datetime(df["day"], errors="coerce")
            df = df.dropna(subset=["day"])
            if not df.empty:
                st.line_chart(df.groupby("day")[["skill", "confidence"]].mean().sort_index())
                st.caption("同じ日に複数の成長を再評価した場合は平均値を表示します。")
        else:
            st.caption("まだ再評価履歴がありません。")

with tabs[7]:
    st.subheader("🛠️ 記録の編集・削除")
    if growths:
        gid = selection("編集する成長", "manage_choice")
        g = get_growth(gid)
        with st.form(f"edit_growth_{gid}"):
            title = st.text_input("タイトル", value=g["title"])
            cat = st.selectbox("カテゴリー", CATEGORIES, index=idx(CATEGORIES, g.get("category")))
            day = st.date_input("発見日", value=safe_date(g.get("day")), max_value=date.today())
            before = st.text_area("以前", value=g.get("before", ""))
            after = st.text_area("今", value=g.get("after", ""))
            trigger = st.text_area("気づいた瞬間", value=g.get("trigger", ""))
            actions = st.multiselect("役立った行動", ACTIONS, default=[a for a in g.get("actions", []) if a in ACTIONS])
            impact = st.slider("成長実感度", 1, 5, g["impact"])
            note = st.text_area("メモ", value=g.get("note", ""))
            favorite = st.checkbox("お気に入り", value=bool(g.get("favorite")))
            numeric = st.checkbox("数値比較を使用", value=g.get("before_value") is not None and g.get("after_value") is not None)
            if numeric:
                a = st.number_input("以前の数値", value=float(g.get("before_value") or 0))
                b = st.number_input("今の数値", value=float(g.get("after_value") or 0))
                unit = st.text_input("単位", value=g.get("unit", ""))
                direction = st.radio("改善の方向", ["小さいほど良い", "大きいほど良い"], index=idx(["小さいほど良い", "大きいほど良い"], g.get("direction")))
            else:
                a = b = None
                unit, direction = "", "大きいほど良い"
            if st.form_submit_button("💾 成長を更新", type="primary"):
                if not title.strip():
                    st.warning("タイトルは必須です。")
                else:
                    g.update(title=title.strip(), category=cat, day=str(day), before=before.strip(), after=after.strip(), trigger=trigger.strip(), actions=actions, impact=impact, note=note.strip(), favorite=favorite, before_value=a, after_value=b, unit=unit.strip(), direction=direction, updated_at=stamp())
                    save(db)
                    st.rerun()
        st.divider()
        st.markdown("### 📸 証拠の編集・削除")
        evs = related("evidences", gid)
        if evs:
            eopts = {f"{e.get('content','')[:25]} [{e['id'][:7]}]": e["id"] for e in evs}
            eid = eopts[st.selectbox("証拠を選択", list(eopts), key=f"ev_select_{gid}")]
            e = next(x for x in evs if x["id"] == eid)
            with st.form(f"edit_ev_{eid}"):
                kind = st.selectbox("種類", EVIDENCE_TYPES, index=idx(EVIDENCE_TYPES, e.get("kind")))
                day = st.date_input("確認日", value=safe_date(e.get("day")), max_value=date.today())
                content = st.text_area("証拠の内容", value=e.get("content", ""))
                link = st.text_input("関連リンク", value=e.get("link", ""))
                if st.form_submit_button("💾 証拠を更新"):
                    if not content.strip():
                        st.warning("内容を入力してね。")
                    else:
                        e.update(kind=kind, day=str(day), content=content.strip(), link=link.strip())
                        save(db)
                        st.rerun()
            if st.checkbox("この証拠を削除する", key=f"check_ev_{eid}") and st.button("🗑️ 証拠を削除", key=f"del_ev_{eid}"):
                db["evidences"] = [x for x in db["evidences"] if x["id"] != eid]
                save(db)
                st.rerun()
        else:
            st.caption("証拠はまだありません。")
        st.divider()
        st.markdown("### 🔁 再評価の編集・削除")
        revs = related("reviews", gid)
        if revs:
            ropts = {f"{r.get('day','')} [{r['id'][:7]}]": r["id"] for r in revs}
            rid = ropts[st.selectbox("再評価を選択", list(ropts), key=f"rv_select_{gid}")]
            r = next(x for x in revs if x["id"] == rid)
            with st.form(f"edit_rev_{rid}"):
                day = st.date_input("再評価日", value=safe_date(r.get("day")), max_value=date.today())
                skill = st.slider("習熟度", 1, 5, r["skill"])
                confidence = st.slider("自信", 1, 5, r["confidence"])
                progress = st.text_area("新しい成長", value=r.get("progress", ""))
                next_goal = st.text_area("次の目標", value=r.get("next_goal", ""))
                if st.form_submit_button("💾 再評価を更新"):
                    r.update(day=str(day), skill=skill, confidence=confidence, progress=progress.strip(), next_goal=next_goal.strip())
                    save(db)
                    st.rerun()
            if st.checkbox("この再評価を削除する", key=f"check_rv_{rid}") and st.button("🗑️ 再評価を削除", key=f"del_rv_{rid}"):
                db["reviews"] = [x for x in db["reviews"] if x["id"] != rid]
                save(db)
                st.rerun()
        else:
            st.caption("再評価はまだありません。")
        st.divider()
        st.markdown("### ⚠️ 成長記録を完全削除")
        st.warning("この成長に紐づく証拠と再評価もすべて削除されます。")
        if st.checkbox("関連データを含めて完全削除する", key=f"check_g_{gid}") and st.button("🗑️ 完全削除", key=f"del_g_{gid}"):
            db["growths"] = [x for x in db["growths"] if x["id"] != gid]
            for group in ("evidences", "reviews"):
                db[group] = [x for x in db[group] if x["growth_id"] != gid]
            save(db)
            st.rerun()
    else:
        st.info("編集できる成長記録はまだありません。")
    st.divider()
    st.subheader("💾 バックアップと復元")
    st.download_button("⬇️ JSONバックアップを保存", data=json.dumps(db, ensure_ascii=False, indent=2), file_name=f"growth_backup_{date.today()}.json", mime="application/json")
    st.warning("復元すると現在の全データが置き換わります。先にバックアップを取ってね。")
    upload = st.file_uploader("復元するJSONファイル", type="json")
    if upload is not None:
        try:
            restored = validate(json.loads(upload.getvalue().decode("utf-8")))
            st.success(f"確認OK：成長 {len(restored['growths'])}件 / 証拠 {len(restored['evidences'])}件 / 再評価 {len(restored['reviews'])}件")
            if st.checkbox("現在のデータを置き換えることに同意する") and st.button("📤 復元を実行", type="primary"):
                save(restored)
                st.rerun()
        except (ValueError, TypeError, UnicodeDecodeError) as e:
            st.error(f"復元ファイルに問題があります：{e}")

st.divider()
st.caption("👣✨ Day315 / 365 — 昨日までの自分が、今日の自分を見たら驚くかもしれない。")
