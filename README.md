# ScopeWise - AI-Powered Project Scoping Tool

A full-stack project scoping application that uses LangChain agents to analyze project requirements and generate comprehensive scope documents with real-time streaming.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Vue 3     │────────▶│   Laravel    │────────▶│  Python FastAPI │
│  Frontend   │  SSE    │   Backend    │  Guzzle │  LangChain Agent│
│  (TypeScript)│         │   (PHP)      │         │   (Python)      │
└─────────────┘         └──────────────┘         └─────────────────┘
```

### Components

1. **Vue 3 Frontend** (`/frontend`)
   - Discovery form with 8+ fields (project type, budget, timeline, features, etc.)
   - Pinia store for state management
   - SSE composable for real-time streaming
   - Section-by-section scope document viewer

2. **Laravel Backend** (`/backend`)
   - API proxy to Python FastAPI service
   - SSE streaming endpoint
   - Guzzle HTTP client for external API calls
   - CORS configuration

3. **Python FastAPI Service** (`/Python/scopewise`)
   - LangChain agent with 3-step pipeline
   - Classify project complexity
   - Identify feature risks
   - Generate structured scope document

## Setup Instructions

### Prerequisites

- PHP 8.3+
- Composer
- Node.js 20+
- Python 3.10+
- Poetry (for Python dependencies)

### 1. Python FastAPI Service

```bash
cd /home/zt113/Learning/Python/scopewise

# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key and other settings

# Run migrations
poetry run alembic upgrade head

# Start the service
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The Python service will be available at `http://localhost:8000`

### 2. Laravel Backend

```bash
cd /home/zt113/Learning/ScopeWise/backend

# Install dependencies
composer install

# Set up environment
cp .env.example .env
# Edit .env and ensure PYTHON_SERVICE_URL=http://localhost:8000

# Generate application key
php artisan key:generate

# Run migrations
php artisan migrate

# Start the Laravel server
php artisan serve --host=0.0.0.0 --port=8000
```

The Laravel API will be available at `http://localhost:8000/api`

### 3. Vue 3 Frontend

```bash
cd /home/zt113/Learning/ScopeWise/frontend

# Install dependencies
npm install

# Set up environment
echo "VITE_LARAVEL_API_URL=http://localhost:8000/api" > .env

# Start the development server
npm run dev
```

The Vue frontend will be available at `http://localhost:5173`

## API Endpoints

### Laravel Backend

- `GET /api/health` - Health check for Python service
- `POST /api/pipeline/run` - Blocking execution of scope pipeline
- `POST /api/pipeline/run-stream` - SSE streaming execution
- `GET /api/pipeline/stream/{requestId}` - Status polling SSE stream

### Python FastAPI

- `POST /api/pipeline/run` - Blocking execution
- `POST /api/pipeline/run-stream` - SSE streaming
- `GET /api/pipeline/stream/{requestId}` - Status polling
- `GET /health` - Health check

## Usage

1. Open the Vue frontend at `http://localhost:5173`
2. Fill out the discovery form with project details:
   - Project Type (required)
   - Budget Range (required)
   - Timeline (required)
   - Key Features (required, add multiple)
   - Target Audience
   - Technical Requirements
   - Business Goals
   - Constraints
   - Additional Notes
3. Click "Generate Scope" to start the analysis
4. Watch the scope document appear section-by-section in real-time
5. Review the generated scope document with:
   - Complexity assessment
   - Cost & timeline estimates
   - Deliverables
   - Recommended tech stack
   - Timeline breakdown
   - Potential risks
   - Out-of-scope items

## Project Structure

```
ScopeWise/
├── backend/                    # Laravel Backend
│   ├── app/
│   │   ├── Http/
│   │   │   ├── Controllers/
│   │   │   │   └── ScopePipelineController.php
│   │   │   └── Requests/
│   │   │       └── PipelineRunRequest.php
│   │   └── Services/
│   │       └── PythonService.php
│   ├── config/
│   │   ├── cors.php
│   │   └── services.php
│   ├── routes/
│   │   └── api.php
│   └── .env.example
├── frontend/                   # Vue 3 Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DiscoveryForm.vue
│   │   │   └── ScopeDocumentViewer.vue
│   │   ├── composables/
│   │   │   └── useAgentStream.ts
│   │   ├── stores/
│   │   │   └── discovery.ts
│   │   └── App.vue
│   └── .env
└── README.md
```

## Technology Stack

### Frontend
- Vue 3 with Composition API
- TypeScript
- Pinia (state management)
- Tailwind CSS (styling)
- Vite (build tool)

### Backend
- Laravel 13 (PHP framework)
- Guzzle HTTP Client
- SSE (Server-Sent Events)

### AI Service
- FastAPI (Python web framework)
- LangChain (LLM orchestration)
- SQLAlchemy (ORM)
- Alembic (database migrations)

## Development

### Running All Services

For development, you'll need three terminals:

```bash
# Terminal 1: Python Service
cd /home/zt113/Learning/Python/scopewise
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Laravel Backend
cd /home/zt113/Learning/ScopeWise/backend
php artisan serve --host=0.0.0.0 --port 8000

# Terminal 3: Vue Frontend
cd /home/zt113/Learning/ScopeWise/frontend
npm run dev
```

### Environment Variables

**Backend (.env)**
```
PYTHON_SERVICE_URL=http://localhost:8000
```

**Frontend (.env)**
```
VITE_LARAVEL_API_URL=http://localhost:8000/api
```

**Python (.env)**
```
OPENAI_API_KEY=your_openai_api_key
# Other configuration from .env.example
```

## Troubleshooting

### CORS Errors
Ensure Laravel CORS configuration allows requests from your frontend origin.

### SSE Connection Issues
- Check that all three services are running
- Verify the API URLs in environment variables
- Check browser console for connection errors

### Python Service Unavailable
- Verify the Python service is running on port 8000
- Check that OPENAI_API_KEY is set correctly
- Review Python service logs for errors

## License

MIT
