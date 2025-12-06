############################
# Stage 1: Builder
############################
FROM python:3.11-slim AS builder

# Workdir inside the image
WORKDIR /app

# Install build tools for some Python packages, then clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install into a temp prefix
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


############################
# Stage 2: Runtime
############################
FROM python:3.11-slim

# Environment
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC
ENV SEED_FILE_PATH=/data/seed.txt

# Set working directory
WORKDIR /app

# Install cron + tzdata, set timezone to UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata \
 && ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code and keys
COPY app ./app
COPY scripts ./scripts
COPY cron ./cron
COPY student_private.pem student_public.pem instructor_public.pem ./

# Create volume mount points and set permissions
RUN mkdir -p /data /cron && \
    chmod 755 /data /cron

# Install cron job file
# cron/2fa-cron already has LF line endings because of .gitattributes
RUN chmod 644 cron/2fa-cron && \
    crontab cron/2fa-cron

# Expose API port
EXPOSE 8080

# Start cron daemon and API server on container launch
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
