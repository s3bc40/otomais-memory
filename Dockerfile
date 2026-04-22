FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uv run python manage.py collectstatic --noinput && uv run gunicorn otomais.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
