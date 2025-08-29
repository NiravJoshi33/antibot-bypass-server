# Use the official Playwright Docker image as base
FROM mcr.microsoft.com/playwright:v1.55.0-noble

# Set working directory
WORKDIR /app

# Install Python and pip (use system Python)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY pyproject.toml pdm.lock ./
RUN pip install --no-cache-dir pdm

# Install project dependencies
RUN pdm install --no-lock --no-editable

# Copy application code
COPY app/ ./app/

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    chown -R pwuser:pwuser /app

# Switch to non-root user
USER pwuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["pdm", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
