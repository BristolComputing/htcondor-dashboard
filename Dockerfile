# app/Dockerfile

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY . .

RUN python -m pip install -e .

EXPOSE 8501

# HEALTHCHECK CMD curl --fail http://localhost:800/health

ENTRYPOINT ["./scripts/run.sh"]
