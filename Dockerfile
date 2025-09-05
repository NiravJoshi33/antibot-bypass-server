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
# Make this optional - if camoufox_cache doesn't exist, create empty directory
COPY camoufox_cache* /tmp/camoufox_cache_temp/
RUN mkdir -p /home/pwuser/.cache/camoufox/ && \
    if [ -d "/tmp/camoufox_cache_temp/camoufox_cache" ]; then \
        cp -r /tmp/camoufox_cache_temp/camoufox_cache/* /home/pwuser/.cache/camoufox/; \
    fi && \
    rm -rf /tmp/camoufox_cache_temp && \
    chown -R pwuser:pwuser /home/pwuser/.cache/camoufox/

# Copy application code
COPY app/ ./app/

# Copy seccomp profile for security
COPY seccomp_profile.json ./

# Create entrypoint script to fix permissions at runtime
RUN echo '#!/bin/bash\n\
# Fix permissions for volume mounts that might override build-time permissions\n\
mkdir -p /home/pwuser/.cache/camoufox\n\
chown -R pwuser:pwuser /home/pwuser/.cache/camoufox\n\
chmod -R 755 /home/pwuser/.cache/camoufox\n\
\n\
# Switch to pwuser and execute the command\n\
exec gosu pwuser "$@"' > /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Install gosu for secure user switching (Ubuntu equivalent of su-exec)
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    chown -R pwuser:pwuser /app && \
    chmod -R 755 /app

# Don't switch to pwuser here - let entrypoint handle it
# USER pwuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint to fix permissions, then run as pwuser
ENTRYPOINT ["/entrypoint.sh"]
CMD ["pdm", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
