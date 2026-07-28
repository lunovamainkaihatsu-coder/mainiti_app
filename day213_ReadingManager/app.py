import json
import os
import random
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =====================================
# ページ設定
# =====================================

st.set_page_config(
    page_title="積読・読書管理",
    page_icon="📚",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "books.json"
)


READING_STATUSES = [
    "読みたい",
    "積読",
    "読書中",
    "読了",
    "中断",
    "再読予定"
]


STATUS_ICONS = {
    "読みたい": "💭",
    "積読": "📚",
    "読書中": "📖",
    "読了": "✅",
    "中断": "⏸️",
    "再読予定": "🔁"
}


GENRES = [
    "AI・テクノロジー",
    "起業・経営",
    "ビジネス",
    "自己啓発",
    "心理学",
    "健康",
    "筋トレ",
    "投資・お金",
    "歴史",
    "社会",
    "哲学",
    "宗教・スピリチュアル",
    "小説",
    "漫画",
    "エッセイ",
    "その他"
]


FORMATS = [
    "紙",
    "電子書籍",
    "オーディオブック",
    "図書館",
    "その他"
]


PRIORITIES = [
    "最優先",
    "高",
    "中",
    "低"
]


PRIORITY_ICONS = {
    "最優先": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵"
}


PRIORITY_ORDER = {
    "最優先": 0,
    "高": 1,
    "中": 2,
    "低": 3
}


# =====================================
# データ管理
# =====================================

def create_empty_data():
    """空の初期データを作成する。"""

    return {
        "books": []
    }


