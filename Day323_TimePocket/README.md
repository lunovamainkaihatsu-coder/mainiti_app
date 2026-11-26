# Day323 もしも、時間があったなら
Python 3.10以上推奨。展開したフォルダで `python -m pip install -r requirements.txt`、続いて `python -m streamlit run app.py` を実行。
全8タブ。データは data/activities.json に保存。外部API不要。単一ユーザー向け。タイマーは開始時刻を保存し、更新ボタンで経過時間を再計算します。自動通知・秒単位の自動更新はありません。活動削除は関連履歴も削除します。復元前にバックアップしてください。完了済み活動は管理画面から再開できます。
