# Django + PowerSync Integration Configuration Summary

## Overview

This document summarizes the configuration changes made to integrate the Django backend with the demo-app frontend client for PowerSync.

## Configuration Changes Made

### 1. **Main Docker Compose Configuration** (`ps-django-backend.yaml`)

- **Changed**: Build context from GitHub URL to local folder `./powersync-django-backend-todolist-demo`
- **Added**: `demo-client` service for the frontend application
- **Updated**: `POWERSYNC_URL` to use internal Docker service name `http://powersync:${PS_PORT}`
- **Added**: `JWT_ISSUER` environment variable for proper JWT token validation
- **Configured**: Frontend build args and environment variables for VITE

### 2. **Django Backend Configuration** (`powersync-django-backend-todolist-demo/.env`)

- **Created**: New `.env` file with all required environment variables
- **Configured**: Database connection to use Docker service names
- **Set**: PowerSync URL to internal Docker network address
- **Set**: JWT issuer URL for token validation

### 3. **Frontend Client Configuration** (`demo-app/.env.local`)

- **Created**: New `.env.local` file for Vite environment variables
- **Set**: `VITE_BACKEND_URL=http://localhost:6061` (accessible from host)
- **Set**: `VITE_POWERSYNC_URL=http://localhost:8080` (accessible from host)
- **Set**: `VITE_CHECKPOINT_MODE=managed`

### 4. **Django API URLs** (`powersync-django-backend-todolist-demo/api/urls.py`)

- **Added**: `api/auth/token` endpoint (matches client expectation)
- **Added**: `api/data` endpoint for batch operations
- **Kept**: Legacy endpoints for backward compatibility

### 5. **Django API Views** (`powersync-django-backend-todolist-demo/api/views.py`)

- **Updated**: `get_powersync_token` to accept `user_id` query parameter
- **Refactored**: `upload_data` to handle both batch and single operations
- **Added**: `process_operation` helper function for cleaner code
- **Improved**: Error handling and operation processing

### 6. **Django Utilities** (`powersync-django-backend-todolist-demo/api/app_utils.py`)

- **Fixed**: Hardcoded ngrok URL replaced with environment variable `JWT_ISSUER`
- **Added**: Fallback default value for JWT issuer

### 7. **Main Environment File** (`.env`)

- **Added**: `VITE_CHECKPOINT_MODE=managed` for client configuration
- **Improved**: Documentation and organization of environment variables

## Service Architecture

```
┌─────────────────┐
│   PostgreSQL    │ (pg-db:5432)
│   Database      │
└────────┬────────┘
         │
         │
┌────────▼────────┐      ┌─────────────────┐
│  Django Backend │◄─────┤   PowerSync     │
│  (demo-backend) │      │   Service       │
│  Port: 6061     │      │  Port: 8080     │
└────────┬────────┘      └────────▲────────┘
         │                        │
         │                        │
┌────────▼────────────────────────┘
│   Frontend Client (demo-client) │
│   Port: 3030 → 4173             │
└─────────────────────────────────┘
```

## API Endpoint Mapping

### Client → Backend

- `GET /api/auth/token?user_id={id}` - Get PowerSync JWT token
- `POST /api/data` - Upload batch operations from PowerSync
  - Body: `{ "batch": [{ "op": "PUT|PATCH|DELETE", "table": "todos|lists", "id": "...", "data": {...} }] }`

### Backend → PowerSync

- PowerSync fetches JWKS from: `http://demo-backend:6061/api/get_keys/`

## How Data Flows

1. **Client connects to PowerSync**:

   - Client requests token from `http://localhost:6061/api/auth/token`
   - Backend generates JWT signed with private key
   - Client uses token to authenticate with PowerSync

2. **PowerSync validates token**:

   - PowerSync fetches public key from `http://demo-backend:6061/api/get_keys/`
   - Validates JWT signature and claims

3. **Data synchronization**:
   - Client queries PowerSync for data
   - PowerSync streams changes from PostgreSQL
   - Client makes local changes
   - Client uploads changes to `http://localhost:6061/api/data`
   - Backend processes batch and updates PostgreSQL
   - PostgreSQL replication triggers PowerSync sync

## Running the Stack

### Start all services:

```bash
docker compose up
```

### Access points:

- **Frontend Client**: http://localhost:3030
- **Django Backend**: http://localhost:6061
- **PowerSync API**: http://localhost:8080

### First-time setup:

The Django backend will automatically:

1. Run migrations to create database tables
2. Create a test user (see migration 0002_create_test_user.py)
3. Create PostgreSQL publication for replication (see migration 0003_create_publication.py)
4. Generate temporary JWT keys if not provided in environment

## Environment Variables Reference

### Required (with defaults)

- `PG_DATABASE_NAME=django_demo`
- `PG_DATABASE_PORT=5432`
- `PG_DATABASE_USER=postgres`
- `PG_DATABASE_PASSWORD=mypassword`
- `DEMO_BACKEND_PORT=6061`
- `DEMO_CLIENT_PORT=3030`
- `PS_PORT=8080`
- `VITE_CHECKPOINT_MODE=managed`

### Optional

- `DEMO_JWKS_PUBLIC_KEY` - Custom JWT public key (auto-generated if empty)
- `DEMO_JWKS_PRIVATE_KEY` - Custom JWT private key (auto-generated if empty)

## Key Features

1. **Automatic Key Generation**: If JWT keys are not provided, the backend generates temporary keys on startup
2. **Batch Operations**: Client can send multiple CRUD operations in a single request
3. **Backward Compatibility**: Legacy API endpoints still work for older clients
4. **Service Discovery**: All services communicate via Docker internal DNS
5. **Hot Reload**: Frontend supports Vite hot module replacement during development

## Troubleshooting

### Client can't connect to backend

- Ensure `VITE_BACKEND_URL=http://localhost:6061` (not demo-backend)
- Check that backend service is healthy: `docker compose ps`

### PowerSync can't validate tokens

- Check JWKS URL: http://localhost:6061/api/get_keys/
- Verify `PS_JWKS_URL` matches backend service name in docker-compose

### Database connection errors

- Ensure PostgreSQL is healthy: `docker compose logs pg-db`
- Verify database credentials match in all .env files

### Frontend build errors

- Check that .env.local exists in demo-app folder
- Verify all VITE\_\* variables are set correctly

## Next Steps

1. **Production Deployment**: Replace auto-generated keys with proper key management
2. **Authentication**: Implement real user authentication (currently uses anonymous users)
3. **CORS**: Configure CORS properly for production domains
4. **HTTPS**: Add SSL/TLS termination for production
5. **Monitoring**: Add logging and monitoring for all services
