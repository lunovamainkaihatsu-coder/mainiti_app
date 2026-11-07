
import json
import os
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
    page_title="別の選択をしていたら？",
    page_icon="🌿",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "decisions.json"

CATEGORIES = [
    "💼 仕事",
    "🤝 人間関係",
    "🏠 住まい",
    "💰 お金",
    "📚 学習",
    "🏃 健康",
    "🎮 趣味",
    "📦 その他",
]

SCENARIO_TYPES = [
    "🌤️ 楽観シナリオ",
    "⚖️ 中立シナリオ",
    "🌧️ 悲観シナリオ",
    "🌙 その他",
]

EMOTIONS = [
    "😊 納得している",
    "😌 少し納得している",
    "🤔 まだ分からない",
    "😟 少し後悔している",
    "😢 後悔している",
    "🌿 その他",
]

REVIEW_STATUS = [
    "未整理",
    "整理中",
    "学びを見つけた",
]


# =========================================================
# データ操作
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


def empty_data():
    return {
        "decisions": [],
        "scenarios": [],
        "reviews": [],
    }


def validate_data(obj):
    if not isinstance(obj, dict):
        raise ValueError("JSON全体がオブジェクトではありません。")

    for key in ("decisions", "scenarios", "reviews"):
        if key not in obj or not isinstance(obj[key], list):
            raise ValueError(f"{key} が配列ではありません。")

        for item in obj[key]:
            if not isinstance(item, dict):
                raise ValueError(f"{key} に不正な記録があります。")

    ids = []

    for key in ("decisions", "scenarios", "reviews"):
        for item in obj[key]:
            item_id = item.get("id")

            if not isinstance(item_id, str) or not item_id:
                raise ValueError(f"{key} にIDのない記録があります。")

            ids.append(item_id)

    if len(ids) != len(set(ids)):
        raise ValueError("記録IDが重複しています。")

    decision_ids = {
        d["id"] for d in obj["decisions"]
    }

    for d in obj["decisions"]:
        if not isinstance(d.get("title"), str):
            raise ValueError("選択タイトルが不正です。")

    for key in ("scenarios", "reviews"):
        for item in obj[key]:
            if item.get("decision_id") not in decision_ids:
                raise ValueError(
                    f"{key} に存在しない選択への参照があります。"
                )

    for review in obj["reviews"]:
        for field in ("acceptance", "clarity"):
            value = review.get(field)

            if type(value) is not int or not 1 <= value <= 5:
                raise ValueError(
                    f"{field} は1〜5の整数です。"
                )

    return obj


def save_data(obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temp = DATA_FILE.with_suffix(".tmp")

    with temp.open("w", encoding="utf-8") as f:
        json.dump(
            obj,
            f,
            ensure_ascii=False,
            indent=2,
        )

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
            "既存データは上書きせず保護しています。"
        )
        st.code(str(exc))
        st.stop()


def decision_by_id(decision_id):
    return next(
        (
            d for d in data["decisions"]
            if d["id"] == decision_id
        ),
        None,
    )


def scenarios_of(decision_id):
    return [
        s for s in data["scenarios"]
        if s["decision_id"] == decision_id
    ]


def reviews_of(decision_id):
    return sorted(
        [
            r for r in data["reviews"]
            if r["decision_id"] == decision_id
        ],
        key=lambda r: (
            r.get("review_date", ""),
            r.get("created_at", ""),
        ),
    )


def decision_label(d):
    return f"{d['title']} [{d['id'][:8]}]"


def choice_index(value, choices):
    return choices.index(value) if value in choices else 0


def add_decision(
    title,
    category,
    decision_date,
    chosen_path,
    other_path,
    reason,
    actual_gain,
    actual_difficulty,
    current_impact,
    emotion,
    learning,
    next_action,
    status,
):
    data["decisions"].append({
        "id": uid(),
        "title": title,
        "category": category,
        "decision_date": str(decision_date),
        "chosen_path": chosen_path,
        "other_path": other_path,
        "reason": reason,
        "actual_gain": actual_gain,
        "actual_difficulty": actual_difficulty,
        "current_impact": current_impact,
        "emotion": emotion,
        "learning": learning,
        "next_action": next_action,
        "status": status,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })

    save_data(data)


