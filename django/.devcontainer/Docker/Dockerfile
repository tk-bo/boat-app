FROM python:3.9

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libopenblas-dev \
    liblapack-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*


ENV PYTHONUNBUFFERED=1

# 作業ディレクトリを設定
WORKDIR /django/

# `requirements.txt` をコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# Django プロジェクトをコピー
COPY ./ .

EXPOSE 8000

CMD [ "sleep", "infinity" ]
