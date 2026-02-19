FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_NO_BUILD=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

FROM python:3.14.3-slim-trixie AS final

WORKDIR /app

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --chown=nonroot:nonroot --chmod=755 entrypoint.sh .
COPY --chown=nonroot:nonroot main.py config.py alembic.ini ./
COPY --chown=nonroot:nonroot alembic ./alembic
COPY --chown=nonroot:nonroot app ./app

USER nonroot

CMD ["./entrypoint.sh"]