def add_scenario(
    decision_id,
    scenario_type,
    title,
    description,
    possible_gain,
    possible_difficulty,
    evidence,
    uncertainty,
):
    data["scenarios"].append({
        "id": uid(),
        "decision_id": decision_id,
        "scenario_type": scenario_type,
        "title": title,
        "description": description,
        "possible_gain": possible_gain,
        "possible_difficulty": possible_difficulty,
        "evidence": evidence,
        "uncertainty": uncertainty,
        "created_at": now_iso(),
    })

    save_data(data)


def add_review(
    decision_id,
    review_date,
    acceptance,
    clarity,
    feeling,
    new_learning,
    next_action,
):
    data["reviews"].append({
        "id": uid(),
        "decision_id": decision_id,
        "review_date": str(review_date),
        "acceptance": acceptance,
        "clarity": clarity,
        "feeling": feeling,
        "new_learning": new_learning,
        "next_action": next_action,
        "created_at": now_iso(),
    })

    save_data(data)


def delete_decision(decision_id):
    data["decisions"] = [
        d for d in data["decisions"]
        if d["id"] != decision_id
    ]

    data["scenarios"] = [
        s for s in data["scenarios"]
        if s["decision_id"] != decision_id
    ]

    data["reviews"] = [
        r for r in data["reviews"]
        if r["decision_id"] != decision_id
    ]

    save_data(data)


def show_decision(d, detailed=True):
    with st.container(border=True):
        st.markdown(f"### 🌿 {d['title']}")

        st.caption(
            f"{d.get('category', '')} "
            f"｜{d.get('decision_date', '')}"
        )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**🌱 実際に選んだ道**")
            st.write(d.get("chosen_path") or "未記入")

        with c2:
            st.markdown("**🌙 選ばなかった道**")
            st.write(d.get("other_path") or "未記入")

        st.caption(
            f"今の気持ち：{d.get('emotion', '')} "
            f"｜振り返り：{d.get('status', '')}"
        )

        if detailed:
            if d.get("reason"):
                st.write(
                    f"**当時の判断基準：** {d['reason']}"
                )

            if d.get("actual_gain"):
                st.write(
                    f"**実際に得られたもの：** "
                    f"{d['actual_gain']}"
                )

            if d.get("actual_difficulty"):
                st.write(
                    f"**大変だったこと：** "
                    f"{d['actual_difficulty']}"
                )

            if d.get("current_impact"):
                st.write(
                    f"**今の自分への影響：** "
                    f"{d['current_impact']}"
                )

            if d.get("learning"):
                st.write(
                    f"**学び：** {d['learning']}"
                )

            if d.get("next_action"):
                st.write(
                    f"**次の行動：** {d['next_action']}"
                )

            st.caption(
                f"🌙 シナリオ {len(scenarios_of(d['id']))}件 "
                f"｜🔁 再評価 {len(reviews_of(d['id']))}回"
            )


# =========================================================
# 初期化
# =========================================================

data = load_data()

decisions = data["decisions"]
scenarios = data["scenarios"]
reviews = data["reviews"]

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
            rgba(50,180,140,.16),
            rgba(150,130,230,.13)
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
        <div>🌿🔀 DAY 314 / 365</div>
        <h1>別の選択をしていたら？</h1>
        <p>
            選ばなかった道にも、<br>
            今を生きるヒントがある。
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
    tab_scenario,
    tab_gain,
    tab_album,
    tab_review,
    tab_analysis,
    tab_manage,
) = st.tabs([
    "🏠 ホーム",
    "🔀 選択を登録",
    "🌙 もしもの世界",
    "🌱 得られたもの",
    "📖 選択アルバム",
    "🔁 再評価",
    "📊 分析",
    "🛠️ 管理",
])


