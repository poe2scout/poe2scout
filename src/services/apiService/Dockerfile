FROM python:3.12.3-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install uv
RUN uv pip install --system --no-cache-dir -r requirements.txt


COPY services services

COPY services/apiService/entrypoint.sh /entrypoint.sh
# Run the application with factory flag
CMD ["python", "-m", "services.apiService.app"]