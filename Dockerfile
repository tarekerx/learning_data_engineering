# --- Stage 1: The Builder (heavy, installs and compiles everything) ---
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY reqs.txt .
RUN pip install --no-cache-dir --prefix=/install -r reqs.txt

# --- Stage 2: The Final Runtime (clean, lightweight) ---
FROM python:3.12-slim
WORKDIR /app
# Copy only the compiled packages from the builder stage!
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "src/main.py"]