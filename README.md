# Django + PowerSync Self-Hosted Demo

This is a complete demonstration of a self-hosted PowerSync setup with a Django backend and React frontend client. It showcases real-time data synchronization between a PostgreSQL database and web clients using PowerSync.

## Overview

This repository contains:

- **Django Backend** (`powersync-django-backend-todolist-demo/`) - A Django REST API that provides:

  - Authentication and JWT token generation for PowerSync
  - CRUD operations for todo lists and items
  - JWKS endpoint for PowerSync to validate tokens
  - PostgreSQL database integration

- **React Frontend** (`demo-app/`) - A web application built with:

  - React + Vite
  - PowerSync Web SDK for offline-first data sync
  - Material-UI components
  - Todo list management interface

- **PowerSync Service** - Self-hosted PowerSync instance for data synchronization
- **PostgreSQL Database** - Primary data store
- **MongoDB** - Used internally by PowerSync for sync state management

## Architecture
![alt text](powersync-docs-diagram-architecture-overview.avif)
## Prerequisites

- Docker and Docker Compose (version 2.20.3 or higher)
- No other services running on ports: 3030, 5432, 6061, 8080, 27017

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/AhmedHanye/django-powersync.git
   cd django-powersync
   ```

2. **Configure environment variables** (Optional)

   The `.env` file contains default configuration. You can modify it if needed:

   - `DEMO_BACKEND_PORT=6061` - Django backend port
   - `DEMO_CLIENT_PORT=3030` - Frontend application port
   - `PS_PORT=8080` - PowerSync service port
   - `PG_DATABASE_*` - PostgreSQL credentials

   For production, generate your own JWKS keys:

   ```bash
   # Leave empty for auto-generation during development
   DEMO_JWKS_PUBLIC_KEY=
   DEMO_JWKS_PRIVATE_KEY=
   ```

3. **Start all services**

   ```bash
   docker compose up
   ```

   This will start:

   - PostgreSQL database on port 5432
   - MongoDB (internal) on port 27017
   - Django backend on port 6061
   - PowerSync service on port 8080
   - React frontend on port 3030

4. **Access the application**
   - **Frontend**: http://localhost:3030
   - **Django Backend API**: http://localhost:6061
   - **PowerSync Service**: http://localhost:8080

## Usage

### Frontend Application

Open http://localhost:3030 in your browser. The app uses anonymous authentication with a randomly generated user ID stored in local storage.

Features:

- Create, edit, and delete todo lists
- Add and manage todo items
- Real-time sync across multiple browser tabs/windows
- Offline-first functionality
- SQL console for debugging

### API Endpoints

The Django backend provides these endpoints:

- `GET /api/auth/token?user_id={id}` - Get PowerSync JWT token
- `POST /api/data` - Upload batch operations from client
- `GET /api/get_keys/` - JWKS endpoint for PowerSync

## Development

### Project Structure

```
django-powersync/
├── docker-compose.yaml              # Main orchestration file
├── ps-django-backend.yaml           # Django & frontend services
├── .env                             # Environment configuration
├── config/
│   ├── powersync.yaml              # PowerSync service config
│   └── sync_rules.yaml             # PowerSync sync rules
├── services/
│   ├── postgres.yaml               # PostgreSQL service
│   ├── mongo.yaml                  # MongoDB service
│   └── powersync.yaml              # PowerSync service
├── powersync-django-backend-todolist-demo/
│   ├── manage.py
│   ├── requirements.txt
│   ├── api/                        # Django app
│   │   ├── models.py              # Todo models
│   │   ├── views.py               # API endpoints
│   │   └── urls.py                # URL routing
│   └── todo_list_custom_backend/  # Django project
└── demo-app/
    ├── src/
    │   ├── app/                    # React application
    │   ├── components/             # UI components
    │   └── library/powersync/      # PowerSync configuration
    └── package.json
```

### Running Individual Services

To run only specific services:

```bash
# Backend + Database only
docker compose up pg-db demo-backend

# Frontend only (requires backend running)
docker compose up demo-client
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f demo-backend
docker compose logs -f powersync
```

### Stopping Services

```bash
docker compose down

# Remove volumes (clears database)
docker compose down -v
```

## Configuration Details

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for detailed information about:

- Service configuration
- API endpoint mapping
- Data flow architecture
- Environment variables
- JWT token validation

## Troubleshooting

**Services won't start:**

- Check if ports 3030, 5432, 6061, 8080, 27017 are available
- Run `docker compose down -v` to clean up

**Frontend can't connect to backend:**

- Ensure all services are running: `docker compose ps`
- Check backend logs: `docker compose logs demo-backend`

**Data not syncing:**

- Check PowerSync logs: `docker compose logs powersync`
- Verify PowerSync can reach the backend JWKS endpoint
- Check browser console for client errors

## Related Resources

- [PowerSync Documentation](https://docs.powersync.com/)
- [Django Backend Source](https://github.com/powersync-ja/powersync-django-backend-todolist-demo)
- [PowerSync React SDK](https://docs.powersync.com/client-sdk-references/react)

## License

See individual component licenses:

- Django Backend: [LICENSE](./powersync-django-backend-todolist-demo/LICENSE)
- React Frontend: [LICENSE](./demo-app/LICENSE)
