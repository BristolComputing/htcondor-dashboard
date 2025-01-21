# app/Dockerfile

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install uv

COPY ./pyproject.toml .
RUN uv venv \
    && uv pip compile pyproject.toml > requirements.txt \
    && uv pip install -r requirements.txt

COPY . .

RUN uv pip install -e .

EXPOSE 8501

ENV APP_ROOT="/"
ENV PATH="/app/.venv/bin:${PATH}"

# workaround for Docker CMD not expanding environment variables
RUN echo "#!/bin/bash\nfastapi run src/htcondor_dashboard/fastapi_app.py --port 8000 --root-path \${APP_ROOT}" > /app/entrypoint.sh \
    && chmod a+x /app/entrypoint.sh

CMD ["sh", "-c", "/app/entrypoint.sh"]
