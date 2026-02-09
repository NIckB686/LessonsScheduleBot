FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-cache

FROM python:3.14.2-slim-bookworm AS final

WORKDIR /app

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=nonroot:nonroot main.py .
COPY --chown=nonroot:nonroot config.py .
COPY --chown=nonroot:nonroot entrypoint.sh .
COPY --chown=nonroot:nonroot alembic.ini .
COPY --chown=nonroot:nonroot alembic ./alembic
COPY --chown=nonroot:nonroot app ./app

RUN chmod +x entrypoint.sh

USER nonroot

CMD ["./entrypoint.sh"]
