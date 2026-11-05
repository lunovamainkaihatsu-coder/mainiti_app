
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
# 基本設定
# =========================================================

st.set_page_config(
    page_title="これ、意外とよかった！",
    page_icon="💡",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "discoveries.json"

CATEGORIES = [
    "🍽️ 食事",
    "🌿 暮らし",
    "💼 仕事",
    "📚 学習",
    "🎮 趣味",
    "🏃 健康",
    "🤝 人間関係",
    "🛍️ 買い物",
    "🚶 お出かけ",
    "📦 その他",
]

LOW_EXPECTATION_REASONS = [
    "😐 興味がなかった",
    "🙄 面倒だと思っていた",
    "💰 お金がもったいないと思った",
    "⏰ 時間がかかりそうだった",
    "😟 苦手意識があった",
    "👤 人に勧められただけ",
    "🎲 たまたま試した",
    "📦 その他",
]

RETRY_RESULTS = [
    "✅ 今回もよかった！",
    "😊 まあまあよかった",
    "😐 普通だった",
    "💭 今回はいまいち",
]


# =========================================================
# 共通関数
# =========================================================

def uid():
    return str(uuid.uuid4())


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def today_iso():
    return date.today().isoformat()


def stars(value):
    try:
        value = max(0, min(5, int(value)))
        return "★" * value + "☆" * (5 - value)
    except (ValueError, TypeError):
        return "☆☆☆☆☆"


def gap_score(discovery):
    return (
        int(discovery["satisfaction"])
        - int(discovery["expectation"])
    )


def gap_label(gap):
    if gap >= 3:
        return "🎉 大当たり！"
    elif gap >= 1:
        return "✨ 期待以上！"
    elif gap == 0:
        return "😊 期待どおり"
    else:
        return "💭 期待とは違った"


def signed(value):
    return f"{value:+d}"


def empty_data():
    return {
        "discoveries": [],
        "retries": [],
    }


def validate_data(obj):
    if not isinstance(obj, dict):
        raise ValueError("JSON全体がオブジェクトではありません。")

    for key in ("discoveries", "retries"):
        if key not in obj or not isinstance(obj[key], list):
            raise ValueError(f"{key} が配列ではありません。")

        if any(not isinstance(x, dict) for x in obj[key]):
            raise ValueError(f"{key} に不正なデータがあります。")

    all_ids = []

    for key in ("discoveries", "retries"):
        for item in obj[key]:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                raise ValueError(f"{key} にIDのない記録があります。")
            all_ids.append(item_id)

    if len(all_ids) != len(set(all_ids)):
        raise ValueError("IDが重複しています。")

    discovery_ids = {
        d["id"] for d in obj["discoveries"]
    }

    for d in obj["discoveries"]:
        if not isinstance(d.get("title"), str):
            raise ValueError("発見タイトルが不正です。")

        for field in ("expectation", "satisfaction"):
            value = d.get(field)
            if type(value) is not int or not 1 <= value <= 5:
                raise ValueError(f"{field} は1〜5の整数です。")

    for r in obj["retries"]:
        if r.get("discovery_id") not in discovery_ids:
            raise ValueError(
                "存在しない発見に紐づく再チャレンジがあります。"
            )

        value = r.get("satisfaction")
        if type(value) is not int or not 1 <= value <= 5:
            raise ValueError(
                "再チャレンジの満足度が不正です。"
            )

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

        return validate_data(obj)

    except (OSError, ValueError, TypeError) as exc:
        st.error(
            "保存データを読み込めませんでした。"
            "ファイルは上書きせず保護しています。"
        )
        st.code(str(exc))
        st.stop()


def discovery_by_id(discovery_id):
    return next(
        (
            d for d in data["discoveries"]
            if d["id"] == discovery_id
        ),
        None,
    )


def retries_of(discovery_id):
    return sorted(
        [
            r for r in data["retries"]
            if r["discovery_id"] == discovery_id
        ],
        key=lambda x: (
            x.get("retry_date", ""),
            x.get("created_at", ""),
        ),
    )


def retry_stats(discovery_id):
    items = retries_of(discovery_id)

    if not items:
        return {
            "count": 0,
            "average": None,
            "last": None,
        }

    values = [r["satisfaction"] for r in items]

    return {
        "count": len(items),
        "average": sum(values) / len(values),
        "last": items[-1]["retry_date"],
    }


def average_label(value):
    return f"{value:.1f}" if value is not None else "—"


def discovery_label(d):
    return f"{d['title']} [{d['id'][:8]}]"


def add_discovery(
    title,
    category,
    discovery_date,
    expectation,
    satisfaction,
    low_reason,
    experience,
    good_point,
    lesson,
    favorite,
    want_retry,
):
    data["discoveries"].append({
        "id": uid(),
        "title": title,
        "category": category,
        "discovery_date": str(discovery_date),
        "expectation": expectation,
        "satisfaction": satisfaction,
        "low_reason": low_reason,
        "experience": experience,
        "good_point": good_point,
        "lesson": lesson,
        "favorite": favorite,
        "want_retry": want_retry,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })

    save_data(data)


def add_retry(
    discovery_id,
    retry_date,
    satisfaction,
    result,
    note,
):
    data["retries"].append({
        "id": uid(),
        "discovery_id": discovery_id,
        "retry_date": str(retry_date),
        "satisfaction": satisfaction,
        "result": result,
        "note": note,
        "created_at": now_iso(),
    })

    save_data(data)


def delete_discovery(discovery_id):
    data["discoveries"] = [
        d for d in data["discoveries"]
        if d["id"] != discovery_id
    ]

    data["retries"] = [
        r for r in data["retries"]
        if r["discovery_id"] != discovery_id
    ]

    save_data(data)


def parse_date(value):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def choice_index(value, choices):
    return choices.index(value) if value in choices else 0


def show_discovery(d, show_details=True):
    gap = gap_score(d)
    stats = retry_stats(d["id"])

    with st.container(border=True):
        left, right = st.columns([4, 1])

        with left:
            st.markdown(f"### 💡 {d['title']}")
            st.caption(
                f"{d.get('category', '')} "
                f"｜{d.get('discovery_date', '')}"
            )

        with right:
            st.metric("意外度", signed(gap))

        c1, c2 = st.columns(2)

        c1.write(
            f"**期待度** {stars(d['expectation'])}"
        )
        c2.write(
            f"**満足度** {stars(d['satisfaction'])}"
        )

        st.write(gap_label(gap))

        if d.get("favorite"):
            st.caption("❤️ お気に入り")

        if d.get("want_retry"):
            st.caption("🔁 またやりたい")

        if show_details:
            if d.get("experience"):
                st.write(
                    f"**何をした？** {d['experience']}"
                )

            if d.get("good_point"):
                st.write(
                    f"**どうよかった？** {d['good_point']}"
                )

            if d.get("lesson"):
                st.write(
                    f"**気づき：** {d['lesson']}"
                )

            st.caption(
                f"再チャレンジ {stats['count']}回 "
                f"｜再体験平均満足度 "
                f"{average_label(stats['average'])}"
            )


# =========================================================
# データ初期化
# =========================================================

data = load_data()
discoveries = data["discoveries"]
retries = data["retries"]
today = date.today()


# =========================================================
# デザイン
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
        padding: 40px 20px;
        text-align: center;
        border-radius: 25px;
        background: linear-gradient(
            135deg,
            rgba(255,190,70,.17),
            rgba(100,180,160,.12)
        );
        margin-bottom: 24px;
    }
    .hero h1 {
        margin-bottom: 8px;
    }
    [data-testid="stMetric"] {
        padding: 12px;
        border-radius: 14px;
        border: 1px solid rgba(150,150,150,.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div>💡✨ DAY 312 / 365</div>
        <h1>これ、意外とよかった！</h1>
        <p>
            期待していなかったことが、<br>
            思いがけず自分を幸せにする。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# タブ
# =========================================================

(
    tab_home,
    tab_add,
    tab_retry,
    tab_library,
    tab_ranking,
    tab_gacha,
    tab_analysis,
    tab_manage,
) = st.tabs([
    "🏠 ホーム",
    "💡 新しい発見",
    "🔁 もう一度やった",
    "📚 発見図鑑",
    "🏆 意外な当たり",
    "🎲 再発見ガチャ",
    "📊 分析",
    "🛠️ 管理",
])


# =========================================================
# 1. ホーム
# =========================================================

with tab_home:
    st.subheader("🏠 意外な発見ダッシュボード")

    gaps = [gap_score(d) for d in discoveries]

    big_hits = sum(g >= 3 for g in gaps)

    avg_gap = (
        sum(gaps) / len(gaps)
        if gaps else None
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💡 発見数", len(discoveries))
    c2.metric("🎉 大当たり", big_hits)
    c3.metric(
        "📊 平均意外度",
        f"{avg_gap:+.1f}" if avg_gap is not None else "—",
    )
    c4.metric("🔁 再チャレンジ", len(retries))

    if not discoveries:
        st.info(
            "まだ発見がありません。"
            "「💡 新しい発見」から登録してみよう！"
        )
    else:
        st.divider()
        st.markdown("### 🌟 最近の意外な発見")

        recent = sorted(
            discoveries,
            key=lambda d: (
                d.get("discovery_date", ""),
                d.get("created_at", ""),
            ),
            reverse=True,
        )[:3]

        for d in recent:
            show_discovery(d, show_details=False)

        st.divider()
        st.markdown("### 🎲 今日の再発見")

        candidates = [
            d for d in discoveries
            if d.get("want_retry")
        ] or discoveries

        ids = [d["id"] for d in candidates]

        if st.session_state.get("home_pick") not in ids:
            st.session_state["home_pick"] = random.choice(ids)

        picked = discovery_by_id(
            st.session_state["home_pick"]
        )

        show_discovery(picked)

        if st.button("🎲 別の発見を見る", key="home_shuffle"):
            alternatives = [
                x for x in ids if x != picked["id"]
            ]
            if alternatives:
                st.session_state["home_pick"] = random.choice(
                    alternatives
                )
            st.rerun()


# =========================================================
# 2. 新しい発見
# =========================================================

with tab_add:
    st.subheader("💡 意外とよかったことを登録")

    with st.form("add_discovery", clear_on_submit=True):
        title = st.text_input(
            "発見したこと",
            placeholder="例：朝5分だけ掃除してみた",
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        discovery_date = st.date_input(
            "発見した日",
            value=today,
            max_value=today,
        )

        c1, c2 = st.columns(2)

        with c1:
            expectation = st.slider(
                "やる前の期待度",
                1, 5, 2,
            )

        with c2:
            satisfaction = st.slider(
                "実際の満足度",
                1, 5, 5,
            )

        low_reason = st.selectbox(
            "期待していなかった理由",
            LOW_EXPECTATION_REASONS,
        )

        experience = st.text_area(
            "何をした？",
            placeholder="具体的にどんなことを試した？",
        )

        good_point = st.text_area(
            "どうよかった？",
            placeholder="予想外によかったポイント",
        )

        lesson = st.text_area(
            "気づいたこと",
            placeholder="今後にも活かせそうな発見は？",
        )

        favorite = st.checkbox(
            "❤️ お気に入りにする"
        )

        want_retry = st.checkbox(
            "🔁 またやりたい",
            value=True,
        )

        submitted = st.form_submit_button(
            "💡 発見を保存",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not title.strip():
                st.warning("発見したことを入力してね。")
            else:
                add_discovery(
                    title.strip(),
                    category,
                    discovery_date,
                    expectation,
                    satisfaction,
                    low_reason,
                    experience.strip(),
                    good_point.strip(),
                    lesson.strip(),
                    favorite,
                    want_retry,
                )
                st.rerun()

    st.caption(
        "意外度 = 実際の満足度 − 事前の期待度"
    )


# =========================================================
# 3. 再チャレンジ
# =========================================================

with tab_retry:
    st.subheader("🔁 もう一度やってみた！")

    if not discoveries:
        st.info("先に発見を登録しよう。")
    else:
        options = {
            discovery_label(d): d["id"]
            for d in discoveries
        }

        selected_label = st.selectbox(
            "再チャレンジした発見",
            list(options),
            key="retry_select",
        )

        discovery_id = options[selected_label]
        selected = discovery_by_id(discovery_id)

        show_discovery(selected, show_details=False)

        with st.form("add_retry", clear_on_submit=True):
            retry_date = st.date_input(
                "再チャレンジした日",
                value=today,
                max_value=today,
            )

            satisfaction = st.slider(
                "今回の満足度",
                1, 5, 4,
            )

            result = st.selectbox(
                "今回もよかった？",
                RETRY_RESULTS,
            )

            note = st.text_area(
                "今回の気づき",
                placeholder="前回と比べてどうだった？",
            )

            submitted = st.form_submit_button(
                "🔁 再チャレンジを記録",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                add_retry(
                    discovery_id,
                    retry_date,
                    satisfaction,
                    result,
                    note.strip(),
                )
                st.rerun()

        st.divider()
        st.markdown("### 📚 再チャレンジ履歴")

        history = list(reversed(
            retries_of(discovery_id)
        ))

        if not history:
            st.caption("まだ再チャレンジ記録はありません。")

        for r in history:
            with st.container(border=True):
                st.markdown(
                    f"**{r['retry_date']}｜{r['result']}**"
                )
                st.write(
                    f"満足度：{stars(r['satisfaction'])}"
                )
                if r.get("note"):
                    st.write(r["note"])


# =========================================================
# 4. 発見図鑑
# =========================================================

with tab_library:
    st.subheader("📚 意外な当たり図鑑")

    if not discoveries:
        st.info("発見を登録するとここに並ぶよ。")
    else:
        search = st.text_input(
            "🔍 発見を検索",
            placeholder="キーワードを入力",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            category_filter = st.selectbox(
                "カテゴリー",
                ["すべて"] + CATEGORIES,
            )

        with c2:
            gap_filter = st.selectbox(
                "意外度",
                [
                    "すべて",
                    "+3以上",
                    "+1以上",
                    "0",
                    "マイナス",
                ],
            )

        with c3:
            favorite_only = st.checkbox(
                "❤️ お気に入りのみ"
            )

        filtered = []

        for d in discoveries:
            searchable = " ".join([
                d.get("title", ""),
                d.get("experience", ""),
                d.get("good_point", ""),
                d.get("lesson", ""),
            ]).lower()

            if search.lower() not in searchable:
                continue

            if (
                category_filter != "すべて"
                and d.get("category") != category_filter
            ):
                continue

            gap = gap_score(d)

            if gap_filter == "+3以上" and gap < 3:
                continue
            if gap_filter == "+1以上" and gap < 1:
                continue
            if gap_filter == "0" and gap != 0:
                continue
            if gap_filter == "マイナス" and gap >= 0:
                continue

            if favorite_only and not d.get("favorite"):
                continue

            filtered.append(d)

        filtered.sort(
            key=lambda d: (
                d.get("discovery_date", ""),
                d.get("created_at", ""),
            ),
            reverse=True,
        )

        st.caption(f"{len(filtered)}件の発見")

        for d in filtered:
            show_discovery(d)


# =========================================================
# 5. ランキング
# =========================================================

with tab_ranking:
    st.subheader("🏆 意外な当たりランキング")

    if not discoveries:
        st.info("まだランキング対象がありません。")
    else:
        ranked = sorted(
            discoveries,
            key=lambda d: (
                gap_score(d),
                d["satisfaction"],
                d.get("discovery_date", ""),
            ),
            reverse=True,
        )

        rows = []

        for i, d in enumerate(ranked, start=1):
            stats = retry_stats(d["id"])

            rows.append({
                "順位": i,
                "発見": d["title"],
                "カテゴリー": d.get("category", ""),
                "期待度": d["expectation"],
                "満足度": d["satisfaction"],
                "意外度": signed(gap_score(d)),
                "再チャレンジ": stats["count"],
                "お気に入り": (
                    "❤️" if d.get("favorite") else ""
                ),
            })

        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

        st.divider()
        st.markdown("### 🎉 TOP 3")

        for i, d in enumerate(ranked[:3], start=1):
            medal = ["🥇", "🥈", "🥉"][i - 1]

            with st.container(border=True):
                st.markdown(
                    f"### {medal} {d['title']}"
                )
                st.write(
                    f"期待 {stars(d['expectation'])} "
                    f"→ 満足 {stars(d['satisfaction'])}"
                )
                st.metric(
                    "意外度",
                    signed(gap_score(d)),
                )


# =========================================================
# 6. 再発見ガチャ
# =========================================================

with tab_gacha:
    st.subheader("🎲 もう一度やってみない？")

    if not discoveries:
        st.info("発見を登録するとガチャが回せるよ。")
    else:
        only_retry = st.checkbox(
            "🔁 またやりたいものだけ",
            value=True,
        )

        candidates = [
            d for d in discoveries
            if d.get("want_retry")
        ] if only_retry else discoveries

        if not candidates:
            st.warning(
                "「またやりたい」に登録された発見がありません。"
            )
        else:
            ids = [d["id"] for d in candidates]

            if st.session_state.get("gacha_pick") not in ids:
                st.session_state["gacha_pick"] = random.choice(ids)

            picked = discovery_by_id(
                st.session_state["gacha_pick"]
            )

            st.markdown("### ✨ 今日のおすすめ再体験")
            show_discovery(picked)

            if st.button(
                "🎲 ガチャを回す！",
                type="primary",
                use_container_width=True,
            ):
                alternatives = [
                    x for x in ids if x != picked["id"]
                ]

                if alternatives:
                    st.session_state["gacha_pick"] = random.choice(
                        alternatives
                    )

                st.rerun()


# =========================================================
# 7. 分析
# =========================================================

with tab_analysis:
    st.subheader("📊 意外な発見の分析")

    if not discoveries:
        st.info("発見が増えると分析できるよ。")
    else:
        st.markdown("### 📚 カテゴリー別の発見数")

        category_counts = Counter(
            d.get("category", "📦 その他")
            for d in discoveries
        )

        category_df = pd.DataFrame([
            {"カテゴリー": k, "発見数": v}
            for k, v in category_counts.items()
        ])

        st.bar_chart(
            category_df.set_index("カテゴリー")
        )

        st.divider()
        st.markdown("### 📈 カテゴリー別の平均意外度")

        category_gaps = defaultdict(list)

        for d in discoveries:
            category_gaps[
                d.get("category", "📦 その他")
            ].append(gap_score(d))

        gap_df = pd.DataFrame([
            {
                "カテゴリー": category,
                "平均意外度": round(
                    sum(values) / len(values), 2
                ),
            }
            for category, values in category_gaps.items()
        ])

        st.bar_chart(
            gap_df.set_index("カテゴリー")
        )

        st.divider()
        st.markdown("### 🤔 期待が低かった理由")

        reason_counts = Counter(
            d.get("low_reason", "📦 その他")
            for d in discoveries
        )

        reason_df = pd.DataFrame([
            {"理由": k, "件数": v}
            for k, v in reason_counts.items()
        ])

        st.bar_chart(
            reason_df.set_index("理由")
        )

        st.divider()
        st.markdown("### 🗓️ 月ごとの発見数")

        monthly = Counter()

        for d in discoveries:
            parsed = parse_date(
                d.get("discovery_date")
            )
            if parsed:
                monthly[parsed.strftime("%Y-%m")] += 1

        if monthly:
            monthly_df = pd.DataFrame([
                {"月": month, "発見数": count}
                for month, count in sorted(monthly.items())
            ])

            st.bar_chart(
                monthly_df.set_index("月")
            )

        st.divider()
        st.markdown("### 🔁 再体験の満足度")

        if retries:
            retry_values = [
                r["satisfaction"] for r in retries
            ]

            st.metric(
                "再体験の平均満足度",
                f"{sum(retry_values) / len(retry_values):.1f} / 5",
            )

            retry_counts = Counter(
                r.get("result", "その他")
                for r in retries
            )

            retry_df = pd.DataFrame([
                {"結果": k, "回数": v}
                for k, v in retry_counts.items()
            ])

            st.bar_chart(
                retry_df.set_index("結果")
            )
        else:
            st.caption("再チャレンジ記録はまだありません。")

        st.divider()
        st.markdown("### 📊 期待と満足の比較")

        avg_expectation = (
            sum(d["expectation"] for d in discoveries)
            / len(discoveries)
        )

        avg_satisfaction = (
            sum(d["satisfaction"] for d in discoveries)
            / len(discoveries)
        )

        comparison_df = pd.DataFrame([
            {
                "項目": "期待度",
                "平均": round(avg_expectation, 2),
            },
            {
                "項目": "満足度",
                "平均": round(avg_satisfaction, 2),
            },
        ])

        st.bar_chart(
            comparison_df.set_index("項目")
        )


# =========================================================
# 8. 管理
# =========================================================

with tab_manage:
    st.subheader("🛠️ 発見の編集・削除")

    if discoveries:
        options = {
            discovery_label(d): d["id"]
            for d in discoveries
        }

        selected_label = st.selectbox(
            "編集する発見",
            list(options),
            key="manage_discovery",
        )

        discovery_id = options[selected_label]
        d = discovery_by_id(discovery_id)

        # IDごとにフォームキーを変えて、
        # 別の発見の入力値が混ざらないようにする。
        with st.form(f"edit_discovery_{discovery_id}"):
            edit_title = st.text_input(
                "発見",
                value=d["title"],
            )

            edit_category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=choice_index(
                    d.get("category"), CATEGORIES
                ),
            )

            edit_date = st.date_input(
                "発見日",
                value=(
                    parse_date(d.get("discovery_date"))
                    or today
                ),
                max_value=today,
            )

            edit_expectation = st.slider(
                "期待度",
                1, 5,
                int(d["expectation"]),
            )

            edit_satisfaction = st.slider(
                "満足度",
                1, 5,
                int(d["satisfaction"]),
            )

            edit_reason = st.selectbox(
                "期待していなかった理由",
                LOW_EXPECTATION_REASONS,
                index=choice_index(
                    d.get("low_reason"),
                    LOW_EXPECTATION_REASONS,
                ),
            )

            edit_experience = st.text_area(
                "何をした？",
                value=d.get("experience", ""),
            )

            edit_good = st.text_area(
                "どうよかった？",
                value=d.get("good_point", ""),
            )

            edit_lesson = st.text_area(
                "気づき",
                value=d.get("lesson", ""),
            )

            edit_favorite = st.checkbox(
                "❤️ お気に入り",
                value=d.get("favorite", False),
            )

            edit_retry = st.checkbox(
                "🔁 またやりたい",
                value=d.get("want_retry", False),
            )

            saved = st.form_submit_button(
                "💾 変更を保存",
                type="primary",
                use_container_width=True,
            )

            if saved:
                if not edit_title.strip():
                    st.warning("発見名を入力してね。")
                else:
                    d.update({
                        "title": edit_title.strip(),
                        "category": edit_category,
                        "discovery_date": str(edit_date),
                        "expectation": edit_expectation,
                        "satisfaction": edit_satisfaction,
                        "low_reason": edit_reason,
                        "experience": edit_experience.strip(),
                        "good_point": edit_good.strip(),
                        "lesson": edit_lesson.strip(),
                        "favorite": edit_favorite,
                        "want_retry": edit_retry,
                        "updated_at": now_iso(),
                    })

                    save_data(data)
                    st.rerun()

        st.divider()
        st.markdown("### 🔁 再チャレンジ記録の管理")

        item_retries = retries_of(discovery_id)

        if item_retries:
            retry_options = {
                (
                    f"{r['retry_date']} "
                    f"｜{r['result']} "
                    f"[{r['id'][:8]}]"
                ): r["id"]
                for r in item_retries
            }

            retry_label = st.selectbox(
                "編集する再チャレンジ",
                list(retry_options),
                key=f"manage_retry_{discovery_id}",
            )

            retry_id = retry_options[retry_label]

            r = next(
                x for x in data["retries"]
                if x["id"] == retry_id
            )

            with st.form(f"edit_retry_{retry_id}"):
                edit_retry_date = st.date_input(
                    "再チャレンジ日",
                    value=(
                        parse_date(r.get("retry_date"))
                        or today
                    ),
                    max_value=today,
                )

                edit_retry_satisfaction = st.slider(
                    "満足度",
                    1, 5,
                    int(r["satisfaction"]),
                )

                edit_retry_result = st.selectbox(
                    "結果",
                    RETRY_RESULTS,
                    index=choice_index(
                        r.get("result"), RETRY_RESULTS
                    ),
                )

                edit_retry_note = st.text_area(
                    "気づき",
                    value=r.get("note", ""),
                )

                if st.form_submit_button(
                    "💾 再チャレンジを保存"
                ):
                    r.update({
                        "retry_date": str(edit_retry_date),
                        "satisfaction": edit_retry_satisfaction,
                        "result": edit_retry_result,
                        "note": edit_retry_note.strip(),
                    })

                    save_data(data)
                    st.rerun()

            confirm_retry_delete = st.checkbox(
                "この再チャレンジを削除する",
                key=f"confirm_retry_{retry_id}",
            )

            if st.button(
                "🗑️ 再チャレンジを削除",
                disabled=not confirm_retry_delete,
                key=f"delete_retry_{retry_id}",
            ):
                data["retries"] = [
                    x for x in data["retries"]
                    if x["id"] != retry_id
                ]
                save_data(data)
                st.rerun()

        else:
            st.caption("再チャレンジ履歴はありません。")

        st.divider()
        st.markdown("### ⚠️ 発見を完全削除")

        st.warning(
            "この発見を削除すると、"
            "紐づく再チャレンジ記録も削除されます。"
        )

        confirm_delete = st.checkbox(
            "この発見と全履歴を削除する",
            key=f"confirm_discovery_{discovery_id}",
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=not confirm_delete,
            key=f"delete_discovery_{discovery_id}",
        ):
            delete_discovery(discovery_id)
            st.rerun()

    else:
        st.info("編集できる発見はまだありません。")

    st.divider()
    st.subheader("💾 JSONバックアップ")

    backup_json = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=backup_json,
        file_name=f"unexpected_good_{today_iso()}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()
    st.subheader("📤 バックアップから復元")

    st.warning(
        "復元すると現在の全データが置き換わります。"
        "必要なら先にバックアップを保存してください。"
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
                f"読み込みOK："
                f"発見 {len(restored['discoveries'])}件、"
                f"再チャレンジ {len(restored['retries'])}件"
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
# フッター
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:25px;">
        <p><b>期待していなかったことが、</b></p>
        <p><b>思いがけず心を満たしてくれる。</b></p>
        <p>
            何でもない一日にも、<br>
            まだ知らない楽しさが隠れている。
        </p>
        <h3>「やってみたら、意外とよかった！」💡✨</h3>
        <p><b>DAY 312 / 365 — COMPLETE 🔥</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)
