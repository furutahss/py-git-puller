import os
import sys
import subprocess
import argparse
from pathlib import Path

# 指定リポジトリで指定のGitコマンドを実施
# @returns  subprocess.CompletedProcess オブジェクト
def run_git_command(repo_path, command):
    try:
        # 失敗しても無視するため check=False に設定
        result = subprocess.run(
            ["git"] + command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except Exception as e:
        return f"実行エラー: {e}"

# メイン処理
# @returns  None
def main():
    parser = argparse.ArgumentParser(description="指定フォルダ内の全Gitリポジトリを一括でFetch & Pullします。")
    parser.add_argument("dir", help="Gitリポジトリが並んでいる親ディレクトリのパス")
    args = parser.parse_args()

    root_dir = Path(args.dir).expanduser().resolve()
    if not root_dir.is_dir():
        print(f"エラー: {root_dir} は有効なディレクトリではありません。")
        sys.exit(1)

    # 直下のディレクトリを取得
    subdirs = [p for p in root_dir.iterdir() if p.is_dir()]
    
    if not subdirs:
        print("フォルダが見つかりませんでした。")
        return

    print(f"🚀 {root_dir} 内のリポジトリを更新中...\n")

    for repo_path in subdirs:
        # .git フォルダがあるかチェック
        if not (repo_path / ".git").exists():
            continue

        print(f"📦 Checking: {repo_path.name}")
        
        # 1. Fetch
        print(f"  -> fetching...")
        run_git_command(repo_path, ["fetch", "--all"])
        
        # 2. Pull
        print(f"  -> pulling...")
        pull_result = run_git_command(repo_path, ["pull"])
        
        if pull_result.returncode == 0:
            if "Already up to date" in pull_result.stdout:
                print("  ✅ すでに最新の状態です。")
            else:
                print("  ✅ 更新が完了しました。")
        else:
            # 失敗しても無視して次へ行くが、通知だけはする
            print(f"  ⚠️ Pullに失敗しました（競合または未コミットの変更がある可能性があります）。")
        print("-" * 30)

    print("\n✨ すべての処理が終了しました。")

if __name__ == "__main__":
    main()