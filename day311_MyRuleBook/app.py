
import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="自分ルール図鑑",
    page_icon="📜",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "rules.json"

CATEGORIES = [
    "💼 仕事",
    "💰 お金",
    "🧠 メンタル",
    "❤️ 家族・恋愛",
    "🤝 人間関係",
    "📚 学習",
    "💪 健康",
    "⏰ 時間",
    "🌱 人生",
    "📦 その他",
]

STATUSES = [
    "🌱 実践中",
    "🧪 お試し中",
    "⏸️ お休み中",
    "📦 卒業した",
]

PRACTICE_RESULTS = [
    "✅ 守れた",
    "🟡 一部守れた",
    "❌ 守れなかった",
    "⚖️ 例外を適用した",
]

REVIEW_DECISIONS = [
    "✅ そのまま続ける",
    "🔄 少し修正する",
    "⏸️ 一時的に休む",
    "📦 卒業する",
    "🌱 再開する",
]


# =========================================================
# UTILITIES
# =========================================================

def uid():
    return str(uuid.uuid4())


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def today_iso():
    return date.today().isoformat()


def parse_date(value):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def stars(value):
    try:
        n = max(0, min(5, int(value)))
        return "★" * n + "☆" * (5 - n)
    except (ValueError, TypeError):
        return "☆☆☆☆☆"


def valid_choice(value, choices, fallback=0):
    return choices.index(value) if value in choices else fallback


def rule_label(rule):
    return f"{rule['title']} [{rule['id'][:8]}]"


def empty_data():
    return {
        "rules": [],
        "practices": [],
        "revisions": [],
    }


def validate_data(obj):
    if not isinstance(obj, dict):
        raise ValueError("データ全体がJSONオブジェクトではありません。")

    for key in ("rules", "practices", "revisions"):
        if key not in obj or not isinstance(obj[key], list):
            raise ValueError(f"{key} が配列ではありません。")

        if any(not isinstance(item, dict) for item in obj[key]):
            raise ValueError(f"{key} に不正なデータがあります。")

    all_ids = []

    for key in ("rules", "practices", "revisions"):
        for item in obj[key]:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                raise ValueError(f"{key} にIDのない記録があります。")
            all_ids.append(item_id)

    if len(all_ids) != len(set(all_ids)):
        raise ValueError("IDが重複しています。")

    rule_ids = {r["id"] for r in obj["rules"]}

    for key in ("practices", "revisions"):
        for item in obj[key]:
            if item.get("rule_id") not in rule_ids:
                raise ValueError(
                    f"{key} に存在しないルールへの参照があります。"
                )

    for rule in obj["rules"]:
        if not isinstance(rule.get("title"), str):
            raise ValueError("ルール名が不正です。")

    return obj


