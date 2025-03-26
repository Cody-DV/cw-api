# CardWatch Reporting API

A Flask-based API for generating nutrition reports with PDF generation capabilities.

## Running with Docker (Recommended)

The easiest way to run this application is with Docker, which handles all dependencies automatically.

### Prerequisites

- Docker
- Docker Compose

### Setup and Run

1. Clone the repository
2. Start the application with Docker Compose:

```bash
docker-compose up -d
```

This will:
- Build the Docker image with all necessary dependencies
- Start the Flask API on port 5174
- Start a PostgreSQL database
- Mount your local code directory for easy development

3. Access the API at http://localhost:5174

### Development

The Docker setup mounts your local code into the container, so any changes you make to the code will be reflected immediately in the running container. The only time you need to rebuild is if you change dependencies in pyproject.toml.

To rebuild:

```bash
docker-compose build
docker-compose up -d
```

### Viewing logs

```bash
docker-compose logs -f api
```

4. **Create a `.env` file**:
   The application requires an OpenAI API key to function properly. Create a `.env` file in the root directory of the project and add your OpenAI API key:
   ```
   AZURE_OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Test the `/prompt` route**:
   ```bash
   curl -X GET http://localhost:5174/prompt
   ```

## Manual Setup (Alternative)

If you prefer to run the application without Docker, follow these steps:

1. **Ensure Python 3.12 is installed**:
   ```bash
   python --version
   ```

2. **Install `uv`**:
   ```bash
   pip install uv
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -r pyproject.toml
   ```

4. **Run the application**:
   ```bash
   source .venv/bin/activate
   python app.py
   ```

The application will be running in debug mode and can be accessed at `http://localhost:5174/`.

### System Dependencies

For PDF generation without Docker, you'll need to install multiple system dependencies:

- libpango-1.0-0
- libpangoft2-1.0-0
- libpangocairo-1.0-0
- libgdk-pixbuf2.0-0
- libcairo2-dev
- libxml2-dev
- libxslt1-dev
- libffi-dev
- shared-mime-info
- xhtml2pdf (Python package alternative that requires fewer system dependencies)

## Database Initialization

1. **Pull Postgres Docker Image**:
    ```
    docker pull postgres
    ```


2. **Initialize Database**:
   ```
   docker run --name cw-postgres \
   -e POSTGRES_PASSWORD=pass \
   -v $(pwd)/db/initdb:/docker-entrypoint-initdb.d \
   -p 5432:5432 \
   -d postgres
   ```

3. **Populate tables with sample data**:
    ```
    cat db/populate_sample_data.sql | docker exec -i cw-postgres psql -U postgres -d patient_nutrition_demo
    ```

4. **Verify the data**:
   ```
   docker exec -it cw-postgres bash

   psql -U postgres -d patient_nutrition_demo

   \dt
   ```

