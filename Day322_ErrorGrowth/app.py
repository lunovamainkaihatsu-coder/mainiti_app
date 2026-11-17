import json
import random
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title='エラーは成長の証', page_icon='🐛', layout='wide')
DATA_FILE = Path(__file__).parent / 'data' / 'errors.json'
LANGS = ['Python', 'Java', 'SQL', 'JavaScript', 'TypeScript', 'その他']
KINDS = ['構文エラー', '型・値のエラー', '名前・参照のエラー', '範囲・キーのエラー', '入出力・ファイル', 'その他・ロジック']
STATUSES = ['未解決', '調査中', '解決済み']
DEFAULT = {'errors': [], 'steps': [], 'reviews': []}


def load():
    if not DATA_FILE.exists():
        return {k: [] for k in DEFAULT}
    try:
        obj = json.loads(DATA_FILE.read_text(encoding='utf-8'))
        return validate(obj)
    except (OSError, ValueError, TypeError) as exc:
        st.error(f'保存データを読み込めませんでした。バックアップを確認してください: {exc}')
        st.stop()


def validate(obj):
    if not isinstance(obj, dict) or any(not isinstance(obj.get(k), list) for k in DEFAULT):
        raise ValueError('errors / steps / reviews は配列である必要があります。')
    for key in DEFAULT:
        if any(not isinstance(row, dict) or not isinstance(row.get('id'), str) for row in obj[key]):
            raise ValueError(f'{key} の各レコードには文字列の id が必要です。')
    return {k: obj[k] for k in DEFAULT}


