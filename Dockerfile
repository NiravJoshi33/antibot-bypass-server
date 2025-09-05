# Use the official Playwright Docker image as base
FROM mcr.microsoft.com/playwright:v1.55.0-noble

# Set working directory
WORKDIR /app

# Install Python and pip (use system Python)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY pyproject.toml pdm.lock ./
RUN pip install --no-cache-dir pdm

# Install project dependencies
RUN pdm install --no-lock --no-editable

# Install playwright system dependencies (fallback installation if PDM didn't include it)
RUN /opt/venv/bin/pip install playwright
RUN /opt/venv/bin/python -m playwright install-deps

# Copy pre-downloaded Camoufox cache to avoid 707MB download on first request
# On Linux, Camoufox stores cache in ~/.cache/camoufox
COPY camoufox_cache/ /home/pwuser/.cache/camoufox/
RUN chown -R pwuser:pwuser /home/pwuser/.cache/camoufox/

# Copy application code
COPY app/ ./app/

# Copy seccomp profile for security
COPY seccomp_profile.json ./

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    chown -R pwuser:pwuser /app && \
    chmod -R 755 /app

# Switch to non-root user
USER pwuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["pdm", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
