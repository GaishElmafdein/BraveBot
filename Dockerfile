# 🐳 BraveBot Dockerfile
# Multi-stage build for production optimization

# Build stage
FROM python:3.11-slim as builder

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash bravebot

# Set work directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/bravebot/.local

# Make sure scripts in .local are usable
ENV PATH=/home/bravebot/.local/bin:$PATH

# Copy application code
COPY --chown=bravebot:bravebot . .

# Create necessary directories
RUN mkdir -p backups logs analytics config \
    && chown -R bravebot:bravebot /app

# Switch to non-root user
USER bravebot

# Create default config if not exists
RUN if [ ! -f config/config.yaml ]; then \
    echo "max_price: 10000" > config/config.yaml && \
    echo "min_price: 0.01" >> config/config.yaml && \
    echo "admin_ids: []" >> config/config.yaml; \
    fi

# Health check
HEALTHCHECK --interval=1m --timeout=10s --start-period=30s --retries=3 \
    CMD python scripts/health_check.py || exit 1

# Expose port (for Railway or other platforms)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]