def save():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(st.session_state.db, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(DATA_FILE)


def add(kind, row):
    row['id'] = str(uuid.uuid4())
    st.session_state.db[kind].append(row)
    save()


def rerun_success(message):
    st.session_state.notice = message
    st.rerun()


def lookup(error_id):
    return next((x for x in db['errors'] if x['id'] == error_id), None)


def label_for(row):
    return f"{row.get('name', '名称なし')} | {row.get('language', '')} | {row['id'][:6]}"


def error_picker(key, solved_only=False):
    items = [x for x in db['errors'] if not solved_only or x.get('status') == '解決済み']
    if not items:
        st.info('対象となるエラー記録がありません。先にエラーを登録してください。')
        return None
    chosen = st.selectbox('対象エラー', items, format_func=label_for, key=key)
    return chosen


if 'db' not in st.session_state:
    st.session_state.db = load()
db = st.session_state.db
st.title('🐛📚 エラーは成長の証')
st.caption('昨日のエラーが、明日の自分を助けてくれる。データはこのPCのJSONに保存されます。')
if st.session_state.get('notice'):
    st.success(st.session_state.pop('notice'))

tabs = st.tabs(['🏠 ホーム', '🐛 エラー登録', '🗂️ エラー分類', '📖 解決辞典', '🔧 解決プロセス', '🧠 復習クイズ', '📊 成長分析', '🛠️ 管理'])

with tabs[0]:
    errors = db['errors']
    solved = [e for e in errors if e.get('status') == '解決済み']
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('登録エラー', len(errors))
    c2.metric('解決済み', len(solved))
    c3.metric('解決率', f'{len(solved)/len(errors)*100:.0f}%' if errors else '—')
    c4.metric('復習回数', len(db['reviews']))
    st.subheader('最近のエラー')
    for e in sorted(errors, key=lambda x: x.get('created_at', ''), reverse=True)[:8]:
        st.write(f"**{e.get('name','')}**　{e.get('language','')}　|　{e.get('status','')}　|　{e.get('date','')}")
    if not errors:
        st.info('「🐛 エラー登録」から最初のエラーを記録しよう！')

with tabs[1]:
    st.subheader('エラーを記録する')
    with st.form('new_error', clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        occurred = c1.date_input('発生日', date.today())
        language = c2.selectbox('言語', LANGS)
        kind = c3.selectbox('分類', KINDS)
        name = st.text_input('エラー名 *', placeholder='例: ValueError')
        message = st.text_area('エラーメッセージ')
        code = st.text_area('発生コード')
        cause = st.text_area('原因')
        fixed_code = st.text_area('修正コード')
        solution = st.text_area('解決方法')
        learned = st.text_area('学んだこと（復習クイズの答えにも使います）')
        c4, c5, c6 = st.columns(3)
        difficulty = c4.slider('難易度', 1, 5, 3)
        status = c5.selectbox('解決状況', STATUSES)
        minutes = c6.number_input('解決までの時間（分）', min_value=0, step=5)
        independent = st.checkbox('自力で解決できた')
        favorite = st.checkbox('お気に入り')
        submitted = st.form_submit_button('💾 登録', type='primary')
        if submitted:
            if not name.strip():
                st.warning('エラー名を入力してね。')
            else:
                add('errors', {'date': occurred.isoformat(), 'created_at': datetime.now().isoformat(timespec='seconds'), 'language': language, 'kind': kind, 'name': name.strip(), 'message': message, 'code': code, 'cause': cause, 'fixed_code': fixed_code, 'solution': solution, 'learned': learned, 'difficulty': difficulty, 'status': status, 'minutes': int(minutes), 'independent': independent, 'favorite': favorite})
                rerun_success('エラーを登録したよ！')

with tabs[2]:
    st.subheader('分類から探す')
    if db['errors']:
        frame = pd.DataFrame(db['errors'])
        a, b = st.columns(2)
        with a:
            st.write('言語別')
            st.bar_chart(frame['language'].value_counts())
        with b:
            st.write('分類別')
            st.bar_chart(frame['kind'].value_counts())
        kind_filter = st.selectbox('分類を絞り込む', ['すべて'] + KINDS)
        filtered = db['errors'] if kind_filter == 'すべて' else [e for e in db['errors'] if e.get('kind') == kind_filter]
        for e in filtered:
            st.write(f"**{e.get('name','')}** — {e.get('language','')} / {e.get('status','')}")
    else:
        st.info('記録が増えると分類別に表示されるよ。')

with tabs[3]:
    st.subheader('自分専用のエラー解決辞典')
    search = st.text_input('キーワード検索', placeholder='エラー名・メッセージ・原因・解決方法')
    c1, c2, c3 = st.columns(3)
    lang_filter = c1.selectbox('言語', ['すべて'] + LANGS)
    status_filter = c2.selectbox('状況', ['すべて'] + STATUSES)
    only_favorites = c3.checkbox('お気に入りのみ')
    filtered = []
    for e in db['errors']:
        blob = ' '.join(str(e.get(k, '')) for k in ['name', 'message', 'cause', 'solution', 'learned', 'code', 'fixed_code']).lower()
        if search.lower() not in blob or (lang_filter != 'すべて' and e.get('language') != lang_filter) or (status_filter != 'すべて' and e.get('status') != status_filter) or (only_favorites and not e.get('favorite')):
            continue
        filtered.append(e)
    st.caption(f'{len(filtered)} 件')
    for e in sorted(filtered, key=lambda x: x.get('date', ''), reverse=True):
        with st.expander(f"{'⭐ ' if e.get('favorite') else ''}{e.get('name','')} | {e.get('language','')} | {e.get('status','')}"):
            st.write('**発生日:**', e.get('date', ''))
            st.write('**メッセージ:**', e.get('message', ''))
            if e.get('code'): st.code(e['code'])
            st.write('**原因:**', e.get('cause', ''))
            if e.get('fixed_code'): st.code(e['fixed_code'])
            st.write('**解決方法:**', e.get('solution', ''))
            st.write('**学び:**', e.get('learned', ''))
            st.write(f"難易度 {e.get('difficulty','?')}/5　解決時間 {e.get('minutes',0)}分")

with tabs[4]:
    st.subheader('試行錯誤を記録する')
    chosen = error_picker('step_target')
    if chosen:
        with st.form('new_step', clear_on_submit=True):
            day = st.date_input('実施日', date.today())
            action = st.text_area('試したこと *')
            result = st.text_area('結果・気づき')
            minutes = st.number_input('所要時間（分）', min_value=0, step=5)
            if st.form_submit_button('手順を保存'):
                if action.strip():
                    add('steps', {'error_id': chosen['id'], 'date': day.isoformat(), 'action': action, 'result': result, 'minutes': int(minutes)})
                    rerun_success('解決プロセスを記録したよ！')
                else:
                    st.warning('試したことを入力してね。')
        st.subheader('これまでの試行')
        steps = [s for s in db['steps'] if s.get('error_id') == chosen['id']]
        for i, s in enumerate(sorted(steps, key=lambda x: x.get('date', '')), 1):
            st.markdown(f"**{i}. {s.get('date','')}（{s.get('minutes',0)}分）**")
            st.write(s.get('action', ''))
            st.caption(s.get('result', ''))
        if not steps:
            st.info('まだ試行記録がないよ。')

with tabs[5]:
    st.subheader('過去のエラーを思い出そう')
    quiz_pool = [e for e in db['errors'] if e.get('status') == '解決済み' and (e.get('cause') or e.get('learned'))]
    if not quiz_pool:
        st.info('原因か学びを記入した「解決済み」のエラーを登録するとクイズに使えるよ。')
    else:
        if st.button('🎲 別の問題を出す') or st.session_state.get('quiz_id') not in [e['id'] for e in quiz_pool]:
            st.session_state.quiz_id = random.choice(quiz_pool)['id']
            st.session_state.quiz_reveal = False
        quiz = next(e for e in quiz_pool if e['id'] == st.session_state.quiz_id)
        st.write(f"**問題:** {quiz.get('name','')}（{quiz.get('language','')}）の原因と解決方法を説明できる？")
        if quiz.get('message'): st.code(quiz['message'])
        if quiz.get('code'): st.code(quiz['code'])
        user_answer = st.text_area('自分の言葉で答えてみよう', key=f"answer_{quiz['id']}")
        if st.button('答えを見る'):
            st.session_state.quiz_reveal = True
        if st.session_state.get('quiz_reveal'):
            st.write('**記録した原因:**', quiz.get('cause', ''))
            st.write('**記録した解決方法:**', quiz.get('solution', ''))
            st.write('**記録した学び:**', quiz.get('learned', ''))
            with st.form(f"quiz_review_{quiz['id']}"):
                rating = st.slider('理解度を自己評価', 1, 5, 3)
                memo = st.text_input('復習メモ')
                if st.form_submit_button('復習履歴を保存'):
                    add('reviews', {'error_id': quiz['id'], 'date': datetime.now().isoformat(timespec='seconds'), 'answer': user_answer, 'rating': rating, 'memo': memo})
                    st.session_state.quiz_reveal = False
                    rerun_success('復習履歴を保存したよ！')

with tabs[6]:
    st.subheader('成長分析')
    errors = db['errors']
    if errors:
        frame = pd.DataFrame(errors)
        c1, c2, c3 = st.columns(3)
        solved_frame = frame[frame['status'] == '解決済み']
        c1.metric('平均解決時間', f"{solved_frame['minutes'].mean():.1f} 分" if not solved_frame.empty else '—')
        c2.metric('自力解決率（解決済み）', f"{solved_frame['independent'].mean()*100:.0f}%" if not solved_frame.empty else '—')
        c3.metric('復習回数', len(db['reviews']))
        st.write('言語別のエラー件数')
        st.bar_chart(frame['language'].value_counts())
        if not solved_frame.empty:
            st.write('解決時間の推移（解決済み・登録日順）')
            times = solved_frame.sort_values(['date', 'created_at'])[['date', 'minutes']].reset_index(drop=True)
            times.index = times.index + 1
            st.line_chart(times['minutes'])
        if db['reviews']:
            reviews_frame = pd.DataFrame(db['reviews']).sort_values('date')
            st.write('復習の自己評価推移')
            st.line_chart(reviews_frame['rating'].reset_index(drop=True))
        st.caption('解決時間はエラーの難易度でも変わるため、単純な短縮だけで実力を判断しないでね。')
    else:
        st.info('記録を追加するとグラフが表示されるよ。')

with tabs[7]:
    st.subheader('エラー記録の編集')
    chosen = error_picker('manage_target')
    if chosen:
        with st.form(f"edit_{chosen['id']}"):
            name = st.text_input('エラー名', value=chosen.get('name', ''))
            language = st.selectbox('言語', LANGS, index=LANGS.index(chosen.get('language', LANGS[0])) if chosen.get('language') in LANGS else 0)
            kind = st.selectbox('分類', KINDS, index=KINDS.index(chosen.get('kind', KINDS[0])) if chosen.get('kind') in KINDS else 0)
            status = st.selectbox('状況', STATUSES, index=STATUSES.index(chosen.get('status', STATUSES[0])) if chosen.get('status') in STATUSES else 0)
            message = st.text_area('エラーメッセージ', value=chosen.get('message', ''))
            code = st.text_area('発生コード', value=chosen.get('code', ''))
            cause = st.text_area('原因', value=chosen.get('cause', ''))
            fixed_code = st.text_area('修正コード', value=chosen.get('fixed_code', ''))
            solution = st.text_area('解決方法', value=chosen.get('solution', ''))
            learned = st.text_area('学び', value=chosen.get('learned', ''))
            difficulty = st.slider('難易度', 1, 5, int(chosen.get('difficulty', 3)))
            minutes = st.number_input('解決時間（分）', min_value=0, value=int(chosen.get('minutes', 0)))
            independent = st.checkbox('自力解決', value=bool(chosen.get('independent', False)))
            favorite = st.checkbox('お気に入り', value=bool(chosen.get('favorite', False)))
            if st.form_submit_button('変更を保存'):
                if not name.strip():
                    st.warning('エラー名は必須だよ。')
                else:
                    chosen.update(name=name.strip(), language=language, kind=kind, status=status, message=message, code=code, cause=cause, fixed_code=fixed_code, solution=solution, learned=learned, difficulty=difficulty, minutes=int(minutes), independent=independent, favorite=favorite)
                    save()
                    rerun_success('変更を保存したよ！')
        with st.expander('⚠️ エラー記録を削除'):
            st.warning('関連する解決プロセス・復習履歴も削除されるよ。')
            confirm = st.checkbox('削除することを確認しました', key=f"confirm_{chosen['id']}")
            if st.button('このエラーを削除', disabled=not confirm):
                eid = chosen['id']
                for key in ['errors', 'steps', 'reviews']:
                    db[key] = [x for x in db[key] if (x['id'] != eid if key == 'errors' else x.get('error_id') != eid)]
                save()
                rerun_success('削除したよ。')
    st.divider()
    st.subheader('解決プロセス・復習履歴の編集と削除')
    record_type = st.selectbox('記録の種類', ['steps', 'reviews'], format_func=lambda x: '解決プロセス' if x == 'steps' else '復習履歴')
    if db[record_type]:
        record = st.selectbox('対象記録', db[record_type], format_func=lambda x: f"{lookup(x.get('error_id', '')) and lookup(x['error_id']).get('name', '') or '不明'} | {x.get('date','')} | {x['id'][:6]}", key='child_record')
        with st.form(f"edit_child_{record['id']}"):
            if record_type == 'steps':
                action = st.text_area('試したこと', value=record.get('action', ''))
                result = st.text_area('結果', value=record.get('result', ''))
                minutes = st.number_input('所要時間（分）', min_value=0, value=int(record.get('minutes', 0)))
            else:
                answer = st.text_area('自分の回答', value=record.get('answer', ''))
                rating = st.slider('理解度', 1, 5, int(record.get('rating', 3)))
                memo = st.text_area('メモ', value=record.get('memo', ''))
            if st.form_submit_button('この記録を更新'):
                if record_type == 'steps':
                    record.update(action=action, result=result, minutes=int(minutes))
                else:
                    record.update(answer=answer, rating=rating, memo=memo)
                save()
                rerun_success('記録を更新したよ！')
        confirm_child = st.checkbox('この記録の削除を確認', key=f"child_confirm_{record['id']}")
        if st.button('選択した記録を削除', disabled=not confirm_child):
            db[record_type] = [x for x in db[record_type] if x['id'] != record['id']]
            save()
            rerun_success('記録を削除したよ。')
    else:
        st.info('対象の記録がまだないよ。')
    st.divider()
    st.subheader('バックアップと復元')
    st.download_button('📥 JSONバックアップをダウンロード', data=json.dumps(db, ensure_ascii=False, indent=2), file_name=f"error_growth_backup_{date.today().isoformat()}.json", mime='application/json')
    upload = st.file_uploader('バックアップJSONを選択', type=['json'])
    if upload:
        try:
            restored = validate(json.loads(upload.getvalue().decode('utf-8')))
            st.info(f"エラー {len(restored['errors'])}件、手順 {len(restored['steps'])}件、復習 {len(restored['reviews'])}件を読み込みます。現在のデータは上書きされます。")
            confirm_restore = st.checkbox('現在のデータを上書きすることに同意します')
            if st.button('📤 復元を実行', disabled=not confirm_restore):
                st.session_state.db = restored
                save()
                rerun_success('バックアップを復元したよ！')
        except (ValueError, UnicodeError, TypeError) as exc:
            st.error(f'バックアップの形式が正しくありません: {exc}')
