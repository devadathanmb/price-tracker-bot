# Build stage
FROM python:3.12-slim as builder

WORKDIR /app
COPY requirements.txt .

# Install build dependencies and Python packages
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  libpq-dev \
  gcc \
  wget \
  && pip install --no-cache-dir -r requirements.txt

# Install Playwright in build stage
RUN playwright install --with-deps chromium && \
  mkdir -p /ms-playwright && \
  cp -r /root/.cache/ms-playwright/* /ms-playwright/

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install only runtime dependencies including the missing ones
RUN apt-get update && apt-get install -y --no-install-recommends \
  libpq5 \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libdbus-1-3 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libasound2 \
  libcups2 \
  libxkbcommon0 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libcairo2 \
  libjpeg-dev \
  libgif-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy Python packages and Playwright from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /ms-playwright /ms-playwright

# Create non-root user
RUN useradd -m appuser && \
  chown -R appuser:appuser /app && \
  mkdir -p /home/appuser/.cache && \
  cp -r /ms-playwright /home/appuser/.cache/ms-playwright && \
  chown -R appuser:appuser /home/appuser

# Copy app
COPY . .
RUN chown -R appuser:appuser /app

USER appuser
ENV HOME=/home/appuser

CMD ["python", "run.py"]