def save_data(obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temp = DATA_FILE.with_suffix(".tmp")

    with temp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    os.replace(temp, DATA_FILE)


def load_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        obj = empty_data()
        save_data(obj)
        return obj

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            obj = json.load(f)

        validate_data(obj)
        return obj

    except (OSError, ValueError, TypeError) as exc:
        st.error(
            "データを読み込めませんでした。"
            "既存ファイルは上書きせず、そのまま保護しています。"
        )
        st.code(str(exc))
        st.stop()


def rule_by_id(rule_id):
    return next(
        (r for r in data["rules"] if r["id"] == rule_id),
        None,
    )


def practices_of(rule_id):
    return sorted(
        [
            p for p in data["practices"]
            if p.get("rule_id") == rule_id
        ],
        key=lambda x: (
            x.get("practice_date", ""),
            x.get("created_at", ""),
        ),
    )


def revisions_of(rule_id):
    return sorted(
        [
            r for r in data["revisions"]
            if r.get("rule_id") == rule_id
        ],
        key=lambda x: (
            x.get("review_date", ""),
            x.get("created_at", ""),
        ),
    )


def practice_stats(rule_id):
    items = practices_of(rule_id)
    values = [
        int(p["helpfulness"])
        for p in items
        if isinstance(p.get("helpfulness"), int)
    ]
    return {
        "count": len(items),
        "average": sum(values) / len(values) if values else None,
        "last": items[-1]["practice_date"] if items else None,
    }


def average_label(value):
    return f"{value:.1f}" if value is not None else "—"


def add_rule(
    title, category, reason, situation, exception,
    importance, status, favorite,
):
    rule = {
        "id": uid(),
        "title": title,
        "category": category,
        "reason": reason,
        "situation": situation,
        "exception": exception,
        "importance": importance,
        "status": status,
        "favorite": favorite,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    data["rules"].append(rule)
    save_data(data)


def add_practice(
    rule_id, practice_date, situation,
    result, helpfulness, outcome,
):
    data["practices"].append({
        "id": uid(),
        "rule_id": rule_id,
        "practice_date": str(practice_date),
        "situation": situation,
        "result": result,
        "helpfulness": helpfulness,
        "outcome": outcome,
        "created_at": now_iso(),
    })
    save_data(data)


def add_revision(
    rule_id, review_date, usefulness,
    decision, new_title, new_exception, note,
):
    rule = rule_by_id(rule_id)

    if not rule:
        return

    old_title = rule["title"]
    old_exception = rule.get("exception", "")
    old_status = rule.get("status", STATUSES[0])

    new_status = old_status

    if decision == "⏸️ 一時的に休む":
        new_status = "⏸️ お休み中"
    elif decision == "📦 卒業する":
        new_status = "📦 卒業した"
    elif decision == "🌱 再開する":
        new_status = "🌱 実践中"

    data["revisions"].append({
        "id": uid(),
        "rule_id": rule_id,
        "review_date": str(review_date),
        "usefulness": usefulness,
        "decision": decision,
        "old_title": old_title,
        "new_title": new_title,
        "old_exception": old_exception,
        "new_exception": new_exception,
        "old_status": old_status,
        "new_status": new_status,
        "note": note,
        "created_at": now_iso(),
    })

    if decision == "🔄 少し修正する":
        rule["title"] = new_title
        rule["exception"] = new_exception

    rule["status"] = new_status
    rule["updated_at"] = now_iso()

    save_data(data)


def delete_rule(rule_id):
    data["rules"] = [
        r for r in data["rules"] if r["id"] != rule_id
    ]
    data["practices"] = [
        p for p in data["practices"]
        if p["rule_id"] != rule_id
    ]
    data["revisions"] = [
        r for r in data["revisions"]
        if r["rule_id"] != rule_id
    ]
    save_data(data)


def build_manual():
    lines = [
        "# 📖 MY LIFE MANUAL",
        "",
        f"作成日：{today_iso()}",
        "",
        "自分の経験から生まれた、人生の取扱説明書。",
        "",
    ]

    for chapter, category in enumerate(CATEGORIES, start=1):
        rules = [
            r for r in data["rules"]
            if r.get("category") == category
        ]

        if not rules:
            continue

        lines.append(f"## 第{chapter}章：{category}")
        lines.append("")

        for i, rule in enumerate(rules, start=1):
            lines.append(f"### {i:02d}. {rule['title']}")
            lines.append("")
            lines.append(f"- 状態：{rule.get('status', '')}")
            lines.append(
                f"- 重要度：{stars(rule.get('importance', 3))}"
            )

            if rule.get("reason"):
                lines.append(f"- 理由：{rule['reason']}")

            if rule.get("situation"):
                lines.append(f"- 使う場面：{rule['situation']}")

            if rule.get("exception"):
                lines.append(f"- 例外：{rule['exception']}")

            stats = practice_stats(rule["id"])
            lines.append(f"- 実践回数：{stats['count']}回")
            lines.append(
                f"- 平均役立ち度：{average_label(stats['average'])}"
            )
            lines.append("")

    lines += [
        "---",
        "",
        "自分の人生の取扱説明書は、自分で書いていい。📜",
    ]

    return "\n".join(lines)


# =========================================================
# INITIALIZE
# =========================================================

data = load_data()
rules = data["rules"]
practices = data["practices"]
revisions = data["revisions"]

today = date.today()


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1300px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .hero {
        padding: 38px 22px;
        text-align: center;
        border-radius: 25px;
        background: linear-gradient(
            135deg,
            rgba(180,140,70,.12),
            rgba(90,160,120,.10)
        );
        margin-bottom: 24px;
    }
    .hero h1 {
        margin-bottom: 8px;
    }
    [data-testid="stMetric"] {
        padding: 14px;
        border-radius: 15px;
        border: 1px solid rgba(150,150,150,.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div>📜🧭 DAY 311 / 365</div>
        <h1>自分ルール図鑑</h1>
        <p>自分の経験から、自分だけの人生の取扱説明書を作ろう。</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

(
    tab_home,
    tab_add,
    tab_practice,
    tab_review,
    tab_manual,
    tab_ranking,
    tab_analysis,
    tab_manage,
) = st.tabs([
    "🏠 ホーム",
    "📜 ルール登録",
    "🌱 実践記録",
    "🔍 ルール見直し",
    "📖 人生の取扱説明書",
    "🏆 ランキング",
    "📊 分析",
    "🛠️ 管理",
])


# =========================================================
# 1. HOME
# =========================================================

with tab_home:
    st.subheader("🏠 今日の自分ルール")

    ratings = [
        p["helpfulness"]
        for p in practices
        if isinstance(p.get("helpfulness"), int)
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📜 登録ルール", len(rules))
    c2.metric("🌱 実践記録", len(practices))
    c3.metric(
        "⭐ 平均役立ち度",
        average_label(
            sum(ratings) / len(ratings) if ratings else None
        ),
    )
    c4.metric(
        "🔄 改訂・見直し",
        len(revisions),
    )

    if not rules:
        st.info(
            "まだルールがありません。"
            "「📜 ルール登録」から最初のルールを作ろう！"
        )
    else:
        st.divider()

        candidates = [
            r for r in rules
            if r.get("status") in STATUSES[:2]
        ] or rules

        candidate_ids = [r["id"] for r in candidates]

        if st.session_state.get("today_rule") not in candidate_ids:
            st.session_state["today_rule"] = random.choice(candidate_ids)

        selected = rule_by_id(st.session_state["today_rule"])

        with st.container(border=True):
            st.caption("📜 TODAY'S RULE")
            st.markdown(f"### {selected['title']}")
            st.write(
                f"{selected.get('category', '')} "
                f"｜重要度 {stars(selected.get('importance', 3))}"
            )

            if selected.get("reason"):
                st.write(f"**なぜ作った？** {selected['reason']}")

            if selected.get("exception"):
                st.info(f"⚖️ 例外：{selected['exception']}")

        if st.button("🎲 別のルールを見る"):
            alternatives = [
                x for x in candidate_ids
                if x != selected["id"]
            ]
            if alternatives:
                st.session_state["today_rule"] = random.choice(
                    alternatives
                )
            st.rerun()

        st.divider()
        st.subheader("📝 最近の実践")

        recent = sorted(
            practices,
            key=lambda p: (
                p.get("practice_date", ""),
                p.get("created_at", ""),
            ),
            reverse=True,
        )[:5]

        if not recent:
            st.caption("まだ実践記録はありません。")

        for p in recent:
            rule = rule_by_id(p["rule_id"])
            if not rule:
                continue

            with st.container(border=True):
                st.markdown(f"**{rule['title']}**")
                st.caption(
                    f"{p['practice_date']} ｜ {p['result']}"
                )
                st.write(
                    f"役立ち度：{stars(p['helpfulness'])}"
                )
                if p.get("outcome"):
                    st.write(p["outcome"])


# =========================================================
# 2. ADD RULE
# =========================================================

with tab_add:
    st.subheader("📜 新しい自分ルール")

    st.caption(
        "完璧なルールでなくて大丈夫。"
        "まずは自分が役立つと思った考えを残そう。"
    )

    with st.form("add_rule_form", clear_on_submit=True):
        title = st.text_input(
            "ルール",
            placeholder="例：迷ったら小さく試す",
        )

        category = st.selectbox("カテゴリー", CATEGORIES)

        reason = st.text_area(
            "このルールが生まれた理由",
            placeholder="どんな経験や気づきから生まれた？",
        )

        situation = st.text_area(
            "どんなときに使う？",
            placeholder="例：新しいことに挑戦するとき",
        )

        exception = st.text_area(
            "⚖️ 例外・無理しなくていい条件",
            placeholder="例：体調が悪いときは休んでいい",
        )

        importance = st.slider("重要度", 1, 5, 3)

        status = st.selectbox(
            "現在の状態",
            STATUSES,
            index=1,
        )

        favorite = st.checkbox("❤️ 大切なルールにする")

        submitted = st.form_submit_button(
            "📜 ルールを登録",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not title.strip():
                st.warning("ルールを入力してね。")
            else:
                add_rule(
                    title.strip(),
                    category,
                    reason.strip(),
                    situation.strip(),
                    exception.strip(),
                    importance,
                    status,
                    favorite,
                )
                st.rerun()


# =========================================================
# 3. PRACTICE
# =========================================================

with tab_practice:
    st.subheader("🌱 ルールを使った日")

    if not rules:
        st.info("先にルールを登録しよう。")
    else:
        options = {rule_label(r): r["id"] for r in rules}

        selected_label = st.selectbox(
            "使ったルール",
            list(options),
            key="practice_select",
        )

        rule_id = options[selected_label]
        selected = rule_by_id(rule_id)

        with st.container(border=True):
            st.markdown(f"### 📜 {selected['title']}")
            st.caption(selected.get("status", ""))

            if selected.get("exception"):
                st.write(
                    f"⚖️ 例外：{selected['exception']}"
                )

        with st.form("practice_form", clear_on_submit=True):
            practice_date = st.date_input(
                "実践した日",
                value=today,
                max_value=today,
            )

            situation = st.text_area(
                "どんな場面だった？",
                placeholder="例：新しい企画で迷った",
            )

            result = st.selectbox(
                "ルールを守れた？",
                PRACTICE_RESULTS,
            )

            helpfulness = st.slider(
                "どれくらい役立った？",
                1, 5, 3,
            )

            outcome = st.text_area(
                "結果・気づき",
                placeholder="例：小さく試したら前に進めた",
            )

            submitted = st.form_submit_button(
                "🌱 実践を記録",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                add_practice(
                    rule_id,
                    practice_date,
                    situation.strip(),
                    result,
                    helpfulness,
                    outcome.strip(),
                )
                st.rerun()

        st.divider()
        st.markdown("#### 📚 このルールの実践履歴")

        items = list(reversed(practices_of(rule_id)))

        if not items:
            st.caption("まだ実践履歴がありません。")

        for p in items[:20]:
            with st.expander(
                f"{p['practice_date']} "
                f"｜{p['result']} "
                f"｜{stars(p['helpfulness'])}"
            ):
                st.write(p.get("situation") or "場面の記録なし")
                st.write(p.get("outcome") or "結果の記録なし")


# =========================================================
# 4. REVIEW / REVISION
# =========================================================

with tab_review:
    st.subheader("🔍 ルールを見直す")

    if not rules:
        st.info("先にルールを登録しよう。")
    else:
        options = {rule_label(r): r["id"] for r in rules}

        selected_label = st.selectbox(
            "見直すルール",
            list(options),
            key="review_select",
        )

        rule_id = options[selected_label]
        rule = rule_by_id(rule_id)

        stats = practice_stats(rule_id)

        with st.container(border=True):
            st.markdown(f"### {rule['title']}")
            st.write(f"状態：{rule.get('status')}")
            st.write(f"実践：{stats['count']}回")
            st.write(
                f"平均役立ち度：{average_label(stats['average'])}"
            )

        with st.form("revision_form"):
            review_date = st.date_input(
                "見直した日",
                value=today,
                max_value=today,
            )

            usefulness = st.slider(
                "今もどれくらい役立つ？",
                1, 5, 3,
            )

            decision = st.selectbox(
                "今回の結論",
                REVIEW_DECISIONS,
            )

            new_title = st.text_input(
                "改訂後のルール",
                value=rule["title"],
            )

            new_exception = st.text_area(
                "改訂後の例外",
                value=rule.get("exception", ""),
            )

            note = st.text_area(
                "見直した理由・気づき",
                placeholder="何が変わった？",
            )

            submitted = st.form_submit_button(
                "🔍 見直しを保存",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if (
                    decision == "🔄 少し修正する"
                    and not new_title.strip()
                ):
                    st.warning("改訂後のルールを入力してね。")
                else:
                    add_revision(
                        rule_id,
                        review_date,
                        usefulness,
                        decision,
                        new_title.strip(),
                        new_exception.strip(),
                        note.strip(),
                    )
                    st.rerun()

        st.divider()
        st.markdown("#### 🕰️ ルールの進化履歴")

        history = list(reversed(revisions_of(rule_id)))

        if not history:
            st.caption("まだ見直し履歴がありません。")

        for rev in history:
            with st.container(border=True):
                st.markdown(
                    f"**{rev['review_date']}｜{rev['decision']}**"
                )
                st.write(
                    f"現在の役立ち度：{stars(rev['usefulness'])}"
                )

                if rev["old_title"] != rev["new_title"]:
                    st.write(f"以前：{rev['old_title']}")
                    st.write(f"改訂：{rev['new_title']}")

                if rev["old_exception"] != rev["new_exception"]:
                    st.write(
                        f"例外の変更："
                        f"{rev['old_exception']} → "
                        f"{rev['new_exception']}"
                    )

                if rev.get("note"):
                    st.caption(rev["note"])


# =========================================================
# 5. LIFE MANUAL
# =========================================================

with tab_manual:
    st.subheader("📖 MY LIFE MANUAL")

    st.caption(
        "自分の経験から生まれた、"
        "世界に一冊だけの人生の取扱説明書。"
    )

    if not rules:
        st.info("ルールを登録すると取扱説明書が育っていくよ。")
    else:
        chapter = 0

        for category in CATEGORIES:
            category_rules = [
                r for r in rules
                if r.get("category") == category
            ]

            if not category_rules:
                continue

            chapter += 1
            st.markdown(f"### 第{chapter}章：{category}")

            for i, rule in enumerate(category_rules, start=1):
                with st.container(border=True):
                    st.markdown(
                        f"#### {i:02d}. {rule['title']}"
                    )
                    st.caption(
                        f"{rule.get('status')} "
                        f"｜重要度 {stars(rule.get('importance', 3))}"
                    )

                    if rule.get("reason"):
                        st.write(
                            f"**生まれた理由：** {rule['reason']}"
                        )

                    if rule.get("situation"):
                        st.write(
                            f"**使う場面：** {rule['situation']}"
                        )

                    if rule.get("exception"):
                        st.info(
                            f"⚖️ 例外：{rule['exception']}"
                        )

                    stats = practice_stats(rule["id"])
                    st.caption(
                        f"実践 {stats['count']}回 "
                        f"｜平均役立ち度 "
                        f"{average_label(stats['average'])}"
                    )

        st.divider()

        st.download_button(
            "📥 人生の取扱説明書をMarkdownで保存",
            data=build_manual(),
            file_name=f"my_life_manual_{today_iso()}.md",
            mime="text/markdown",
            use_container_width=True,
        )


# =========================================================
# 6. RANKING
# =========================================================

with tab_ranking:
    st.subheader("🏆 自分ルールランキング")

    if not rules:
        st.info("まだランキング対象がありません。")
    else:
        ranking = []

        for rule in rules:
            stats = practice_stats(rule["id"])
            ranking.append({
                "id": rule["id"],
                "ルール": rule["title"],
                "カテゴリー": rule.get("category", ""),
                "状態": rule.get("status", ""),
                "実践回数": stats["count"],
                "平均役立ち度": stats["average"],
                "重要度": rule.get("importance", 3),
            })

        sort_mode = st.selectbox(
            "並び替え",
            [
                "実践回数が多い順",
                "平均役立ち度が高い順",
                "重要度が高い順",
            ],
        )

        if sort_mode == "実践回数が多い順":
            ranking.sort(
                key=lambda x: (
                    x["実践回数"],
                    x["平均役立ち度"] or 0,
                ),
                reverse=True,
            )
        elif sort_mode == "平均役立ち度が高い順":
            ranking.sort(
                key=lambda x: (
                    x["平均役立ち度"] is not None,
                    x["平均役立ち度"] or 0,
                    x["実践回数"],
                ),
                reverse=True,
            )
        else:
            ranking.sort(
                key=lambda x: (
                    x["重要度"],
                    x["実践回数"],
                ),
                reverse=True,
            )

        rows = []

        for index, item in enumerate(ranking, start=1):
            rows.append({
                "順位": index,
                "ルール": item["ルール"],
                "カテゴリー": item["カテゴリー"],
                "実践回数": item["実践回数"],
                "平均役立ち度": average_label(
                    item["平均役立ち度"]
                ),
                "重要度": stars(item["重要度"]),
                "状態": item["状態"],
            })

        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

        st.caption(
            "※実践回数が少なくても、"
            "自分にとって大切なルールは大切なまま。"
        )


# =========================================================
# 7. ANALYSIS
# =========================================================

with tab_analysis:
    st.subheader("📊 自分ルール分析")

    if not rules:
        st.info("記録が増えると分析できるよ。")
    else:
        category_counts = Counter(
            r.get("category", "📦 その他")
            for r in rules
        )

        status_counts = Counter(
            r.get("status", STATUSES[0])
            for r in rules
        )

        st.markdown("### 📚 カテゴリー分布")

        category_df = pd.DataFrame([
            {"カテゴリー": k, "ルール数": v}
            for k, v in category_counts.items()
        ])

        st.bar_chart(
            category_df.set_index("カテゴリー")
        )

        st.divider()
        st.markdown("### 🌱 ルールの状態")

        status_df = pd.DataFrame([
            {"状態": k, "件数": v}
            for k, v in status_counts.items()
        ])

        st.bar_chart(
            status_df.set_index("状態")
        )

        st.divider()
        st.markdown("### 🗓️ 月ごとの実践回数")

        monthly = Counter()

        for p in practices:
            d = parse_date(p.get("practice_date"))
            if d:
                monthly[d.strftime("%Y-%m")] += 1

        if monthly:
            monthly_df = pd.DataFrame([
                {"月": month, "実践回数": count}
                for month, count in sorted(monthly.items())
            ])

            st.bar_chart(monthly_df.set_index("月"))
        else:
            st.caption("まだ実践記録がありません。")

        st.divider()
        st.markdown("### ⚖️ 守れた・守れなかった")

        result_counts = Counter(
            p.get("result", "その他")
            for p in practices
        )

        if result_counts:
            result_df = pd.DataFrame([
                {"結果": k, "回数": v}
                for k, v in result_counts.items()
            ])

            st.bar_chart(result_df.set_index("結果"))

        st.divider()
        st.markdown("### 🔄 ルールの見直し")

        revision_counts = Counter(
            rev.get("decision", "その他")
            for rev in revisions
        )

        if revision_counts:
            revision_df = pd.DataFrame([
                {"結論": k, "回数": v}
                for k, v in revision_counts.items()
            ])

            st.bar_chart(revision_df.set_index("結論"))
        else:
            st.caption("まだ見直し履歴がありません。")

        st.divider()
        st.markdown("### ⭐ カテゴリー別の平均役立ち度")

        category_ratings = defaultdict(list)

        for p in practices:
            rule = rule_by_id(p["rule_id"])
            if rule:
                category_ratings[
                    rule.get("category", "📦 その他")
                ].append(p["helpfulness"])

        if category_ratings:
            rating_df = pd.DataFrame([
                {
                    "カテゴリー": category,
                    "平均役立ち度": round(
                        sum(values) / len(values), 2
                    ),
                    "実践回数": len(values),
                }
                for category, values in category_ratings.items()
            ])

            st.dataframe(
                rating_df,
                hide_index=True,
                use_container_width=True,
            )

            st.bar_chart(
                rating_df.set_index("カテゴリー")[
                    ["平均役立ち度"]
                ]
            )


# =========================================================
# 8. MANAGEMENT
# =========================================================

with tab_manage:
    st.subheader("🛠️ データ管理")

    if rules:
        options = {rule_label(r): r["id"] for r in rules}

        selected_label = st.selectbox(
            "編集するルール",
            list(options),
            key="manage_rule",
        )

        rule_id = options[selected_label]
        rule = rule_by_id(rule_id)

        # Selected ID in widget keys prevents stale values
        # from a previously selected rule.

        with st.form(f"edit_rule_{rule_id}"):
            edit_title = st.text_input(
                "ルール",
                value=rule["title"],
            )

            edit_category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=valid_choice(
                    rule.get("category"), CATEGORIES
                ),
            )

            edit_reason = st.text_area(
                "理由",
                value=rule.get("reason", ""),
            )

            edit_situation = st.text_area(
                "使う場面",
                value=rule.get("situation", ""),
            )

            edit_exception = st.text_area(
                "例外",
                value=rule.get("exception", ""),
            )

            edit_importance = st.slider(
                "重要度",
                1, 5,
                int(rule.get("importance", 3)),
            )

            edit_status = st.selectbox(
                "状態",
                STATUSES,
                index=valid_choice(
                    rule.get("status"), STATUSES
                ),
            )

            edit_favorite = st.checkbox(
                "❤️ 大切なルール",
                value=rule.get("favorite", False),
            )

            saved = st.form_submit_button(
                "💾 変更を保存",
                type="primary",
                use_container_width=True,
            )

            if saved:
                if not edit_title.strip():
                    st.warning("ルール名を入力してね。")
                else:
                    before = {
                        "title": rule["title"],
                        "exception": rule.get("exception", ""),
                        "status": rule.get("status", STATUSES[0]),
                    }

                    rule.update({
                        "title": edit_title.strip(),
                        "category": edit_category,
                        "reason": edit_reason.strip(),
                        "situation": edit_situation.strip(),
                        "exception": edit_exception.strip(),
                        "importance": edit_importance,
                        "status": edit_status,
                        "favorite": edit_favorite,
                        "updated_at": now_iso(),
                    })

                    if (
                        before["title"] != rule["title"]
                        or before["exception"] != rule["exception"]
                        or before["status"] != rule["status"]
                    ):
                        data["revisions"].append({
                            "id": uid(),
                            "rule_id": rule_id,
                            "review_date": today_iso(),
                            "usefulness": 3,
                            "decision": "🛠️ 管理画面で編集",
                            "old_title": before["title"],
                            "new_title": rule["title"],
                            "old_exception": before["exception"],
                            "new_exception": rule["exception"],
                            "old_status": before["status"],
                            "new_status": rule["status"],
                            "note": "管理画面から変更",
                            "created_at": now_iso(),
                        })

                    save_data(data)
                    st.rerun()

        st.divider()
        st.markdown("### 📝 実践記録の編集・削除")

        item_practices = practices_of(rule_id)

        if item_practices:
            p_options = {
                (
                    f"{p['practice_date']}｜{p['result']} "
                    f"[{p['id'][:8]}]"
                ): p["id"]
                for p in item_practices
            }

            p_label = st.selectbox(
                "実践記録",
                list(p_options),
                key=f"manage_practice_{rule_id}",
            )

            p_id = p_options[p_label]
            p = next(
                x for x in data["practices"]
                if x["id"] == p_id
            )

            with st.form(f"edit_practice_{p_id}"):
                p_date = st.date_input(
                    "実践日",
                    value=parse_date(p["practice_date"]) or today,
                    max_value=today,
                )
                p_situation = st.text_area(
                    "場面",
                    value=p.get("situation", ""),
                )
                p_result = st.selectbox(
                    "結果",
                    PRACTICE_RESULTS,
                    index=valid_choice(
                        p.get("result"), PRACTICE_RESULTS
                    ),
                )
                p_help = st.slider(
                    "役立ち度",
                    1, 5,
                    int(p.get("helpfulness", 3)),
                )
                p_outcome = st.text_area(
                    "気づき",
                    value=p.get("outcome", ""),
                )

                if st.form_submit_button("💾 実践記録を保存"):
                    p.update({
                        "practice_date": str(p_date),
                        "situation": p_situation.strip(),
                        "result": p_result,
                        "helpfulness": p_help,
                        "outcome": p_outcome.strip(),
                    })
                    save_data(data)
                    st.rerun()

            confirm_p = st.checkbox(
                "この実践記録を削除する",
                key=f"confirm_p_{p_id}",
            )

            if st.button(
                "🗑️ 実践記録を削除",
                disabled=not confirm_p,
                key=f"delete_p_{p_id}",
            ):
                data["practices"] = [
                    x for x in data["practices"]
                    if x["id"] != p_id
                ]
                save_data(data)
                st.rerun()
        else:
            st.caption("実践記録はありません。")

        st.divider()
        st.markdown("### 🕰️ 見直し履歴の削除")

        item_revisions = revisions_of(rule_id)

        if item_revisions:
            rev_options = {
                (
                    f"{r['review_date']}｜{r['decision']} "
                    f"[{r['id'][:8]}]"
                ): r["id"]
                for r in item_revisions
            }

            rev_label = st.selectbox(
                "見直し履歴",
                list(rev_options),
                key=f"manage_revision_{rule_id}",
            )

            rev_id = rev_options[rev_label]

            st.caption(
                "履歴を削除しても、"
                "現在のルール内容は変更されません。"
            )

            confirm_rev = st.checkbox(
                "この見直し履歴を削除する",
                key=f"confirm_rev_{rev_id}",
            )

            if st.button(
                "🗑️ 見直し履歴を削除",
                disabled=not confirm_rev,
                key=f"delete_rev_{rev_id}",
            ):
                data["revisions"] = [
                    x for x in data["revisions"]
                    if x["id"] != rev_id
                ]
                save_data(data)
                st.rerun()

        st.divider()
        st.markdown("### ⚠️ ルールを完全削除")

        st.warning(
            "このルールを削除すると、"
            "紐づく実践記録と見直し履歴も削除されます。"
        )

        confirm_rule = st.checkbox(
            "このルールと全履歴を削除する",
            key=f"confirm_rule_{rule_id}",
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=not confirm_rule,
            key=f"delete_rule_{rule_id}",
        ):
            delete_rule(rule_id)
            st.rerun()

    else:
        st.info("編集できるルールはまだありません。")

    st.divider()
    st.subheader("💾 バックアップ")

    backup_json = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップを保存",
        data=backup_json,
        file_name=f"my_rules_{today_iso()}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown("### 📤 バックアップから復元")

    st.warning(
        "復元すると現在の全データが置き換わります。"
        "先にバックアップをダウンロードしてください。"
    )

    uploaded = st.file_uploader(
        "復元するJSONファイル",
        type=["json"],
    )

    if uploaded is not None:
        try:
            restored = json.loads(
                uploaded.getvalue().decode("utf-8")
            )
            validate_data(restored)

            st.success(
                f"読み込み確認OK："
                f"ルール {len(restored['rules'])}件、"
                f"実践 {len(restored['practices'])}件、"
                f"見直し {len(restored['revisions'])}件"
            )

            confirm_restore = st.checkbox(
                "現在のデータを置き換えることに同意する"
            )

            if st.button(
                "📤 復元を実行",
                disabled=not confirm_restore,
                type="primary",
            ):
                save_data(restored)
                st.rerun()

        except (ValueError, UnicodeDecodeError) as exc:
            st.error(f"復元できないJSONです：{exc}")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:25px;">
        <p><b>人生に、たった一つの正解はない。</b></p>
        <p>
            でも、自分の経験から見つけた答えなら、<br>
            少しずつ増やしていける。
        </p>
        <p>
            自分を縛るためではなく、<br>
            自分を助けるためのルールを。
        </p>
        <h3>自分の人生の取扱説明書は、自分で書いていい。📜🧭</h3>
        <p><b>DAY 311 / 365 — COMPLETE 🔥</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)
