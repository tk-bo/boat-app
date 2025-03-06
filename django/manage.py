#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # 'backend' に変更
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django をインポートできませんでした。環境が正しく設定されているか確認してください。"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
