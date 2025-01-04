# Dockerイメージを指定。
FROM python:3.11.0-slim

# パッケージのアップデートとcurlをインストール
RUN apt-get update && apt-get -y install curl

# Poetryの実行パスを設定
ENV PATH /root/.local/bin:$PATH

# Poetryをインストール
RUN curl -sSL https://install.python-poetry.org | python3 -

# 作業ディレクトリを設定
WORKDIR /app

# Poetryの設定ファイルとソースコードをコピー
COPY pyproject.toml poetry.lock ./
COPY testagent/main.py ./

# Poetryの仮想環境を無効化
RUN poetry config virtualenvs.create false

# 依存関係をインストール
RUN poetry install --no-interaction --only main

# コンテナ起動時に実行するコマンド
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]