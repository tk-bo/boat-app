FROM python:3.12

# 必要なパッケージをインストール（--no-install-recommends を追加）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libopenblas-dev \
    liblapack-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 環境変数
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

# 作業ディレクトリ
WORKDIR /app/

# Python仮想環境を作成
RUN python -m venv /venv

# `requirements.txt` をコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Django プロジェクトをコピー
COPY ./ . 

# ポート 8000 を公開
EXPOSE 8000

# コンテナ起動時のデフォルトコマンド
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
