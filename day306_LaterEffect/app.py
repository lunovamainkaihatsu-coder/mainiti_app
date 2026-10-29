import json
import os
import random
import uuid
from collections import defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="あとで効いてきた",
    page_icon="🌱",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "later_effect.json")

CATEGORIES = [
    "📚 勉強",
    "💪 運動",
    "💰 お金",
    "🛠️ 制作",
    "📣 発信",
    "📖 読書",
    "🤝 人間関係",
    "🧹 生活改善",
    "🚀 挑戦",
    "🌱 その他",
]

STATUSES = [
    "🌱 育っている",
    "🌿 少し効いてきた",
    "🌳 効いた！",
    "🍂 今回は分からなかった",
]

EXPECTED_PERIODS = [
    "1週間",
    "1か月",
    "3か月",
    "半年",
    "1年",
    "分からない",
]


# =========================================================
# BASIC HELPERS
# =========================================================

def new_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def today_text():
    return date.today().isoformat()


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d",
        ).date()
    except (ValueError, TypeError):
        return None


def star_text(value):
    if value is None:
        return "未記録"

    value = int(value)
    value = max(0, min(value, 5))

    return "★" * value + "☆" * (5 - value)


def seed_label(seed):
    return (
        f"{seed.get('title', '')}"
        f" [{seed.get('id', '')[:6]}]"
    )


def created_date(seed):
    created = parse_datetime(
        seed.get("created_at")
    )

    return created.date() if created else None


def elapsed_days(seed, target_date=None):
    start = created_date(seed)

    if not start:
        return None

    end = target_date or date.today()

    return max(
        0,
        (end - start).days,
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "seeds": [],
        "effects": [],
    }


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)

    temp_file = DATA_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temp_file,
        DATA_FILE,
    )


def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            data = default_data()

        data.setdefault("seeds", [])
        data.setdefault("effects", [])

        for seed in data["seeds"]:
            seed.setdefault("id", new_id())
            seed.setdefault("title", "")
            seed.setdefault(
                "category",
                "🌱 その他",
            )
            seed.setdefault("minutes", 0)
            seed.setdefault(
                "initial_feeling",
                3,
            )
            seed.setdefault(
                "initial_note",
                "",
            )
            seed.setdefault(
                "desired_result",
                "",
            )
            seed.setdefault(
                "expected_period",
                "分からない",
            )
            seed.setdefault(
                "status",
                "🌱 育っている",
            )
            seed.setdefault(
                "created_at",
                now_text(),
            )
            seed.setdefault(
                "updated_at",
                seed.get(
                    "created_at",
                    now_text(),
                ),
            )

        for effect in data["effects"]:
            effect.setdefault("id", new_id())
            effect.setdefault("seed_id", "")
            effect.setdefault(
                "effect_date",
                today_text(),
            )
            effect.setdefault("rating", 3)
            effect.setdefault("note", "")
            effect.setdefault(
                "created_at",
                now_text(),
            )

        return data

    except (OSError, ValueError):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS
# =========================================================

def get_seed(data, seed_id):
    return next(
        (
            seed
            for seed in data["seeds"]
            if seed.get("id") == seed_id
        ),
        None,
    )


def get_effect(data, effect_id):
    return next(
        (
            effect
            for effect in data["effects"]
            if effect.get("id") == effect_id
        ),
        None,
    )


def effects_for_seed(data, seed_id):
    effects = [
        effect
        for effect in data["effects"]
        if effect.get("seed_id") == seed_id
    ]

    return sorted(
        effects,
        key=lambda e: (
            e.get("effect_date", ""),
            e.get("created_at", ""),
        ),
    )


def max_effect_rating(data, seed_id):
    effects = effects_for_seed(
        data,
        seed_id,
    )

    if not effects:
        return None

    return max(
        int(e.get("rating", 0))
        for e in effects
    )


def first_effect(data, seed_id):
    effects = effects_for_seed(
        data,
        seed_id,
    )

    if not effects:
        return None

    return effects[0]


def first_effect_days(data, seed):
    effect = first_effect(
        data,
        seed.get("id"),
    )

    if not effect:
        return None

    effect_date = parse_date(
        effect.get("effect_date")
    )

    if not effect_date:
        return None

    return elapsed_days(
        seed,
        effect_date,
    )


def latest_effect(data, seed_id):
    effects = effects_for_seed(
        data,
        seed_id,
    )

    if not effects:
        return None

    return effects[-1]


# =========================================================
# CRUD
# =========================================================

