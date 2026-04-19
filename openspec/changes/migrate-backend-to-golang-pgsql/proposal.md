## Why

The current Python/FastAPI backend faces critical limitations for concurrent test execution: Python's GIL restricts true parallelism, asyncio subprocess handling requires platform-specific workarounds on Windows, and thread pool scalability is limited. As test volume grows, we need a backend that can efficiently handle 100+ concurrent test executions with lower resource consumption and simpler deployment.

## What Changes

- Replace Python/FastAPI backend with Golang/Gin framework
- Migrate from SQLite to PostgreSQL for better concurrency and production readiness
- Rewrite all API endpoints in Golang with identical REST interface
- Implement goroutine-based concurrent test execution (no GIL, no event loop issues)
- Maintain backward compatibility with existing frontend and test scripts
- Deploy as single binary with embedded migrations

## Capabilities

### New Capabilities
- `golang-api-server`: Golang-based REST API server using Gin framework with CORS, authentication, and error handling
- `pgsql-data-layer`: PostgreSQL database integration with connection pooling and migration management
- `concurrent-execution`: Goroutine-based test script execution engine supporting 100+ concurrent runs
- `script-lifecycle`: Script upload, storage, validation, and retrieval with file system management
- `execution-monitoring`: Real-time execution status tracking with structured logging to files and database

### Modified Capabilities
<!-- No existing capabilities are being modified - this is a complete backend rewrite -->

## Impact

**Code Changes:**
- Complete rewrite of `backend/` directory in Golang
- Database schema migration from SQLite to PostgreSQL
- New environment configuration for PostgreSQL connection

**API Compatibility:**
- All REST endpoints maintain same paths and request/response formats
- Frontend requires no changes (same API contract)
- Authentication tokens remain JWT-based

**Dependencies:**
- Remove: Python, FastAPI, uvicorn, SQLite
- Add: Golang 1.21+, Gin, pgx (PostgreSQL driver), golang-migrate

**Deployment:**
- Single binary deployment (no virtual environment needed)
- PostgreSQL server required (local or remote)
- Simplified cross-platform deployment (Windows/Linux identical)

**Testing:**
- Existing Python test scripts continue to work unchanged
- Environment variables (GIDS_ADDR, etc.) injected identically
- Log format and storage paths remain consistent
