# Backend API

FastAPI backend for the drone surveillance system.

## Features

- REST API for drones, zones, and events management
- WebSocket endpoint for real-time alerts
- PostgreSQL persistence with Alembic migrations
- Redis integration for pub/sub alerts
- Automatic event persistence from Redis channel

## Running Locally

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with PostGIS
- Redis 7+

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Set environment variables:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/drone_surveillance"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_CHANNEL="alerts"
```

### Database Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /api/health` - System health status

### Drones
- `GET /api/drones` - List all drones
- `GET /api/drones/{drone_id}` - Get specific drone
- `POST /api/drones` - Create new drone
- `PUT /api/drones/{drone_id}` - Update drone
- `DELETE /api/drones/{drone_id}` - Delete drone

### Zones
- `GET /api/zones` - List all zones
- `GET /api/zones/{zone_id}` - Get specific zone
- `POST /api/zones` - Create new zone
- `PUT /api/zones/{zone_id}` - Update zone
- `DELETE /api/zones/{zone_id}` - Delete zone

### Events
- `GET /api/events` - List events (with filters)
- `GET /api/events/{alert_id}` - Get specific event
- `POST /api/events` - Create new event
- `PUT /api/events/{alert_id}` - Update event (e.g., acknowledge)
- `DELETE /api/events/{alert_id}` - Delete event

## WebSocket

### Real-time Alerts

Connect to `/ws/alerts?client_id=<your_id>` to receive real-time alerts.

Example (JavaScript):

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts?client_id=dashboard-1');

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Received alert:', alert);
};
```

## Docker

Build and run with Docker Compose:

```bash
docker-compose up -d backend
```

## Architecture

- **app/main.py** - FastAPI application entry point
- **app/api/** - REST API routes and schemas
- **app/models/** - SQLAlchemy models
- **app/db/** - Database configuration
- **app/websocket/** - WebSocket manager and Redis subscriber
- **app/services/** - Background services (event persister)

## License

MIT
