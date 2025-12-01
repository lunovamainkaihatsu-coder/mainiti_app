import os
import subprocess
import sys

def main():
    # exe化したときと通常実行の両方に対応して app.py の場所を決定
    if getattr(sys, "frozen", False):
        # game_idea_maker.exe がある dist フォルダ -> その1つ上が本当のプロジェクトフォルダ
        dist_dir = os.path.dirname(sys.executable)
        base_dir = os.path.abspath(os.path.join(dist_dir, ".."))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(base_dir, "app.py")

    print("Streamlit アプリを起動します…")
    print(f"使用中の app.py パス: {app_path}")
    print("もしブラウザが開かない場合は、このウィンドウのメッセージを確認してください。")
    print()

    try:
        completed = subprocess.run(
            ["streamlit", "run", app_path],
            check=False
        )
        print()
        print(f"Streamlit 終了コード: {completed.returncode}")
    except Exception as e:
        print("エラーが発生しました:", e)

    input("\nEnterキーを押すとこのウィンドウを閉じます。")

if __name__ == "__main__":
    main()
