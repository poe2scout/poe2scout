FROM python:3.12.3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install uv
RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY services services

CMD ["python", "-m", "services.currencyExchangeService"]