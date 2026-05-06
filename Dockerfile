FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir uv

COPY pyproject.toml .
# COPY uv.lock .  # if you have one

RUN uv venv

COPY . .

RUN uv pip install .

ENV PATH="/app/.venv/bin:${PATH}"
ENV APP_ROOT="/"
EXPOSE 8000

CMD ["sh", "-c", "fastapi run src/htcondor_dashboard/fastapi_app.py --host 0.0.0.0 --port 8000 --root-path ${APP_ROOT}"]