def save_data(data):
    """データをJSONファイルへ保存する。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "保存データの形式が正しくありません。"
            )

        data.setdefault(
            "books",
            []
        )

        for book in data["books"]:
            book.setdefault(
                "id",
                create_id()
            )

            book.setdefault(
                "title",
                ""
            )

            book.setdefault(
                "author",
                ""
            )

            book.setdefault(
                "publisher",
                ""
            )

            book.setdefault(
                "genre",
                "その他"
            )

            book.setdefault(
                "format",
                "紙"
            )

            book.setdefault(
                "status",
                "読みたい"
            )

            book.setdefault(
                "priority",
                "中"
            )

            book.setdefault(
                "purchase_date",
                ""
            )

            book.setdefault(
                "start_date",
                ""
            )

            book.setdefault(
                "finish_date",
                ""
            )

            book.setdefault(
                "current_page",
                0
            )

            book.setdefault(
                "total_pages",
                0
            )

            book.setdefault(
                "rating",
                0
            )

            book.setdefault(
                "summary",
                ""
            )

            book.setdefault(
                "learning",
                ""
            )

            book.setdefault(
                "quote",
                ""
            )

            book.setdefault(
                "next_action",
                ""
            )

            book.setdefault(
                "memo",
                ""
            )

            book.setdefault(
                "logs",
                []
            )

            book.setdefault(
                "created_at",
                ""
            )

            book.setdefault(
                "updated_at",
                ""
            )

            for log in book["logs"]:
                log.setdefault(
                    "id",
                    create_id()
                )

                log.setdefault(
                    "log_date",
                    str(
                        date.today()
                    )
                )

                log.setdefault(
                    "page",
                    0
                )

                log.setdefault(
                    "content",
                    ""
                )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data


# =====================================
# 補助関数
# =====================================

def create_id():
    """一意のIDを生成する。"""

    return str(
        uuid.uuid4()
    )


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date_text(
    date_text
):
    """日付文字列をdate型に変換する。"""

    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except (
        ValueError,
        TypeError
    ):
        return None


def format_date(
    date_text
):
    """日付を日本語表示にする。"""

    parsed_date = parse_date_text(
        date_text
    )

    if not parsed_date:
        return "未設定"

    return parsed_date.strftime(
        "%Y年%m月%d日"
    )


def get_book_by_id(
    data,
    book_id
):
    """IDから本を取得する。"""

    for book in data["books"]:
        if book.get(
            "id"
        ) == book_id:
            return book

    return None


def calculate_progress(
    current_page,
    total_pages
):
    """読書進捗率を計算する。"""

    try:
        current_page = int(
            current_page
        )

        total_pages = int(
            total_pages
        )

    except (
        ValueError,
        TypeError
    ):
        return 0

    if total_pages <= 0:
        return 0

    progress = (
        current_page
        / total_pages
        * 100
    )

    return min(
        max(
            progress,
            0
        ),
        100
    )


def count_finished_this_month(
    books
):
    """今月読了した冊数を数える。"""

    today = date.today()
    count = 0

    for book in books:
        finish_date = parse_date_text(
            book.get(
                "finish_date",
                ""
            )
        )

        if (
            finish_date
            and finish_date.year
            == today.year
            and finish_date.month
            == today.month
        ):
            count += 1

    return count


def get_average_rating(
    books
):
    """読了本の平均評価を計算する。"""

    ratings = [
        int(
            book.get(
                "rating",
                0
            )
        )
        for book in books
        if int(
            book.get(
                "rating",
                0
            )
        ) > 0
    ]

    if not ratings:
        return 0

    return (
        sum(ratings)
        / len(ratings)
    )


def get_completion_rate(
    books
):
    """登録本の読了率を計算する。"""

    if not books:
        return 0

    finished_count = len(
        [
            book
            for book in books
            if book.get(
                "status"
            ) == "読了"
        ]
    )

    return (
        finished_count
        / len(books)
        * 100
    )


def get_display_title(
    book
):
    """本の表示名を作成する。"""

    title = book.get(
        "title",
        "無題"
    )

    author = book.get(
        "author",
        ""
    )

    if author:
        return f"{title}／{author}"

    return title


# =====================================
# データ操作
# =====================================

def add_book(
    data,
    title,
    author,
    publisher,
    genre,
    book_format,
    status,
    priority,
    purchase_date,
    start_date,
    finish_date,
    current_page,
    total_pages,
    rating,
    summary,
    learning,
    quote,
    next_action,
    memo
):
    """新しい本を登録する。"""

    book = {
        "id": create_id(),
        "title": title,
        "author": author,
        "publisher": publisher,
        "genre": genre,
        "format": book_format,
        "status": status,
        "priority": priority,
        "purchase_date": (
            str(
                purchase_date
            )
            if purchase_date
            else ""
        ),
        "start_date": (
            str(
                start_date
            )
            if start_date
            else ""
        ),
        "finish_date": (
            str(
                finish_date
            )
            if finish_date
            else ""
        ),
        "current_page": int(
            current_page
        ),
        "total_pages": int(
            total_pages
        ),
        "rating": int(
            rating
        ),
        "summary": summary,
        "learning": learning,
        "quote": quote,
        "next_action": next_action,
        "memo": memo,
        "logs": [],
        "created_at": now_text(),
        "updated_at": ""
    }

    data["books"].append(
        book
    )

    save_data(data)


def update_book(
    data,
    book_id,
    title,
    author,
    publisher,
    genre,
    book_format,
    status,
    priority,
    purchase_date,
    start_date,
    finish_date,
    current_page,
    total_pages,
    rating,
    summary,
    learning,
    quote,
    next_action,
    memo
):
    """本の情報を更新する。"""

    book = get_book_by_id(
        data,
        book_id
    )

    if not book:
        return

    book["title"] = title
    book["author"] = author
    book["publisher"] = publisher
    book["genre"] = genre
    book["format"] = book_format
    book["status"] = status
    book["priority"] = priority
    book["purchase_date"] = (
        str(
            purchase_date
        )
        if purchase_date
        else ""
    )
    book["start_date"] = (
        str(
            start_date
        )
        if start_date
        else ""
    )
    book["finish_date"] = (
        str(
            finish_date
        )
        if finish_date
        else ""
    )
    book["current_page"] = int(
        current_page
    )
    book["total_pages"] = int(
        total_pages
    )
    book["rating"] = int(
        rating
    )
    book["summary"] = summary
    book["learning"] = learning
    book["quote"] = quote
    book["next_action"] = next_action
    book["memo"] = memo
    book["updated_at"] = now_text()

    save_data(data)


def delete_book(
    data,
    book_id
):
    """本を削除する。"""

    data["books"] = [
        book
        for book in data["books"]
        if book.get(
            "id"
        ) != book_id
    ]

    save_data(data)


def add_reading_log(
    data,
    book_id,
    log_date,
    page,
    content
):
    """読書ログを追加する。"""

    book = get_book_by_id(
        data,
        book_id
    )

    if not book:
        return

    log = {
        "id": create_id(),
        "log_date": str(
            log_date
        ),
        "page": int(
            page
        ),
        "content": content,
        "created_at": now_text()
    }

    book["logs"].append(
        log
    )

    if int(
        page
    ) > int(
        book.get(
            "current_page",
            0
        )
    ):
        book["current_page"] = int(
            page
        )

    if book.get(
        "status"
    ) in [
        "読みたい",
        "積読"
    ]:
        book["status"] = "読書中"

        if not book.get(
            "start_date"
        ):
            book["start_date"] = str(
                log_date
            )

    book["updated_at"] = now_text()

    save_data(data)


def delete_reading_log(
    data,
    book_id,
    log_id
):
    """読書ログを削除する。"""

    book = get_book_by_id(
        data,
        book_id
    )

    if not book:
        return

    book["logs"] = [
        log
        for log in book.get(
            "logs",
            []
        )
        if log.get(
            "id"
        ) != log_id
    ]

    book["updated_at"] = now_text()

    save_data(data)


def mark_as_finished(
    data,
    book_id
):
    """本を読了状態にする。"""

    book = get_book_by_id(
        data,
        book_id
    )

    if not book:
        return

    book["status"] = "読了"
    book["finish_date"] = str(
        date.today()
    )

    total_pages = int(
        book.get(
            "total_pages",
            0
        )
    )

    if total_pages > 0:
        book["current_page"] = (
            total_pages
        )

    book["updated_at"] = now_text()

    save_data(data)


# =====================================
# データ読み込み
# =====================================

data = load_data()

books = data["books"]


# =====================================
# タイトル
# =====================================

st.title(
    "📚 積読・読書管理"
)

st.caption(
    "読みたい本から読了後の学びまで、"
    "読書の記録をまとめて管理するアプリです。"
)


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header(
    "📊 読書ダッシュボード"
)

registered_count = len(
    books
)

unread_count = len(
    [
        book
        for book in books
        if book.get(
            "status"
        ) == "積読"
    ]
)

reading_count = len(
    [
        book
        for book in books
        if book.get(
            "status"
        ) == "読書中"
    ]
)

finished_count = len(
    [
        book
        for book in books
        if book.get(
            "status"
        ) == "読了"
    ]
)

reread_count = len(
    [
        book
        for book in books
        if book.get(
            "status"
        ) == "再読予定"
    ]
)

monthly_finished_count = (
    count_finished_this_month(
        books
    )
)

average_rating = get_average_rating(
    books
)

completion_rate = get_completion_rate(
    books
)


metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(4)
)

with metric_col1:
    st.metric(
        "登録冊数",
        f"{registered_count}冊"
    )

with metric_col2:
    st.metric(
        "積読",
        f"{unread_count}冊"
    )

with metric_col3:
    st.metric(
        "読書中",
        f"{reading_count}冊"
    )

with metric_col4:
    st.metric(
        "読了",
        f"{finished_count}冊"
    )


metric_col5, metric_col6, metric_col7, metric_col8 = (
    st.columns(4)
)

with metric_col5:
    st.metric(
        "今月の読了",
        f"{monthly_finished_count}冊"
    )

with metric_col6:
    st.metric(
        "平均評価",
        (
            f"{average_rating:.1f} / 5"
            if average_rating > 0
            else "未評価"
        )
    )

with metric_col7:
    st.metric(
        "再読予定",
        f"{reread_count}冊"
    )

with metric_col8:
    st.metric(
        "読了率",
        f"{completion_rate:.1f}%"
    )


# =====================================
# 読書中の本
# =====================================

reading_books = [
    book
    for book in books
    if book.get(
        "status"
    ) == "読書中"
]

if reading_books:
    st.divider()

    st.header(
        "📖 現在読んでいる本"
    )

    for book in reading_books:
        progress = calculate_progress(
            book.get(
                "current_page",
                0
            ),
            book.get(
                "total_pages",
                0
            )
        )

        with st.container(
            border=True
        ):
            title_col, progress_col = (
                st.columns(
                    [3, 1]
                )
            )

            with title_col:
                st.subheader(
                    book.get(
                        "title",
                        ""
                    )
                )

                if book.get(
                    "author",
                    ""
                ):
                    st.caption(
                        f"著者："
                        f"{book.get('author', '')}"
                    )

            with progress_col:
                st.metric(
                    "進捗",
                    f"{progress:.0f}%"
                )

            st.progress(
                progress / 100
            )

            st.caption(
                f"{book.get('current_page', 0)}ページ "
                f"／ {book.get('total_pages', 0)}ページ"
            )


# =====================================
# 今日の学び
# =====================================

learning_books = [
    book
    for book in books
    if (
        book.get(
            "status"
        ) == "読了"
        and book.get(
            "learning",
            ""
        ).strip()
    )
]

if learning_books:
    st.divider()

    st.header(
        "💡 今日の読書の学び"
    )

    if (
        "random_learning_book_id"
        not in st.session_state
    ):
        st.session_state[
            "random_learning_book_id"
        ] = random.choice(
            learning_books
        ).get(
            "id"
        )

    random_book = get_book_by_id(
        data,
        st.session_state[
            "random_learning_book_id"
        ]
    )

    if random_book:
        with st.container(
            border=True
        ):
            st.subheader(
                random_book.get(
                    "title",
                    ""
                )
            )

            if random_book.get(
                "author",
                ""
            ):
                st.caption(
                    f"著者："
                    f"{random_book.get('author', '')}"
                )

            st.info(
                random_book.get(
                    "learning",
                    ""
                )
            )

            if random_book.get(
                "next_action",
                ""
            ):
                st.success(
                    f"次に試すこと：\n\n"
                    f"{random_book.get('next_action', '')}"
                )

    if st.button(
        "🔄 別の学びを表示"
    ):
        st.session_state[
            "random_learning_book_id"
        ] = random.choice(
            learning_books
        ).get(
            "id"
        )

        st.rerun()


# =====================================
# タブ
# =====================================

st.divider()

add_tab, list_tab, log_tab, completed_tab, analysis_tab = (
    st.tabs(
        [
            "➕ 本を登録",
            "📚 本棚",
            "📝 読書ログ",
            "✅ 読了記録",
            "📈 読書分析"
        ]
    )
)


# =====================================
# 本の登録
# =====================================

with add_tab:
    st.header(
        "➕ 新しい本を登録"
    )

    with st.form(
        "add_book_form",
        clear_on_submit=True
    ):
        form_col1, form_col2 = (
            st.columns(2)
        )

        with form_col1:
            title = st.text_input(
                "本のタイトル",
                placeholder=(
                    "例：AI時代の超発想法"
                )
            )

            author = st.text_input(
                "著者",
                placeholder=(
                    "例：野口悠紀雄"
                )
            )

            publisher = st.text_input(
                "出版社",
                placeholder=(
                    "任意"
                )
            )

            genre = st.selectbox(
                "ジャンル",
                GENRES
            )

            book_format = st.selectbox(
                "書籍形式",
                FORMATS
            )

            priority = st.selectbox(
                "読む優先度",
                PRIORITIES,
                index=2
            )

        with form_col2:
            status = st.selectbox(
                "読書状態",
                READING_STATUSES,
                index=0
            )

            total_pages = st.number_input(
                "総ページ数",
                min_value=0,
                max_value=10000,
                value=0,
                step=1
            )

            current_page = st.number_input(
                "現在ページ",
                min_value=0,
                max_value=10000,
                value=0,
                step=1
            )

            rating = st.slider(
                "評価",
                min_value=0,
                max_value=5,
                value=0,
                help=(
                    "未読・未評価の場合は0"
                )
            )

            has_purchase_date = st.checkbox(
                "購入日を設定する"
            )

            purchase_date = None

            if has_purchase_date:
                purchase_date = st.date_input(
                    "購入日",
                    value=date.today(),
                    max_value=date.today()
                )

            has_start_date = st.checkbox(
                "読書開始日を設定する"
            )

            start_date = None

            if has_start_date:
                start_date = st.date_input(
                    "読書開始日",
                    value=date.today(),
                    max_value=date.today()
                )

            has_finish_date = st.checkbox(
                "読了日を設定する"
            )

            finish_date = None

            if has_finish_date:
                finish_date = st.date_input(
                    "読了日",
                    value=date.today(),
                    max_value=date.today()
                )

        st.subheader(
            "📝 読書メモ"
        )

        summary = st.text_area(
            "本の概要・感想",
            placeholder=(
                "どんな本か、読んで感じたこと"
            ),
            height=100
        )

        learning = st.text_area(
            "学び",
            placeholder=(
                "この本から得た重要な学び"
            ),
            height=100
        )

        quote = st.text_area(
            "印象に残った言葉",
            placeholder=(
                "心に残った言葉や考え方"
            ),
            height=80
        )

        next_action = st.text_area(
            "次に試すこと",
            placeholder=(
                "学びをどのような行動につなげるか"
            ),
            height=80
        )

        memo = st.text_area(
            "自由メモ",
            placeholder=(
                "そのほか残しておきたいこと"
            ),
            height=80
        )

        submit = st.form_submit_button(
            "📚 本を登録",
            use_container_width=True
        )

        if submit:
            cleaned_title = (
                title.strip()
            )

            duplicate_book = any(
                book.get(
                    "title",
                    ""
                ).strip().lower()
                == cleaned_title.lower()
                and book.get(
                    "author",
                    ""
                ).strip().lower()
                == author.strip().lower()
                for book in books
            )

            if not cleaned_title:
                st.error(
                    "本のタイトルを入力してください。"
                )

            elif duplicate_book:
                st.warning(
                    "同じタイトルと著者の本が登録されています。"
                )

            elif (
                total_pages > 0
                and current_page > total_pages
            ):
                st.error(
                    "現在ページは総ページ数以下にしてください。"
                )

            else:
                if status == "読了":
                    if not finish_date:
                        finish_date = date.today()

                    if total_pages > 0:
                        current_page = (
                            total_pages
                        )

                add_book(
                    data=data,
                    title=cleaned_title,
                    author=author.strip(),
                    publisher=publisher.strip(),
                    genre=genre,
                    book_format=book_format,
                    status=status,
                    priority=priority,
                    purchase_date=purchase_date,
                    start_date=start_date,
                    finish_date=finish_date,
                    current_page=current_page,
                    total_pages=total_pages,
                    rating=rating,
                    summary=summary.strip(),
                    learning=learning.strip(),
                    quote=quote.strip(),
                    next_action=(
                        next_action.strip()
                    ),
                    memo=memo.strip()
                )

                st.success(
                    "本を登録しました！"
                )

                st.rerun()


# =====================================
# 本棚
# =====================================

with list_tab:
    st.header(
        "📚 本棚"
    )

    if not books:
        st.info(
            "本はまだ登録されていません。"
        )

    else:
        filter_col1, filter_col2, filter_col3 = (
            st.columns(3)
        )

        with filter_col1:
            search_keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "タイトル・著者・学び"
                ),
                key="book_search"
            )

        with filter_col2:
            status_filter = st.selectbox(
                "読書状態",
                [
                    "すべて"
                ] + READING_STATUSES,
                key="book_status_filter"
            )

        with filter_col3:
            genre_filter = st.selectbox(
                "ジャンル",
                [
                    "すべて"
                ] + GENRES,
                key="book_genre_filter"
            )

        priority_filter = st.multiselect(
            "優先度",
            PRIORITIES,
            default=PRIORITIES
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "登録が新しい順",
                "優先度順",
                "進捗が高い順",
                "評価が高い順",
                "タイトル順"
            ]
        )

        filtered_books = list(
            books
        )

        if search_keyword:
            keyword = (
                search_keyword.strip().lower()
            )

            filtered_books = [
                book
                for book in filtered_books
                if (
                    keyword
                    in book.get(
                        "title",
                        ""
                    ).lower()
                    or keyword
                    in book.get(
                        "author",
                        ""
                    ).lower()
                    or keyword
                    in book.get(
                        "publisher",
                        ""
                    ).lower()
                    or keyword
                    in book.get(
                        "summary",
                        ""
                    ).lower()
                    or keyword
                    in book.get(
                        "learning",
                        ""
                    ).lower()
                    or keyword
                    in book.get(
                        "quote",
                        ""
                    ).lower()
                )
            ]

        if status_filter != "すべて":
            filtered_books = [
                book
                for book in filtered_books
                if book.get(
                    "status"
                ) == status_filter
            ]

        if genre_filter != "すべて":
            filtered_books = [
                book
                for book in filtered_books
                if book.get(
                    "genre"
                ) == genre_filter
            ]

        filtered_books = [
            book
            for book in filtered_books
            if book.get(
                "priority",
                "中"
            ) in priority_filter
        ]

        if sort_option == "登録が新しい順":
            filtered_books = sorted(
                filtered_books,
                key=lambda book: book.get(
                    "created_at",
                    ""
                ),
                reverse=True
            )

        elif sort_option == "優先度順":
            filtered_books = sorted(
                filtered_books,
                key=lambda book: (
                    PRIORITY_ORDER.get(
                        book.get(
                            "priority",
                            "中"
                        ),
                        99
                    ),
                    book.get(
                        "created_at",
                        ""
                    )
                )
            )

        elif sort_option == "進捗が高い順":
            filtered_books = sorted(
                filtered_books,
                key=lambda book: (
                    calculate_progress(
                        book.get(
                            "current_page",
                            0
                        ),
                        book.get(
                            "total_pages",
                            0
                        )
                    )
                ),
                reverse=True
            )

        elif sort_option == "評価が高い順":
            filtered_books = sorted(
                filtered_books,
                key=lambda book: int(
                    book.get(
                        "rating",
                        0
                    )
                ),
                reverse=True
            )

        else:
            filtered_books = sorted(
                filtered_books,
                key=lambda book: book.get(
                    "title",
                    ""
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_books)}冊**"
        )

        for book in filtered_books:
            book_id = book.get(
                "id",
                ""
            )

            progress = calculate_progress(
                book.get(
                    "current_page",
                    0
                ),
                book.get(
                    "total_pages",
                    0
                )
            )

            with st.container(
                border=True
            ):
                title_col, status_col = (
                    st.columns(
                        [4, 1]
                    )
                )

                with title_col:
                    st.subheader(
                        f"{PRIORITY_ICONS.get(book.get('priority', ''), '')} "
                        f"{book.get('title', '')}"
                    )

                    details = []

                    if book.get(
                        "author",
                        ""
                    ):
                        details.append(
                            f"著者："
                            f"{book.get('author', '')}"
                        )

                    details.append(
                        book.get(
                            "genre",
                            ""
                        )
                    )

                    details.append(
                        book.get(
                            "format",
                            ""
                        )
                    )

                    st.caption(
                        " ／ ".join(
                            details
                        )
                    )

                with status_col:
                    current_status = book.get(
                        "status",
                        "読みたい"
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(current_status, '')} "
                        f"{current_status}"
                    )

                if (
                    book.get(
                        "total_pages",
                        0
                    ) > 0
                ):
                    st.progress(
                        progress / 100
                    )

                    st.caption(
                        f"進捗：{progress:.0f}% "
                        f"（{book.get('current_page', 0)}"
                        f"／{book.get('total_pages', 0)}ページ）"
                    )

                if int(
                    book.get(
                        "rating",
                        0
                    )
                ) > 0:
                    st.write(
                        "⭐ "
                        + "★" * int(
                            book.get(
                                "rating",
                                0
                            )
                        )
                    )

                if book.get(
                    "learning",
                    ""
                ):
                    st.info(
                        f"💡 学び\n\n"
                        f"{book.get('learning', '')}"
                    )

                if book.get(
                    "next_action",
                    ""
                ):
                    st.success(
                        f"➡️ 次に試すこと\n\n"
                        f"{book.get('next_action', '')}"
                    )

                if (
                    book.get(
                        "status"
                    ) != "読了"
                ):
                    if st.button(
                        "✅ 読了にする",
                        key=(
                            f"finish_book_{book_id}"
                        )
                    ):
                        mark_as_finished(
                            data,
                            book_id
                        )

                        st.balloons()
                        st.rerun()

                with st.expander(
                    "✏️ 本の情報を編集"
                ):
                    edit_title = st.text_input(
                        "タイトル",
                        value=book.get(
                            "title",
                            ""
                        ),
                        key=(
                            f"edit_title_{book_id}"
                        )
                    )

                    edit_author = st.text_input(
                        "著者",
                        value=book.get(
                            "author",
                            ""
                        ),
                        key=(
                            f"edit_author_{book_id}"
                        )
                    )

                    edit_publisher = st.text_input(
                        "出版社",
                        value=book.get(
                            "publisher",
                            ""
                        ),
                        key=(
                            f"edit_publisher_{book_id}"
                        )
                    )

                    current_genre = book.get(
                        "genre",
                        "その他"
                    )

                    genre_index = (
                        GENRES.index(
                            current_genre
                        )
                        if current_genre
                        in GENRES
                        else len(
                            GENRES
                        ) - 1
                    )

                    edit_genre = st.selectbox(
                        "ジャンル",
                        GENRES,
                        index=genre_index,
                        key=(
                            f"edit_genre_{book_id}"
                        )
                    )

                    current_format = book.get(
                        "format",
                        "紙"
                    )

                    format_index = (
                        FORMATS.index(
                            current_format
                        )
                        if current_format
                        in FORMATS
                        else 0
                    )

                    edit_format = st.selectbox(
                        "形式",
                        FORMATS,
                        index=format_index,
                        key=(
                            f"edit_format_{book_id}"
                        )
                    )

                    current_status = book.get(
                        "status",
                        "読みたい"
                    )

                    status_index = (
                        READING_STATUSES.index(
                            current_status
                        )
                        if current_status
                        in READING_STATUSES
                        else 0
                    )

                    edit_status = st.selectbox(
                        "状態",
                        READING_STATUSES,
                        index=status_index,
                        key=(
                            f"edit_status_{book_id}"
                        )
                    )

                    current_priority = book.get(
                        "priority",
                        "中"
                    )

                    priority_index = (
                        PRIORITIES.index(
                            current_priority
                        )
                        if current_priority
                        in PRIORITIES
                        else 2
                    )

                    edit_priority = st.selectbox(
                        "優先度",
                        PRIORITIES,
                        index=priority_index,
                        key=(
                            f"edit_priority_{book_id}"
                        )
                    )

                    edit_total_pages = st.number_input(
                        "総ページ数",
                        min_value=0,
                        max_value=10000,
                        value=int(
                            book.get(
                                "total_pages",
                                0
                            )
                        ),
                        key=(
                            f"edit_total_pages_{book_id}"
                        )
                    )

                    edit_current_page = st.number_input(
                        "現在ページ",
                        min_value=0,
                        max_value=10000,
                        value=int(
                            book.get(
                                "current_page",
                                0
                            )
                        ),
                        key=(
                            f"edit_current_page_{book_id}"
                        )
                    )

                    edit_rating = st.slider(
                        "評価",
                        min_value=0,
                        max_value=5,
                        value=int(
                            book.get(
                                "rating",
                                0
                            )
                        ),
                        key=(
                            f"edit_rating_{book_id}"
                        )
                    )

                    purchase_date_value = (
                        parse_date_text(
                            book.get(
                                "purchase_date",
                                ""
                            )
                        )
                    )

                    edit_has_purchase_date = (
                        st.checkbox(
                            "購入日を設定する",
                            value=bool(
                                purchase_date_value
                            ),
                            key=(
                                f"edit_has_purchase_{book_id}"
                            )
                        )
                    )

                    edit_purchase_date = None

                    if edit_has_purchase_date:
                        edit_purchase_date = (
                            st.date_input(
                                "購入日",
                                value=(
                                    purchase_date_value
                                    or date.today()
                                ),
                                max_value=date.today(),
                                key=(
                                    f"edit_purchase_date_{book_id}"
                                )
                            )
                        )

                    start_date_value = (
                        parse_date_text(
                            book.get(
                                "start_date",
                                ""
                            )
                        )
                    )

                    edit_has_start_date = (
                        st.checkbox(
                            "開始日を設定する",
                            value=bool(
                                start_date_value
                            ),
                            key=(
                                f"edit_has_start_{book_id}"
                            )
                        )
                    )

                    edit_start_date = None

                    if edit_has_start_date:
                        edit_start_date = (
                            st.date_input(
                                "読書開始日",
                                value=(
                                    start_date_value
                                    or date.today()
                                ),
                                max_value=date.today(),
                                key=(
                                    f"edit_start_date_{book_id}"
                                )
                            )
                        )

                    finish_date_value = (
                        parse_date_text(
                            book.get(
                                "finish_date",
                                ""
                            )
                        )
                    )

                    edit_has_finish_date = (
                        st.checkbox(
                            "読了日を設定する",
                            value=bool(
                                finish_date_value
                            ),
                            key=(
                                f"edit_has_finish_{book_id}"
                            )
                        )
                    )

                    edit_finish_date = None

                    if edit_has_finish_date:
                        edit_finish_date = (
                            st.date_input(
                                "読了日",
                                value=(
                                    finish_date_value
                                    or date.today()
                                ),
                                max_value=date.today(),
                                key=(
                                    f"edit_finish_date_{book_id}"
                                )
                            )
                        )

                    edit_summary = st.text_area(
                        "概要・感想",
                        value=book.get(
                            "summary",
                            ""
                        ),
                        key=(
                            f"edit_summary_{book_id}"
                        )
                    )

                    edit_learning = st.text_area(
                        "学び",
                        value=book.get(
                            "learning",
                            ""
                        ),
                        key=(
                            f"edit_learning_{book_id}"
                        )
                    )

                    edit_quote = st.text_area(
                        "印象に残った言葉",
                        value=book.get(
                            "quote",
                            ""
                        ),
                        key=(
                            f"edit_quote_{book_id}"
                        )
                    )

                    edit_next_action = st.text_area(
                        "次に試すこと",
                        value=book.get(
                            "next_action",
                            ""
                        ),
                        key=(
                            f"edit_next_action_{book_id}"
                        )
                    )

                    edit_memo = st.text_area(
                        "自由メモ",
                        value=book.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_memo_{book_id}"
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_book_{book_id}"
                        ),
                        use_container_width=True
                    ):
                        if not edit_title.strip():
                            st.error(
                                "タイトルを入力してください。"
                            )

                        elif (
                            edit_total_pages > 0
                            and edit_current_page
                            > edit_total_pages
                        ):
                            st.error(
                                "現在ページは総ページ数以下にしてください。"
                            )

                        else:
                            if edit_status == "読了":
                                if not edit_finish_date:
                                    edit_finish_date = (
                                        date.today()
                                    )

                                if edit_total_pages > 0:
                                    edit_current_page = (
                                        edit_total_pages
                                    )

                            update_book(
                                data=data,
                                book_id=book_id,
                                title=edit_title.strip(),
                                author=edit_author.strip(),
                                publisher=(
                                    edit_publisher.strip()
                                ),
                                genre=edit_genre,
                                book_format=edit_format,
                                status=edit_status,
                                priority=edit_priority,
                                purchase_date=(
                                    edit_purchase_date
                                ),
                                start_date=edit_start_date,
                                finish_date=edit_finish_date,
                                current_page=(
                                    edit_current_page
                                ),
                                total_pages=(
                                    edit_total_pages
                                ),
                                rating=edit_rating,
                                summary=(
                                    edit_summary.strip()
                                ),
                                learning=(
                                    edit_learning.strip()
                                ),
                                quote=edit_quote.strip(),
                                next_action=(
                                    edit_next_action.strip()
                                ),
                                memo=edit_memo.strip()
                            )

                            st.success(
                                "本の情報を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 本を削除"
                ):
                    st.warning(
                        "削除すると読書ログも消えます。"
                    )

                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_{book_id}"
                        )
                    )

                    if st.button(
                        "この本を削除",
                        key=(
                            f"delete_book_{book_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_book(
                            data,
                            book_id
                        )

                        st.rerun()


# =====================================
# 読書ログ
# =====================================

with log_tab:
    st.header(
        "📝 読書ログ"
    )

    if not books:
        st.info(
            "本を登録すると読書ログを追加できます。"
        )

    else:
        book_options = {
            get_display_title(
                book
            ): book.get(
                "id"
            )
            for book in books
        }

        selected_book_name = st.selectbox(
            "本を選択",
            list(
                book_options.keys()
            ),
            key="log_book_select"
        )

        selected_book = get_book_by_id(
            data,
            book_options[
                selected_book_name
            ]
        )

        if selected_book:
            book_id = selected_book.get(
                "id",
                ""
            )

            st.subheader(
                selected_book.get(
                    "title",
                    ""
                )
            )

            current_progress = (
                calculate_progress(
                    selected_book.get(
                        "current_page",
                        0
                    ),
                    selected_book.get(
                        "total_pages",
                        0
                    )
                )
            )

            if selected_book.get(
                "total_pages",
                0
            ) > 0:
                st.progress(
                    current_progress / 100
                )

                st.caption(
                    f"現在："
                    f"{selected_book.get('current_page', 0)}ページ "
                    f"／ "
                    f"{selected_book.get('total_pages', 0)}ページ"
                )

            with st.form(
                f"add_log_form_{book_id}",
                clear_on_submit=True
            ):
                log_col1, log_col2 = (
                    st.columns(2)
                )

                with log_col1:
                    log_date = st.date_input(
                        "読書日",
                        value=date.today(),
                        max_value=date.today()
                    )

                with log_col2:
                    log_page = st.number_input(
                        "読んだところまでのページ",
                        min_value=0,
                        max_value=10000,
                        value=int(
                            selected_book.get(
                                "current_page",
                                0
                            )
                        )
                    )

                log_content = st.text_area(
                    "読書メモ",
                    placeholder=(
                        "読んだ範囲、気づき、"
                        "印象に残ったこと"
                    ),
                    height=140
                )

                log_submit = st.form_submit_button(
                    "📝 読書ログを追加",
                    use_container_width=True
                )

                if log_submit:
                    total_pages = int(
                        selected_book.get(
                            "total_pages",
                            0
                        )
                    )

                    if not log_content.strip():
                        st.error(
                            "読書メモを入力してください。"
                        )

                    elif (
                        total_pages > 0
                        and log_page > total_pages
                    ):
                        st.error(
                            "ページ数が総ページ数を超えています。"
                        )

                    else:
                        add_reading_log(
                            data=data,
                            book_id=book_id,
                            log_date=log_date,
                            page=log_page,
                            content=(
                                log_content.strip()
                            )
                        )

                        st.success(
                            "読書ログを追加しました！"
                        )

                        st.rerun()

            st.divider()

            st.subheader(
                "📚 過去の読書ログ"
            )

            logs = sorted(
                selected_book.get(
                    "logs",
                    []
                ),
                key=lambda log: (
                    log.get(
                        "log_date",
                        ""
                    ),
                    log.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

            if not logs:
                st.info(
                    "読書ログはまだありません。"
                )

            for log in logs:
                log_id = log.get(
                    "id",
                    ""
                )

                with st.container(
                    border=True
                ):
                    log_col1, log_col2 = (
                        st.columns(
                            [4, 1]
                        )
                    )

                    with log_col1:
                        st.subheader(
                            format_date(
                                log.get(
                                    "log_date",
                                    ""
                                )
                            )
                        )

                    with log_col2:
                        st.metric(
                            "ページ",
                            f"{log.get('page', 0)}"
                        )

                    st.write(
                        log.get(
                            "content",
                            ""
                        )
                    )

                    with st.expander(
                        "ログを削除"
                    ):
                        confirm_log_delete = (
                            st.checkbox(
                                "削除を確認しました",
                                key=(
                                    f"confirm_log_delete_{log_id}"
                                )
                            )
                        )

                        if st.button(
                            "このログを削除",
                            key=(
                                f"delete_log_{log_id}"
                            ),
                            disabled=(
                                not confirm_log_delete
                            )
                        ):
                            delete_reading_log(
                                data,
                                book_id,
                                log_id
                            )

                            st.rerun()


# =====================================
# 読了記録
# =====================================

with completed_tab:
    st.header(
        "✅ 読了記録"
    )

    completed_books = [
        book
        for book in books
        if book.get(
            "status"
        ) == "読了"
    ]

    if not completed_books:
        st.info(
            "読了した本はまだありません。"
        )

    else:
        completed_books = sorted(
            completed_books,
            key=lambda book: book.get(
                "finish_date",
                ""
            ),
            reverse=True
        )

        for book in completed_books:
            with st.container(
                border=True
            ):
                title_col, rating_col = (
                    st.columns(
                        [4, 1]
                    )
                )

                with title_col:
                    st.subheader(
                        book.get(
                            "title",
                            ""
                        )
                    )

                    if book.get(
                        "author",
                        ""
                    ):
                        st.caption(
                            f"著者："
                            f"{book.get('author', '')}"
                        )

                    st.caption(
                        f"読了日："
                        f"{format_date(book.get('finish_date', ''))}"
                    )

                with rating_col:
                    rating = int(
                        book.get(
                            "rating",
                            0
                        )
                    )

                    st.metric(
                        "評価",
                        (
                            f"{rating} / 5"
                            if rating > 0
                            else "未評価"
                        )
                    )

                if book.get(
                    "summary",
                    ""
                ):
                    st.write(
                        f"📝 **感想・概要**\n\n"
                        f"{book.get('summary', '')}"
                    )

                if book.get(
                    "learning",
                    ""
                ):
                    st.info(
                        f"💡 学び\n\n"
                        f"{book.get('learning', '')}"
                    )

                if book.get(
                    "quote",
                    ""
                ):
                    st.warning(
                        f"💬 印象に残った言葉\n\n"
                        f"{book.get('quote', '')}"
                    )

                if book.get(
                    "next_action",
                    ""
                ):
                    st.success(
                        f"➡️ 次に試すこと\n\n"
                        f"{book.get('next_action', '')}"
                    )


# =====================================
# 読書分析
# =====================================

with analysis_tab:
    st.header(
        "📈 読書分析"
    )

    if not books:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        book_rows = []

        for book in books:
            book_rows.append(
                {
                    "タイトル": book.get(
                        "title",
                        ""
                    ),
                    "ジャンル": book.get(
                        "genre",
                        ""
                    ),
                    "状態": book.get(
                        "status",
                        ""
                    ),
                    "形式": book.get(
                        "format",
                        ""
                    ),
                    "評価": int(
                        book.get(
                            "rating",
                            0
                        )
                    ),
                    "進捗率": round(
                        calculate_progress(
                            book.get(
                                "current_page",
                                0
                            ),
                            book.get(
                                "total_pages",
                                0
                            )
                        ),
                        1
                    ),
                    "読了日": book.get(
                        "finish_date",
                        ""
                    )
                }
            )

        book_df = pd.DataFrame(
            book_rows
        )

        st.subheader(
            "📚 読書状態別"
        )

        status_summary = (
            book_df.groupby(
                "状態",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "冊数"
                }
            )
            .sort_values(
                "冊数",
                ascending=False
            )
        )

        st.bar_chart(
            status_summary.set_index(
                "状態"
            )[["冊数"]]
        )

        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "📂 ジャンル別冊数"
        )

        genre_summary = (
            book_df.groupby(
                "ジャンル",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "冊数"
                }
            )
            .sort_values(
                "冊数",
                ascending=False
            )
        )

        st.bar_chart(
            genre_summary.set_index(
                "ジャンル"
            )[["冊数"]]
        )

        st.dataframe(
            genre_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "📱 書籍形式別冊数"
        )

        format_summary = (
            book_df.groupby(
                "形式",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "冊数"
                }
            )
            .sort_values(
                "冊数",
                ascending=False
            )
        )

        st.bar_chart(
            format_summary.set_index(
                "形式"
            )[["冊数"]]
        )

        st.dataframe(
            format_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🗓️ 月別読了数"
        )

        finished_rows = []

        for book in books:
            finish_date = parse_date_text(
                book.get(
                    "finish_date",
                    ""
                )
            )

            if finish_date:
                finished_rows.append(
                    {
                        "月": finish_date.strftime(
                            "%Y-%m"
                        ),
                        "冊数": 1
                    }
                )

        if finished_rows:
            finished_df = pd.DataFrame(
                finished_rows
            )

            monthly_summary = (
                finished_df.groupby(
                    "月",
                    as_index=False
                )["冊数"]
                .sum()
                .sort_values(
                    "月"
                )
            )

            st.bar_chart(
                monthly_summary.set_index(
                    "月"
                )[["冊数"]]
            )

            st.dataframe(
                monthly_summary,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "読了日の記録がありません。"
            )

        st.divider()

        st.subheader(
            "⭐ 高評価の本"
        )

        rated_books = [
            book
            for book in books
            if int(
                book.get(
                    "rating",
                    0
                )
            ) > 0
        ]

        rated_books = sorted(
            rated_books,
            key=lambda book: int(
                book.get(
                    "rating",
                    0
                )
            ),
            reverse=True
        )

        if not rated_books:
            st.info(
                "評価された本がありません。"
            )

        else:
            for book in rated_books[:10]:
                st.write(
                    f"**{book.get('title', '')}** "
                    f"― "
                    f"{'★' * int(book.get('rating', 0))}"
                )


st.divider()

st.success(
    "読書は、読んだ冊数だけでなく、"
    "何を学び、何を行動に変えたかで価値が深まります。📚"
)
