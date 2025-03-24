FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for WeasyPrint and Node.js
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    shared-mime-info \
    wkhtmltopdf \
    curl \
    postgresql-client \
    gnupg \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install newer Node.js version (16.x)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv for better dependency management
RUN pip install --upgrade pip uv

# Copy pyproject.toml first for better caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv with --system flag
RUN uv pip install --system -r pyproject.toml
RUN uv pip install --system -e .

# Explicitly install PDF generation libraries with uv
RUN uv pip install --system xhtml2pdf weasyprint pdfkit

# Install APScheduler for report scheduling
RUN uv pip install --system apscheduler>=3.10.1

# Install PostgreSQL drivers
RUN uv pip install --system psycopg2-binary

# Install Node.js dependencies
WORKDIR /app/js
COPY js/package.json ./

# Install Chromium dependencies (required for Puppeteer)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    wget \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js dependencies (first local, then global for backup)
RUN npm install
RUN npm install -g chart.js html-pdf

# Install Puppeteer with Chrome binary matching the container's architecture
# ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
# RUN npm install puppeteer@22.8.2

# Alternative approach: use a pre-built image with Puppeteer installed
# Install Chrome directly for use with Puppeteer
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    apt-get install -y --no-install-recommends chromium && \
    rm -rf /var/lib/apt/lists/*

# Verify chrome installation
RUN which chromium || which chromium-browser || echo "Chrome not found"

# Set Chrome path
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Create a symbolic link to ensure puppeteer is findable
# RUN mkdir -p /usr/local/lib/node_modules && \
#     ln -s /app/js/node_modules/puppeteer /usr/local/lib/node_modules/puppeteer || true

# Return to main directory
WORKDIR /app

# Copy the wait script
COPY wait-for-db.sh .
RUN chmod +x wait-for-db.sh

# Copy the rest of the code
COPY . .

# Ensure the reports directory exists 
RUN mkdir -p reports

# Set permissions
RUN chmod -R 777 reports

# Expose the port
EXPOSE 5174