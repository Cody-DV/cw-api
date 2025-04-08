# CardWatch Reporting API

A Flask-based API for generating nutrition reports with PDF generation capabilities and AI integration.

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
4. Access the Frontend at http://localhost:3000

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
   AZUREAI_ENDPOINT_URL=https://cardwatch-reporting-ai.openai.azure.com/
   ```