def add_seed(
    data,
    title,
    category,
    minutes,
    initial_feeling,
    initial_note,
    desired_result,
    expected_period,
):
    seed = {
        "id": new_id(),
        "title": title,
        "category": category,
        "minutes": int(minutes),
        "initial_feeling": int(
            initial_feeling
        ),
        "initial_note": initial_note,
        "desired_result": desired_result,
        "expected_period": (
            expected_period
        ),
        "status": "🌱 育っている",
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["seeds"].append(seed)
    save_data(data)


def add_effect(
    data,
    seed_id,
    effect_date,
    rating,
    note,
    status,
):
    effect = {
        "id": new_id(),
        "seed_id": seed_id,
        "effect_date": str(effect_date),
        "rating": int(rating),
        "note": note,
        "created_at": now_text(),
    }

    data["effects"].append(effect)

    seed = get_seed(
        data,
        seed_id,
    )

    if seed:
        seed["status"] = status
        seed["updated_at"] = now_text()

    save_data(data)


def delete_seed(data, seed_id):
    data["seeds"] = [
        seed
        for seed in data["seeds"]
        if seed.get("id") != seed_id
    ]

    data["effects"] = [
        effect
        for effect in data["effects"]
        if effect.get("seed_id") != seed_id
    ]

    save_data(data)


def delete_effect(data, effect_id):
    data["effects"] = [
        effect
        for effect in data["effects"]
        if effect.get("id") != effect_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero {
        padding: 42px 25px;
        text-align: center;
        border-radius: 28px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 180, 110, .13),
                rgba(255, 215, 100, .10),
                rgba(255, 255, 255, .02)
            );
    }

    .seed-card {
        padding: 20px;
        border-radius: 20px;
        border:
            1px solid rgba(100, 180, 120, .18);
        margin-bottom: 12px;
    }

    .growth-card {
        padding: 28px;
        text-align: center;
        border-radius: 24px;
        margin: 15px 0;
        background:
            linear-gradient(
                135deg,
                rgba(90, 190, 120, .10),
                rgba(255, 220, 100, .10)
            );
    }

    .timeline {
        padding-left: 20px;
        border-left:
            3px solid rgba(100, 180, 120, .35);
        margin: 10px 0 10px 10px;
    }

    .timeline-item {
        padding: 10px 0 18px 15px;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(80, 180, 110, .05);
        border:
            1px solid rgba(80, 180, 110, .12);
    }

    .footer {
        text-align: center;
        padding: 34px;
        margin-top: 35px;
        border-radius: 25px;
        background:
            rgba(80, 180, 110, .06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()
seeds = data["seeds"]
effects = data["effects"]
today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>🌱⏳ DAY 306 / 365</div>
        <h1>あとで効いてきた</h1>
        <p>
            今日まいた種が、
            いつか役に立った瞬間を見逃さない。
        </p>
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
    tab_box,
    tab_effect,
    tab_growth,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "🌱 種をまく",
        "📦 種BOX",
        "🌿 効いてきた",
        "🌳 成長記録",
        "📊 分析",
        "📚 種図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    growing_count = sum(
        1
        for seed in seeds
        if seed.get("status")
        == "🌱 育っている"
    )

    effect_seed_ids = set(
        effect.get("seed_id")
        for effect in effects
    )

    effective_count = len(
        effect_seed_ids
    )

    tree_count = sum(
        1
        for seed in seeds
        if seed.get("status")
        == "🌳 効いた！"
    )

    ratings = [
        int(effect.get("rating", 0))
        for effect in effects
    ]

    avg_effect = (
        sum(ratings) / len(ratings)
        if ratings
        else 0
    )

    st.subheader("🌱 今の畑")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🌱 まいた種",
        f"{len(seeds)}個",
    )

    c2.metric(
        "⏳ 育っている",
        f"{growing_count}個",
    )

    c3.metric(
        "🌿 効果を感じた",
        f"{effective_count}個",
    )

    c4.metric(
        "⭐ 平均効果",
        (
            f"{avg_effect:.1f} / 5"
            if ratings
            else "-"
        ),
    )

    # -----------------------------------------------------
    # RECENT SEEDS
    # -----------------------------------------------------

    if seeds:
        st.divider()

        st.subheader(
            "🌱 最近まいた種"
        )

        recent = sorted(
            seeds,
            key=lambda s: s.get(
                "created_at",
                "",
            ),
            reverse=True,
        )

        for seed in recent[:5]:
            days = elapsed_days(seed)

            max_rating = max_effect_rating(
                data,
                seed.get("id"),
            )

            st.markdown(
                f"""
                <div class="seed-card">
                    <b>
                        {seed.get("category")}
                        {seed.get("title")}
                    </b>
                    <br><br>
                    {seed.get("status")}
                    &nbsp;｜&nbsp;
                    {days}日経過
                    <br>
                    最初の手応え：
                    {star_text(seed.get("initial_feeling"))}
                    <br>
                    最大効果：
                    {star_text(max_rating)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # LOW START / HIGH EFFECT
    # -----------------------------------------------------

    surprise_seeds = []

    for seed in seeds:
        max_rating = max_effect_rating(
            data,
            seed.get("id"),
        )

        if (
            int(
                seed.get(
                    "initial_feeling",
                    0,
                )
            ) <= 2
            and max_rating is not None
            and max_rating >= 4
        ):
            surprise_seeds.append(
                (
                    max_rating
                    - int(
                        seed.get(
                            "initial_feeling",
                            0,
                        )
                    ),
                    seed,
                )
            )

    if surprise_seeds:
        st.divider()

        st.subheader(
            "😲 最初は分からなかった。でも…"
        )

        surprise_seeds.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        for diff, seed in surprise_seeds[:5]:
            max_rating = max_effect_rating(
                data,
                seed.get("id"),
            )

            st.write(
                f"**{seed.get('category')} "
                f"{seed.get('title')}**"
            )

            st.caption(
                f"{star_text(seed.get('initial_feeling'))}"
                f" → {star_text(max_rating)} "
                f"｜+{diff}"
            )


# =========================================================
# ADD SEED
# =========================================================

with tab_add:

    st.subheader(
        "🌱 今日まいた種"
    )

    st.caption(
        "すぐに結果が出るかどうかではなく、"
        "今日やったことを残します。"
    )

    with st.form(
        "add_seed_form",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "今日、何をした？",
            placeholder=(
                "例：JavaのScannerを勉強した"
            ),
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        minutes = st.number_input(
            "かけた時間（分）",
            min_value=0,
            max_value=1440,
            value=30,
            step=5,
        )

        initial_feeling = st.slider(
            "今の手応え",
            1,
            5,
            3,
        )

        st.write(
            star_text(initial_feeling)
        )

        initial_note = st.text_area(
            "今の気持ち・手応え",
            placeholder=(
                "例：まだよく分かってない"
            ),
        )

        desired_result = st.text_area(
            "🎯 何につながったら嬉しい？",
            placeholder=(
                "例：Javaのコードを"
                "自力で書けるようになる"
            ),
        )

        expected_period = st.selectbox(
            "いつ頃つながったら嬉しい？",
            EXPECTED_PERIODS,
            index=1,
        )

        submitted = st.form_submit_button(
            "🌱 種をまく",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "今日やったことを入力してね。"
                )

            else:
                add_seed(
                    data=data,
                    title=title.strip(),
                    category=category,
                    minutes=minutes,
                    initial_feeling=(
                        initial_feeling
                    ),
                    initial_note=(
                        initial_note.strip()
                    ),
                    desired_result=(
                        desired_result.strip()
                    ),
                    expected_period=(
                        expected_period
                    ),
                )

                st.rerun()


# =========================================================
# SEED BOX
# =========================================================

with tab_box:

    st.subheader(
        "📦 種BOX"
    )

    if not seeds:
        st.info(
            "まだ種はありません。"
        )

    else:
        status_filter = st.selectbox(
            "状態",
            ["すべて"] + STATUSES,
            key="box_status",
        )

        sort_type = st.selectbox(
            "並び順",
            [
                "新しい順",
                "古い順",
                "経過日数が長い順",
                "最初の手応えが低い順",
            ],
        )

        box_seeds = [
            seed
            for seed in seeds
            if (
                status_filter == "すべて"
                or seed.get("status")
                == status_filter
            )
        ]

        if sort_type == "新しい順":
            box_seeds.sort(
                key=lambda s: s.get(
                    "created_at",
                    "",
                ),
                reverse=True,
            )

        elif sort_type == "古い順":
            box_seeds.sort(
                key=lambda s: s.get(
                    "created_at",
                    "",
                )
            )

        elif (
            sort_type
            == "経過日数が長い順"
        ):
            box_seeds.sort(
                key=lambda s: (
                    elapsed_days(s) or 0
                ),
                reverse=True,
            )

        else:
            box_seeds.sort(
                key=lambda s: int(
                    s.get(
                        "initial_feeling",
                        3,
                    )
                )
            )

        for seed in box_seeds:
            seed_effects = effects_for_seed(
                data,
                seed.get("id"),
            )

            with st.container(border=True):
                st.markdown(
                    f"### {seed.get('category')} "
                    f"{seed.get('title')}"
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "経過",
                    f"{elapsed_days(seed)}日",
                )

                c2.metric(
                    "最初の手応え",
                    f"{seed.get('initial_feeling')} / 5",
                )

                max_rating = max_effect_rating(
                    data,
                    seed.get("id"),
                )

                c3.metric(
                    "最大効果",
                    (
                        f"{max_rating} / 5"
                        if max_rating is not None
                        else "-"
                    ),
                )

                st.write(
                    f"**状態：{seed.get('status')}**"
                )

                if seed.get("initial_note"):
                    st.write(
                        "📝 "
                        + seed.get("initial_note")
                    )

                if seed.get("desired_result"):
                    st.info(
                        "🎯 つながったら嬉しいこと\n\n"
                        + seed.get("desired_result")
                    )

                st.caption(
                    f"期待していた時期："
                    f"{seed.get('expected_period')}"
                    f"｜効果記録："
                    f"{len(seed_effects)}件"
                )


# =========================================================
# ADD EFFECT
# =========================================================

with tab_effect:

    st.subheader(
        "🌿 あれ、効いてきた？"
    )

    if not seeds:
        st.info(
            "まずは種を登録してみよう。"
        )

    else:
        options = {
            seed_label(seed): seed.get("id")
            for seed in seeds
        }

        selected_label = st.selectbox(
            "どの種に変化があった？",
            list(options.keys()),
            key="effect_seed",
        )

        selected_id = options[
            selected_label
        ]

        seed = get_seed(
            data,
            selected_id,
        )

        st.markdown(
            f"### {seed.get('category')} "
            f"{seed.get('title')}"
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "🌱 経過日数",
            f"{elapsed_days(seed)}日",
        )

        c2.metric(
            "最初の手応え",
            f"{seed.get('initial_feeling')} / 5",
        )

        if seed.get("initial_note"):
            st.caption(
                "当時："
                + seed.get("initial_note")
            )

        with st.form(
            "add_effect_form"
        ):
            effect_date = st.date_input(
                "いつ効果を感じた？",
                value=today,
                max_value=today,
            )

            rating = st.slider(
                "効果実感",
                1,
                5,
                3,
            )

            st.write(
                star_text(rating)
            )

            note = st.text_area(
                "何が起きた？",
                placeholder=(
                    "例：コードを見たときに"
                    "Scannerの意味が普通に分かった"
                ),
            )

            current_status = seed.get(
                "status",
                "🌱 育っている",
            )

            status_index = (
                STATUSES.index(
                    current_status
                )
                if current_status in STATUSES
                else 0
            )

            status = st.selectbox(
                "今の状態",
                STATUSES,
                index=status_index,
            )

            submitted = st.form_submit_button(
                "🌿 成長記録を追加",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                seed_start = created_date(seed)

                if (
                    seed_start
                    and effect_date < seed_start
                ):
                    st.warning(
                        "種をまいた日より前の日付には"
                        "できません。"
                    )

                elif not note.strip():
                    st.warning(
                        "何が起きたかを"
                        "少し残してみよう。"
                    )

                else:
                    add_effect(
                        data=data,
                        seed_id=selected_id,
                        effect_date=effect_date,
                        rating=rating,
                        note=note.strip(),
                        status=status,
                    )

                    st.rerun()


# =========================================================
# GROWTH TIMELINE
# =========================================================

with tab_growth:

    st.subheader(
        "🌳 成長記録"
    )

    if not seeds:
        st.info(
            "まだ記録がありません。"
        )

    else:
        options = {
            seed_label(seed): seed.get("id")
            for seed in seeds
        }

        selected_label = st.selectbox(
            "成長を見る種",
            list(options.keys()),
            key="growth_seed",
        )

        selected_id = options[
            selected_label
        ]

        seed = get_seed(
            data,
            selected_id,
        )

        seed_effects = effects_for_seed(
            data,
            selected_id,
        )

        st.markdown(
            f"## {seed.get('category')} "
            f"{seed.get('title')}"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "経過",
            f"{elapsed_days(seed)}日",
        )

        c2.metric(
            "投資時間",
            f"{seed.get('minutes', 0)}分",
        )

        c3.metric(
            "最初",
            f"{seed.get('initial_feeling')} / 5",
        )

        max_rating = max_effect_rating(
            data,
            selected_id,
        )

        c4.metric(
            "最大効果",
            (
                f"{max_rating} / 5"
                if max_rating is not None
                else "-"
            ),
        )

        if seed_effects:
            first_days = first_effect_days(
                data,
                seed,
            )

            st.markdown(
                f"""
                <div class="growth-card">
                    🌱 種をまいてから
                    <br>
                    <span style="font-size:2rem;">
                        <b>{first_days}日後</b>
                    </span>
                    <br>
                    最初の「効いてきた」が
                    記録されました。
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### 🕰️ タイムライン")

        start = created_date(seed)

        st.markdown(
            f"""
            <div class="timeline">
                <div class="timeline-item">
                    <b>🌱 {start.strftime("%Y/%m/%d") if start else "-"}</b>
                    <br>
                    種をまいた
                    <br>
                    {star_text(seed.get("initial_feeling"))}
                    <br>
                    {seed.get("initial_note", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not seed_effects:
            st.caption(
                "まだ成長記録はありません。"
            )

        for effect in seed_effects:
            e_date = parse_date(
                effect.get("effect_date")
            )

            days = (
                elapsed_days(seed, e_date)
                if e_date
                else None
            )

            icon = (
                "🌳"
                if int(effect.get("rating", 0)) >= 4
                else "🌿"
            )

            st.markdown(
                f"""
                <div class="timeline">
                    <div class="timeline-item">
                        <b>
                            {icon}
                            {e_date.strftime("%Y/%m/%d") if e_date else "-"}
                        </b>
                        <br>
                        {days}日後
                        <br>
                        {star_text(effect.get("rating"))}
                        <br>
                        {effect.get("note", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 努力はいつ効いてきた？"
    )

    if not seeds:
        st.info(
            "種をまいていくと、"
            "ここに分析が育ちます。"
        )

    else:
        effective_seeds = [
            seed
            for seed in seeds
            if first_effect(
                data,
                seed.get("id"),
            )
            is not None
        ]

        first_days_list = [
            first_effect_days(
                data,
                seed,
            )
            for seed in effective_seeds
        ]

        first_days_list = [
            days
            for days in first_days_list
            if days is not None
        ]

        avg_days = (
            sum(first_days_list)
            / len(first_days_list)
            if first_days_list
            else None
        )

        max_ratings = [
            max_effect_rating(
                data,
                seed.get("id"),
            )
            for seed in seeds
        ]

        max_ratings = [
            value
            for value in max_ratings
            if value is not None
        ]

        avg_max = (
            sum(max_ratings)
            / len(max_ratings)
            if max_ratings
            else None
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "🌱 種",
            f"{len(seeds)}個",
        )

        c2.metric(
            "🌿 効果あり",
            f"{len(effective_seeds)}個",
        )

        c3.metric(
            "⏳ 最初の効果まで",
            (
                f"{avg_days:.1f}日"
                if avg_days is not None
                else "-"
            ),
        )

        c4.metric(
            "⭐ 平均最大効果",
            (
                f"{avg_max:.1f}"
                if avg_max is not None
                else "-"
            ),
        )

        # -------------------------------------------------
        # CATEGORY ANALYSIS
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🧠 カテゴリー別"
        )

        category_rows = []

        for category in CATEGORIES:
            category_seeds = [
                seed
                for seed in seeds
                if seed.get("category")
                == category
            ]

            if not category_seeds:
                continue

            category_effective = [
                seed
                for seed in category_seeds
                if first_effect(
                    data,
                    seed.get("id"),
                )
                is not None
            ]

            category_days = [
                first_effect_days(
                    data,
                    seed,
                )
                for seed in category_effective
            ]

            category_days = [
                d
                for d in category_days
                if d is not None
            ]

            category_ratings = [
                max_effect_rating(
                    data,
                    seed.get("id"),
                )
                for seed in category_seeds
            ]

            category_ratings = [
                r
                for r in category_ratings
                if r is not None
            ]

            category_minutes = [
                int(
                    seed.get(
                        "minutes",
                        0,
                    )
                )
                for seed in category_seeds
            ]

            category_rows.append(
                {
                    "カテゴリー": category,
                    "種": len(
                        category_seeds
                    ),
                    "効果あり": len(
                        category_effective
                    ),
                    "平均投資分": round(
                        sum(category_minutes)
                        / len(category_minutes),
                        1,
                    ),
                    "平均効果日数": (
                        round(
                            sum(category_days)
                            / len(category_days),
                            1,
                        )
                        if category_days
                        else None
                    ),
                    "平均最大効果": (
                        round(
                            sum(category_ratings)
                            / len(category_ratings),
                            1,
                        )
                        if category_ratings
                        else None
                    ),
                }
            )

        category_df = pd.DataFrame(
            category_rows
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        chart_df = (
            category_df[
                [
                    "カテゴリー",
                    "平均最大効果",
                ]
            ]
            .dropna()
            .set_index("カテゴリー")
        )

        if not chart_df.empty:
            st.bar_chart(chart_df)

        # -------------------------------------------------
        # RANKING
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🌳 あとで効いたランキング"
        )

        ranking = []

        for seed in seeds:
            rating = max_effect_rating(
                data,
                seed.get("id"),
            )

            if rating is None:
                continue

            diff = (
                rating
                - int(
                    seed.get(
                        "initial_feeling",
                        0,
                    )
                )
            )

            ranking.append(
                (
                    rating,
                    diff,
                    seed,
                )
            )

        ranking.sort(
            key=lambda x: (
                x[0],
                x[1],
            ),
            reverse=True,
        )

        for index, (
            rating,
            diff,
            seed,
        ) in enumerate(
            ranking[:10],
            start=1,
        ):
            st.write(
                f"**{index}. "
                f"{seed.get('title')}**"
            )

            diff_text = (
                f"+{diff}"
                if diff > 0
                else str(diff)
            )

            st.caption(
                f"{star_text(seed.get('initial_feeling'))}"
                f" → {star_text(rating)} "
                f"｜差 {diff_text}"
            )

        # -------------------------------------------------
        # SURPRISE
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 😲 最初は意味が分からなかった"
        )

        surprise = []

        for seed in seeds:
            initial = int(
                seed.get(
                    "initial_feeling",
                    0,
                )
            )

            rating = max_effect_rating(
                data,
                seed.get("id"),
            )

            if (
                initial <= 2
                and rating is not None
                and rating >= 4
            ):
                surprise.append(
                    (
                        rating - initial,
                        seed,
                    )
                )

        surprise.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        if not surprise:
            st.caption(
                "まだ該当する記録はありません。"
            )

        for diff, seed in surprise:
            latest = latest_effect(
                data,
                seed.get("id"),
            )

            with st.container(border=True):
                st.write(
                    f"**{seed.get('category')} "
                    f"{seed.get('title')}**"
                )

                st.write(
                    f"{star_text(seed.get('initial_feeling'))}"
                    f" → "
                    f"{star_text(max_effect_rating(data, seed.get('id')))}"
                )

                if seed.get("initial_note"):
                    st.caption(
                        "当時："
                        + seed.get("initial_note")
                    )

                if latest:
                    st.success(
                        latest.get(
                            "note",
                            "",
                        )
                    )

        # -------------------------------------------------
        # MONTHLY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 📅 月別の種まき"
        )

        monthly_seed_rows = []

        for seed in seeds:
            created = parse_datetime(
                seed.get("created_at")
            )

            if not created:
                continue

            monthly_seed_rows.append(
                {
                    "月": created.strftime(
                        "%Y-%m"
                    ),
                    "種": 1,
                }
            )

        if monthly_seed_rows:
            monthly_df = pd.DataFrame(
                monthly_seed_rows
            )

            monthly_summary = (
                monthly_df
                .groupby("月")["種"]
                .sum()
                .to_frame()
            )

            st.bar_chart(
                monthly_summary
            )

        # -------------------------------------------------
        # RANDOM OLD SEED
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🎲 昔まいた種"
        )

        old_candidates = [
            seed
            for seed in seeds
            if (
                elapsed_days(seed) is not None
                and elapsed_days(seed) >= 30
                and seed.get("status")
                in [
                    "🌱 育っている",
                    "🌿 少し効いてきた",
                ]
            )
        ]

        if not old_candidates:
            st.caption(
                "30日以上経った育成中の種が"
                "ここに現れます。"
            )

        else:
            candidate_ids = [
                seed.get("id")
                for seed in old_candidates
            ]

            random_id = st.session_state.get(
                "old_seed_random_id"
            )

            if random_id not in candidate_ids:
                random_id = random.choice(
                    candidate_ids
                )

                st.session_state[
                    "old_seed_random_id"
                ] = random_id

            random_seed = get_seed(
                data,
                random_id,
            )

            with st.container(border=True):
                st.markdown(
                    f"### {random_seed.get('category')} "
                    f"{random_seed.get('title')}"
                )

                st.write(
                    f"🌱 **{elapsed_days(random_seed)}日前**"
                    "にまいた種"
                )

                if random_seed.get(
                    "desired_result"
                ):
                    st.info(
                        "当時期待していたこと\n\n"
                        + random_seed.get(
                            "desired_result"
                        )
                    )

                st.write(
                    "**今、何かにつながってない？**"
                )

            if st.button(
                "🎲 別の種を見る",
                use_container_width=True,
            ):
                alternatives = [
                    seed_id
                    for seed_id in candidate_ids
                    if seed_id != random_id
                ]

                if alternatives:
                    st.session_state[
                        "old_seed_random_id"
                    ] = random.choice(
                        alternatives
                    )

                st.rerun()


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 種図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    c1, c2 = st.columns(2)

    with c1:
        category_filter = st.selectbox(
            "カテゴリー",
            ["すべて"] + CATEGORIES,
            key="library_category",
        )

    with c2:
        status_filter = st.selectbox(
            "状態",
            ["すべて"] + STATUSES,
            key="library_status",
        )

    min_initial = st.slider(
        "最低初期手応え",
        1,
        5,
        1,
    )

    rows = []

    for seed in seeds:
        if (
            category_filter != "すべて"
            and seed.get("category")
            != category_filter
        ):
            continue

        if (
            status_filter != "すべて"
            and seed.get("status")
            != status_filter
        ):
            continue

        if (
            int(
                seed.get(
                    "initial_feeling",
                    0,
                )
            )
            < min_initial
        ):
            continue

        searchable = " ".join(
            [
                seed.get("title", ""),
                seed.get(
                    "initial_note",
                    "",
                ),
                seed.get(
                    "desired_result",
                    "",
                ),
            ]
        ).lower()

        if (
            search.strip()
            and search.lower().strip()
            not in searchable
        ):
            continue

        max_rating = max_effect_rating(
            data,
            seed.get("id"),
        )

        start = created_date(seed)

        rows.append(
            {
                "種": seed.get("title"),
                "カテゴリー": (
                    seed.get("category")
                ),
                "日付": (
                    start.strftime("%Y/%m/%d")
                    if start
                    else "-"
                ),
                "経過日数": (
                    elapsed_days(seed)
                ),
                "最初": (
                    seed.get(
                        "initial_feeling"
                    )
                ),
                "最大効果": (
                    max_rating
                    if max_rating is not None
                    else "-"
                ),
                "効果記録": len(
                    effects_for_seed(
                        data,
                        seed.get("id"),
                    )
                ),
                "状態": seed.get("status"),
            }
        )

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "条件に合う種はありません。"
        )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 記録を管理"
    )

    if not seeds:
        st.info(
            "まだ種がありません。"
        )

    else:
        options = {
            seed_label(seed): seed.get("id")
            for seed in seeds
        }

        selected_label = st.selectbox(
            "編集する種",
            list(options.keys()),
            key="manage_seed",
        )

        selected_id = options[
            selected_label
        ]

        seed = get_seed(
            data,
            selected_id,
        )

        edit_title = st.text_input(
            "タイトル",
            value=seed.get(
                "title",
                "",
            ),
        )

        old_category = seed.get(
            "category",
            "🌱 その他",
        )

        category_index = (
            CATEGORIES.index(
                old_category
            )
            if old_category in CATEGORIES
            else len(CATEGORIES) - 1
        )

        edit_category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
            index=category_index,
            key="manage_category",
        )

        edit_minutes = st.number_input(
            "かけた時間（分）",
            min_value=0,
            max_value=1440,
            value=int(
                seed.get(
                    "minutes",
                    0,
                )
            ),
            step=5,
        )

        edit_initial = st.slider(
            "最初の手応え",
            1,
            5,
            int(
                seed.get(
                    "initial_feeling",
                    3,
                )
            ),
        )

        edit_note = st.text_area(
            "最初のメモ",
            value=seed.get(
                "initial_note",
                "",
            ),
        )

        edit_desired = st.text_area(
            "何につながったら嬉しい？",
            value=seed.get(
                "desired_result",
                "",
            ),
        )

        old_period = seed.get(
            "expected_period",
            "分からない",
        )

        period_index = (
            EXPECTED_PERIODS.index(
                old_period
            )
            if old_period
            in EXPECTED_PERIODS
            else len(
                EXPECTED_PERIODS
            ) - 1
        )

        edit_period = st.selectbox(
            "期待していた時期",
            EXPECTED_PERIODS,
            index=period_index,
        )

        old_status = seed.get(
            "status",
            "🌱 育っている",
        )

        status_index = (
            STATUSES.index(old_status)
            if old_status in STATUSES
            else 0
        )

        edit_status = st.selectbox(
            "状態",
            STATUSES,
            index=status_index,
            key="manage_status",
        )

        if st.button(
            "💾 種を保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "タイトルを入力してね。"
                )

            else:
                seed["title"] = (
                    edit_title.strip()
                )
                seed["category"] = (
                    edit_category
                )
                seed["minutes"] = int(
                    edit_minutes
                )
                seed[
                    "initial_feeling"
                ] = int(
                    edit_initial
                )
                seed["initial_note"] = (
                    edit_note.strip()
                )
                seed["desired_result"] = (
                    edit_desired.strip()
                )
                seed["expected_period"] = (
                    edit_period
                )
                seed["status"] = (
                    edit_status
                )
                seed["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # EFFECT MANAGEMENT
        # -------------------------------------------------

        seed_effects = effects_for_seed(
            data,
            selected_id,
        )

        st.divider()

        st.subheader(
            "🌿 効果記録"
        )

        if not seed_effects:
            st.caption(
                "まだ効果記録はありません。"
            )

        else:
            effect_options = {
                (
                    f"{effect.get('effect_date')} "
                    f"｜{star_text(effect.get('rating'))} "
                    f"[{effect.get('id', '')[:6]}]"
                ): effect.get("id")
                for effect in seed_effects
            }

            effect_label = st.selectbox(
                "編集する効果記録",
                list(
                    effect_options.keys()
                ),
            )

            effect_id = effect_options[
                effect_label
            ]

            effect = get_effect(
                data,
                effect_id,
            )

            current_effect_date = (
                parse_date(
                    effect.get(
                        "effect_date"
                    )
                )
                or today
            )

            edit_effect_date = (
                st.date_input(
                    "効果を感じた日",
                    value=current_effect_date,
                    max_value=today,
                    key="manage_effect_date",
                )
            )

            edit_rating = st.slider(
                "効果実感",
                1,
                5,
                int(
                    effect.get(
                        "rating",
                        3,
                    )
                ),
                key="manage_rating",
            )

            edit_effect_note = (
                st.text_area(
                    "効果メモ",
                    value=effect.get(
                        "note",
                        "",
                    ),
                    key="manage_effect_note",
                )
            )

            if st.button(
                "💾 効果記録を保存",
                use_container_width=True,
            ):
                start = created_date(seed)

                if (
                    start
                    and edit_effect_date
                    < start
                ):
                    st.warning(
                        "種をまいた日より"
                        "前の日付にはできません。"
                    )

                else:
                    effect["effect_date"] = (
                        str(edit_effect_date)
                    )
                    effect["rating"] = int(
                        edit_rating
                    )
                    effect["note"] = (
                        edit_effect_note.strip()
                    )

                    seed["updated_at"] = (
                        now_text()
                    )

                    save_data(data)
                    st.rerun()

            confirm_effect_delete = (
                st.checkbox(
                    "この効果記録を削除する",
                    key=(
                        "effect_delete_confirm_"
                        + effect_id
                    ),
                )
            )

            if st.button(
                "🗑️ 効果記録を削除",
                disabled=(
                    not confirm_effect_delete
                ),
                key=(
                    "effect_delete_"
                    + effect_id
                ),
                use_container_width=True,
            ):
                delete_effect(
                    data,
                    effect_id,
                )

                st.rerun()

        # -------------------------------------------------
        # SEED DELETE
        # -------------------------------------------------

        st.divider()

        st.warning(
            "種を削除すると、"
            "その種の成長記録もすべて削除されます。"
        )

        confirm_delete = st.checkbox(
            "この種を完全に削除する",
            key=(
                "seed_delete_confirm_"
                + selected_id
            ),
        )

        if st.button(
            "🗑️ 種を完全削除",
            disabled=not confirm_delete,
            key=(
                "seed_delete_"
                + selected_id
            ),
            use_container_width=True,
        ):
            delete_seed(
                data,
                selected_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    backup_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=backup_text,
        file_name=(
            f"later_effect_{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <p>
            <b>
                今日の努力が、
                今日報われるとは限らない。
            </b>
        </p>

        <p>
            忘れた頃に、
            「あれ、前にやったことが役立ってる」
            と気づく日がある。
        </p>

        <p>
            だから、今日まいた種を残しておこう。
        </p>

        <p>
            <b>
                成果が少し遅れてやってきても、
                見逃さないために。🌱
            </b>
        </p>

        <br>

        <b>
            DAY 306 / 365 — COMPLETE 🔥
        </b>
    </div>
    """,
    unsafe_allow_html=True,
)
