FROM python:3.14.3-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY packages/backend /app

RUN pip install uv
RUN uv pip install --system --no-cache-dir /app

CMD ["python", "-m", "poe2scout.workers.currency_price_log"]
