FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for WeasyPrint and other libraries
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

# Install PostgreSQL drivers
RUN uv pip install --system psycopg2-binary

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