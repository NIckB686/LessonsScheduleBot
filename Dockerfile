FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -Lss https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv export --format requirements-txt --no-dev > requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]