# === Builder ===
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN pip install poetry-plugin-export && \
    poetry export -f requirements.txt --output requirements.txt

# === Runner ===
FROM python:3.13-slim AS runner
WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src

# === Command ===
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]