# =========================================================
# 1. ホーム
# =========================================================

with tab_home:
    st.subheader("🏠 人生の分岐点ダッシュボード")

    learning_count = sum(
        bool(d.get("learning", "").strip())
        for d in decisions
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔀 振り返った選択", len(decisions))
    c2.metric("🌙 もしものシナリオ", len(scenarios))
    c3.metric("🔁 再評価した回数", len(reviews))
    c4.metric("🌱 学びのある選択", learning_count)

    if not decisions:
        st.info(
            "まだ選択がありません。"
            "「🔀 選択を登録」から最初の分岐点を記録しよう。"
        )
    else:
        st.divider()
        st.markdown("### 📝 最近登録した選択")

        recent = sorted(
            decisions,
            key=lambda d: d.get("created_at", ""),
            reverse=True,
        )[:3]

        for d in recent:
            show_decision(d, detailed=False)

        st.divider()
        st.markdown("### 🌿 今の自分への問い")

        st.info(
            "あのときの自分は、"
            "何を守ろうとしてその選択をしたんだろう？"
        )


# =========================================================
# 2. 選択を登録
# =========================================================

with tab_add:
    st.subheader("🔀 過去の分岐点を記録")

    with st.form("add_decision", clear_on_submit=True):
        title = st.text_input(
            "選択のタイトル",
            placeholder="例：あのとき転職を決めたこと",
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        decision_date = st.date_input(
            "選択した日",
            value=today,
            max_value=today,
        )

        c1, c2 = st.columns(2)

        with c1:
            chosen_path = st.text_area(
                "🌱 実際に選んだ道",
                placeholder="実際に何を選んだ？",
            )

        with c2:
            other_path = st.text_area(
                "🌙 選ばなかった道",
                placeholder="別にどんな選択肢があった？",
            )

        reason = st.text_area(
            "当時の判断基準",
            placeholder="何を大切にして決めた？",
        )

        actual_gain = st.text_area(
            "実際に得られたもの",
            placeholder="新しい経験、知識、出会いなど",
        )

        actual_difficulty = st.text_area(
            "大変だったこと",
            placeholder="どんな苦労があった？",
        )

        current_impact = st.text_area(
            "今の自分への影響",
        )

        emotion = st.selectbox(
            "今の気持ち",
            EMOTIONS,
            index=2,
        )

        learning = st.text_area(
            "この選択から学んだこと",
        )

        next_action = st.text_area(
            "これからできる小さな行動",
        )

        status = st.selectbox(
            "振り返り状況",
            REVIEW_STATUS,
        )

        submitted = st.form_submit_button(
            "🌿 選択を保存",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not title.strip():
                st.warning("タイトルを入力してね。")
            elif not chosen_path.strip():
                st.warning("実際に選んだ道を入力してね。")
            else:
                add_decision(
                    title.strip(),
                    category,
                    decision_date,
                    chosen_path.strip(),
                    other_path.strip(),
                    reason.strip(),
                    actual_gain.strip(),
                    actual_difficulty.strip(),
                    current_impact.strip(),
                    emotion,
                    learning.strip(),
                    next_action.strip(),
                    status,
                )
                st.rerun()


# =========================================================
# 3. もしもの世界
# =========================================================

with tab_scenario:
    st.subheader("🌙 もしも別の道を選んでいたら？")

    st.caption(
        "ここに書くのは事実ではなく想像。"
        "良い可能性も悪い可能性も自由に考えてみよう。"
    )

    if not decisions:
        st.info("先に選択を登録しよう。")
    else:
        options = {
            decision_label(d): d["id"]
            for d in decisions
        }

        selected_label = st.selectbox(
            "想像する選択",
            list(options),
            key="scenario_decision",
        )

        decision_id = options[selected_label]
        selected = decision_by_id(decision_id)

        show_decision(selected, detailed=False)

        with st.form("add_scenario", clear_on_submit=True):
            scenario_type = st.selectbox(
                "シナリオの種類",
                SCENARIO_TYPES,
            )

            title = st.text_input(
                "シナリオのタイトル",
                placeholder="例：前の環境で成長していた世界",
            )

            description = st.text_area(
                "もしもの世界",
                placeholder="どんな人生になっていたか想像してみよう",
                height=120,
            )

            possible_gain = st.text_area(
                "得られたかもしれないもの",
            )

            possible_difficulty = st.text_area(
                "生まれたかもしれない課題",
            )

            evidence = st.text_area(
                "そう考える理由",
                placeholder="想像の根拠はある？",
            )

            uncertainty = st.text_area(
                "分からない部分",
                placeholder="予測できないことは何だろう？",
            )

            submitted = st.form_submit_button(
                "🌙 シナリオを保存",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not title.strip():
                    st.warning("シナリオ名を入力してね。")
                else:
                    add_scenario(
                        decision_id,
                        scenario_type,
                        title.strip(),
                        description.strip(),
                        possible_gain.strip(),
                        possible_difficulty.strip(),
                        evidence.strip(),
                        uncertainty.strip(),
                    )
                    st.rerun()

        st.divider()
        st.markdown("### 🌙 保存したシナリオ")

        items = scenarios_of(decision_id)

        if not items:
            st.caption("まだシナリオはありません。")

        for s in items:
            with st.container(border=True):
                st.markdown(
                    f"### {s['scenario_type']}｜{s['title']}"
                )

                if s.get("description"):
                    st.write(s["description"])

                if s.get("possible_gain"):
                    st.write(
                        f"**得られた可能性：** "
                        f"{s['possible_gain']}"
                    )

                if s.get("possible_difficulty"):
                    st.write(
                        f"**考えられる課題：** "
                        f"{s['possible_difficulty']}"
                    )

                if s.get("evidence"):
                    st.write(
                        f"**想像の根拠：** {s['evidence']}"
                    )

                if s.get("uncertainty"):
                    st.write(
                        f"**不確かな部分：** "
                        f"{s['uncertainty']}"
                    )


# =========================================================
# 4. 得られたもの
# =========================================================

with tab_gain:
    st.subheader("🌱 今の選択が残してくれたもの")

    if not decisions:
        st.info("選択を登録すると振り返れるよ。")
    else:
        with_gain = [
            d for d in decisions
            if d.get("actual_gain", "").strip()
        ]

        st.metric(
            "🌱 得られたものを記録した選択",
            len(with_gain),
        )

        st.caption(
            "何も思いつかない選択があっても大丈夫。"
            "無理に良い意味を見つける必要はないよ。"
        )

        for d in decisions:
            with st.container(border=True):
                st.markdown(f"### 🌿 {d['title']}")

                st.caption(d.get("decision_date", ""))

                st.markdown("**実際に得られたもの**")
                st.write(
                    d.get("actual_gain") or "まだ記録なし"
                )

                st.markdown("**大変だったこと**")
                st.write(
                    d.get("actual_difficulty") or "まだ記録なし"
                )

                st.markdown("**これから活かせる学び**")
                st.write(
                    d.get("learning") or "まだ記録なし"
                )

                st.markdown("**次の小さな行動**")
                st.write(
                    d.get("next_action") or "まだ記録なし"
                )


# =========================================================
# 5. 選択アルバム
# =========================================================

with tab_album:
    st.subheader("📖 人生の選択アルバム")

    if not decisions:
        st.info("選択を登録するとここに並ぶよ。")
    else:
        search = st.text_input(
            "🔍 選択を検索",
            placeholder="キーワードを入力",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            category_filter = st.selectbox(
                "カテゴリー",
                ["すべて"] + CATEGORIES,
                key="album_category",
            )

        with c2:
            emotion_filter = st.selectbox(
                "今の気持ち",
                ["すべて"] + EMOTIONS,
            )

        with c3:
            status_filter = st.selectbox(
                "振り返り状況",
                ["すべて"] + REVIEW_STATUS,
            )

        filtered = []

        for d in decisions:
            searchable = " ".join([
                d.get("title", ""),
                d.get("chosen_path", ""),
                d.get("other_path", ""),
                d.get("reason", ""),
                d.get("learning", ""),
            ]).lower()

            if search.lower() not in searchable:
                continue

            if (
                category_filter != "すべて"
                and d.get("category") != category_filter
            ):
                continue

            if (
                emotion_filter != "すべて"
                and d.get("emotion") != emotion_filter
            ):
                continue

            if (
                status_filter != "すべて"
                and d.get("status") != status_filter
            ):
                continue

            filtered.append(d)

        filtered.sort(
            key=lambda d: (
                d.get("decision_date", ""),
                d.get("created_at", ""),
            ),
            reverse=True,
        )

        st.caption(f"{len(filtered)}件の選択")

        for d in filtered:
            show_decision(d)


# =========================================================
# 6. 再評価
# =========================================================

with tab_review:
    st.subheader("🔁 時間が経った今、どう感じる？")

    if not decisions:
        st.info("先に選択を登録しよう。")
    else:
        options = {
            decision_label(d): d["id"]
            for d in decisions
        }

        selected_label = st.selectbox(
            "再評価する選択",
            list(options),
            key="review_decision",
        )

        decision_id = options[selected_label]
        selected = decision_by_id(decision_id)

        show_decision(selected, detailed=False)

        with st.form("add_review", clear_on_submit=True):
            review_date = st.date_input(
                "振り返った日",
                value=today,
                max_value=today,
            )

            c1, c2 = st.columns(2)

            with c1:
                acceptance = st.slider(
                    "今の選択への納得度",
                    1, 5, 3,
                )

            with c2:
                clarity = st.slider(
                    "今後の判断への学びの明確さ",
                    1, 5, 3,
                )

            feeling = st.text_area(
                "今の気持ち",
            )

            new_learning = st.text_area(
                "新しく気づいたこと",
            )

            next_action = st.text_area(
                "これからできる行動",
            )

            submitted = st.form_submit_button(
                "🔁 再評価を保存",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                add_review(
                    decision_id,
                    review_date,
                    acceptance,
                    clarity,
                    feeling.strip(),
                    new_learning.strip(),
                    next_action.strip(),
                )
                st.rerun()

        st.divider()
        st.markdown("### 📚 再評価の履歴")

        history = list(reversed(
            reviews_of(decision_id)
        ))

        if not history:
            st.caption("まだ再評価記録はありません。")

        for r in history:
            with st.container(border=True):
                st.markdown(
                    f"### 🔁 {r['review_date']}"
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "納得度",
                    f"{r['acceptance']} / 5",
                )

                c2.metric(
                    "学びの明確さ",
                    f"{r['clarity']} / 5",
                )

                if r.get("feeling"):
                    st.write(
                        f"**気持ち：** {r['feeling']}"
                    )

                if r.get("new_learning"):
                    st.write(
                        f"**新しい学び：** "
                        f"{r['new_learning']}"
                    )

                if r.get("next_action"):
                    st.write(
                        f"**次の行動：** "
                        f"{r['next_action']}"
                    )


# =========================================================
# 7. 分析
# =========================================================

with tab_analysis:
    st.subheader("📊 人生の選択を分析")

    if not decisions:
        st.info("記録が増えると分析できるよ。")
    else:
        st.markdown("### 📚 カテゴリー別の選択数")

        category_counts = Counter(
            d.get("category", "📦 その他")
            for d in decisions
        )

        category_df = pd.DataFrame([
            {"カテゴリー": k, "選択数": v}
            for k, v in category_counts.items()
        ])

        st.bar_chart(
            category_df.set_index("カテゴリー")
        )

        st.divider()
        st.markdown("### 🗓️ 選択した年代")

        decade_counts = Counter()

        for d in decisions:
            parsed = parse_date(
                d.get("decision_date")
            )

            if parsed:
                decade = (parsed.year // 10) * 10
                decade_counts[f"{decade}年代"] += 1

        if decade_counts:
            decade_df = pd.DataFrame([
                {"年代": k, "選択数": v}
                for k, v in sorted(decade_counts.items())
            ])

            st.bar_chart(
                decade_df.set_index("年代")
            )

        st.divider()
        st.markdown("### 🌙 シナリオの種類")

        if scenarios:
            scenario_counts = Counter(
                s.get("scenario_type", "その他")
                for s in scenarios
            )

            scenario_df = pd.DataFrame([
                {"種類": k, "件数": v}
                for k, v in scenario_counts.items()
            ])

            st.bar_chart(
                scenario_df.set_index("種類")
            )
        else:
            st.caption("シナリオはまだありません。")

        st.divider()
        st.markdown("### 🌿 今の気持ち")

        emotion_counts = Counter(
            d.get("emotion", "その他")
            for d in decisions
        )

        emotion_df = pd.DataFrame([
            {"気持ち": k, "件数": v}
            for k, v in emotion_counts.items()
        ])

        st.bar_chart(
            emotion_df.set_index("気持ち")
        )

        st.divider()
        st.markdown("### 🔁 再評価の推移")

        if reviews:
            review_rows = []

            for r in reviews:
                review_rows.append({
                    "日付": r["review_date"],
                    "納得度": r["acceptance"],
                    "学びの明確さ": r["clarity"],
                })

            review_df = pd.DataFrame(review_rows)

            review_df["日付"] = pd.to_datetime(
                review_df["日付"],
                errors="coerce",
            )

            review_df = review_df.dropna(
                subset=["日付"]
            )

            if not review_df.empty:
                daily = (
                    review_df.groupby("日付")[
                        ["納得度", "学びの明確さ"]
                    ]
                    .mean()
                    .sort_index()
                )

                st.line_chart(daily)

            st.caption(
                "※異なる選択の再評価を日付別に平均したものです。"
                "個別の選択の変化とは区別して見てね。"
            )
        else:
            st.caption("再評価記録はまだありません。")

        st.divider()
        st.markdown("### 🌱 振り返り状況")

        status_counts = Counter(
            d.get("status", "未整理")
            for d in decisions
        )

        status_df = pd.DataFrame([
            {"状況": k, "件数": v}
            for k, v in status_counts.items()
        ])

        st.bar_chart(
            status_df.set_index("状況")
        )


# =========================================================
# 8. 管理
# =========================================================

with tab_manage:
    st.subheader("🛠️ 記録の編集・削除")

    if decisions:
        options = {
            decision_label(d): d["id"]
            for d in decisions
        }

        selected_label = st.selectbox(
            "編集する選択",
            list(options),
            key="manage_decision",
        )

        decision_id = options[selected_label]
        d = decision_by_id(decision_id)

        with st.form(f"edit_decision_{decision_id}"):
            edit_title = st.text_input(
                "タイトル",
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
                "選択した日",
                value=(
                    parse_date(d.get("decision_date"))
                    or today
                ),
                max_value=today,
            )

            edit_chosen = st.text_area(
                "実際に選んだ道",
                value=d.get("chosen_path", ""),
            )

            edit_other = st.text_area(
                "選ばなかった道",
                value=d.get("other_path", ""),
            )

            edit_reason = st.text_area(
                "当時の判断基準",
                value=d.get("reason", ""),
            )

            edit_gain = st.text_area(
                "実際に得られたもの",
                value=d.get("actual_gain", ""),
            )

            edit_difficulty = st.text_area(
                "大変だったこと",
                value=d.get("actual_difficulty", ""),
            )

            edit_impact = st.text_area(
                "今の自分への影響",
                value=d.get("current_impact", ""),
            )

            edit_emotion = st.selectbox(
                "今の気持ち",
                EMOTIONS,
                index=choice_index(
                    d.get("emotion"), EMOTIONS
                ),
            )

            edit_learning = st.text_area(
                "学び",
                value=d.get("learning", ""),
            )

            edit_action = st.text_area(
                "次の行動",
                value=d.get("next_action", ""),
            )

            edit_status = st.selectbox(
                "振り返り状況",
                REVIEW_STATUS,
                index=choice_index(
                    d.get("status"), REVIEW_STATUS
                ),
            )

            saved = st.form_submit_button(
                "💾 変更を保存",
                type="primary",
                use_container_width=True,
            )

            if saved:
                if not edit_title.strip():
                    st.warning("タイトルを入力してね。")
                elif not edit_chosen.strip():
                    st.warning("実際に選んだ道を入力してね。")
                else:
                    d.update({
                        "title": edit_title.strip(),
                        "category": edit_category,
                        "decision_date": str(edit_date),
                        "chosen_path": edit_chosen.strip(),
                        "other_path": edit_other.strip(),
                        "reason": edit_reason.strip(),
                        "actual_gain": edit_gain.strip(),
                        "actual_difficulty": edit_difficulty.strip(),
                        "current_impact": edit_impact.strip(),
                        "emotion": edit_emotion,
                        "learning": edit_learning.strip(),
                        "next_action": edit_action.strip(),
                        "status": edit_status,
                        "updated_at": now_iso(),
                    })

                    save_data(data)
                    st.rerun()

        st.divider()
        st.markdown("### 🌙 シナリオの管理")

        item_scenarios = scenarios_of(decision_id)

        if item_scenarios:
            scenario_options = {
                f"{s['title']} [{s['id'][:8]}]": s["id"]
                for s in item_scenarios
            }

            scenario_label = st.selectbox(
                "編集するシナリオ",
                list(scenario_options),
                key=f"manage_scenario_{decision_id}",
            )

            scenario_id = scenario_options[scenario_label]

            s = next(
                x for x in data["scenarios"]
                if x["id"] == scenario_id
            )

            with st.form(f"edit_scenario_{scenario_id}"):
                edit_s_type = st.selectbox(
                    "種類",
                    SCENARIO_TYPES,
                    index=choice_index(
                        s.get("scenario_type"),
                        SCENARIO_TYPES,
                    ),
                )

                edit_s_title = st.text_input(
                    "タイトル",
                    value=s.get("title", ""),
                )

                edit_s_description = st.text_area(
                    "もしもの世界",
                    value=s.get("description", ""),
                )

                edit_s_gain = st.text_area(
                    "得られた可能性",
                    value=s.get("possible_gain", ""),
                )

                edit_s_difficulty = st.text_area(
                    "考えられる課題",
                    value=s.get("possible_difficulty", ""),
                )

                edit_s_evidence = st.text_area(
                    "想像の根拠",
                    value=s.get("evidence", ""),
                )

                edit_s_uncertainty = st.text_area(
                    "不確かな部分",
                    value=s.get("uncertainty", ""),
                )

                if st.form_submit_button(
                    "💾 シナリオを保存"
                ):
                    if not edit_s_title.strip():
                        st.warning("タイトルを入力してね。")
                    else:
                        s.update({
                            "scenario_type": edit_s_type,
                            "title": edit_s_title.strip(),
                            "description": edit_s_description.strip(),
                            "possible_gain": edit_s_gain.strip(),
                            "possible_difficulty": edit_s_difficulty.strip(),
                            "evidence": edit_s_evidence.strip(),
                            "uncertainty": edit_s_uncertainty.strip(),
                        })

                        save_data(data)
                        st.rerun()

            confirm_s_delete = st.checkbox(
                "このシナリオを削除する",
                key=f"confirm_s_{scenario_id}",
            )

            if st.button(
                "🗑️ シナリオを削除",
                disabled=not confirm_s_delete,
                key=f"delete_s_{scenario_id}",
            ):
                data["scenarios"] = [
                    x for x in data["scenarios"]
                    if x["id"] != scenario_id
                ]

                save_data(data)
                st.rerun()

        else:
            st.caption("シナリオはまだありません。")

        st.divider()
        st.markdown("### 🔁 再評価履歴の管理")

        item_reviews = reviews_of(decision_id)

        if item_reviews:
            review_options = {
                (
                    f"{r['review_date']} "
                    f"[{r['id'][:8]}]"
                ): r["id"]
                for r in item_reviews
            }

            review_label = st.selectbox(
                "編集する再評価",
                list(review_options),
                key=f"manage_review_{decision_id}",
            )

            review_id = review_options[review_label]

            r = next(
                x for x in data["reviews"]
                if x["id"] == review_id
            )

            with st.form(f"edit_review_{review_id}"):
                edit_r_date = st.date_input(
                    "再評価日",
                    value=(
                        parse_date(r.get("review_date"))
                        or today
                    ),
                    max_value=today,
                )

                edit_acceptance = st.slider(
                    "納得度",
                    1, 5,
                    int(r["acceptance"]),
                )

                edit_clarity = st.slider(
                    "学びの明確さ",
                    1, 5,
                    int(r["clarity"]),
                )

                edit_feeling = st.text_area(
                    "今の気持ち",
                    value=r.get("feeling", ""),
                )

                edit_new_learning = st.text_area(
                    "新しい学び",
                    value=r.get("new_learning", ""),
                )

                edit_next_action = st.text_area(
                    "次の行動",
                    value=r.get("next_action", ""),
                )

                if st.form_submit_button(
                    "💾 再評価を保存"
                ):
                    r.update({
                        "review_date": str(edit_r_date),
                        "acceptance": edit_acceptance,
                        "clarity": edit_clarity,
                        "feeling": edit_feeling.strip(),
                        "new_learning": edit_new_learning.strip(),
                        "next_action": edit_next_action.strip(),
                    })

                    save_data(data)
                    st.rerun()

            confirm_r_delete = st.checkbox(
                "この再評価を削除する",
                key=f"confirm_r_{review_id}",
            )

            if st.button(
                "🗑️ 再評価を削除",
                disabled=not confirm_r_delete,
                key=f"delete_r_{review_id}",
            ):
                data["reviews"] = [
                    x for x in data["reviews"]
                    if x["id"] != review_id
                ]

                save_data(data)
                st.rerun()

        else:
            st.caption("再評価履歴はまだありません。")

        st.divider()
        st.markdown("### ⚠️ 選択を完全削除")

        st.warning(
            "選択を削除すると、紐づくシナリオと"
            "再評価履歴もすべて削除されます。"
        )

        confirm_delete = st.checkbox(
            "この選択と全履歴を削除する",
            key=f"confirm_d_{decision_id}",
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=not confirm_delete,
            key=f"delete_d_{decision_id}",
        ):
            delete_decision(decision_id)
            st.rerun()

    else:
        st.info("編集できる選択はまだありません。")

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
        file_name=f"another_path_{today_iso()}.json",
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
                f"選択 {len(restored['decisions'])}件、"
                f"シナリオ {len(restored['scenarios'])}件、"
                f"再評価 {len(restored['reviews'])}件"
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
        <p><b>選ばなかった道にも、</b></p>
        <p><b>今を生きるヒントがある。</b></p>
        <p>
            過去を変えることはできなくても、<br>
            過去から学ぶことはできる。
        </p>
        <h3>
            これからの選択を、もっと自分らしく。🌿
        </h3>
        <p><b>DAY 314 / 365 — COMPLETE 🔥</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)
