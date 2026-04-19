# Test Platform Backend (Golang)

A high-performance test execution platform backend built with Golang, Gin, and PostgreSQL.

## Features

- **High Concurrency**: Support for 100+ concurrent test script executions using goroutines
- **Multiple Languages**: Execute Python, Shell, and JavaScript test scripts
- **Dual Logging**: Logs stored in both PostgreSQL database and file system
- **JWT Authentication**: Secure API endpoints with JWT tokens
- **RESTful API**: Clean and consistent API design
- **Database Migrations**: Automated schema management with golang-migrate

## Tech Stack

- **Language**: Go 1.21+
- **Web Framework**: Gin
- **Database**: PostgreSQL 14+
- **Database Driver**: pgx/v5 (pure Go, no CGO)
- **Authentication**: JWT (golang-jwt/v5)
- **Configuration**: Viper
- **Migrations**: golang-migrate

## Prerequisites

- Go 1.21 or higher
- PostgreSQL 14 or higher
- Python 3.x (for Python test scripts)
- Node.js (for JavaScript test scripts)
- Bash (for shell test scripts)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
go mod download
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

4. Start PostgreSQL (using Docker):
```bash
docker-compose up -d postgres
```

5. Run the server:
```bash
go run cmd/server/main.go
```

## Configuration

Environment variables (`.env` file):

```env
# Server
SERVER_PORT=8011

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=testplatform
DB_MAX_CONNS=25
DB_MIN_CONNS=5

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION=24h

# Executor
MAX_CONCURRENT_EXECUTIONS=100
DEFAULT_TIMEOUT=3600s
UPLOAD_DIR=data/uploads
LOG_DIR=logs

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Scripts
- `POST /api/scripts` - Upload test script
- `GET /api/scripts` - List scripts
- `GET /api/scripts/:id` - Get script details
- `PUT /api/scripts/:id` - Update script
- `DELETE /api/scripts/:id` - Delete script

### Executions
- `POST /api/executions` - Start execution
- `GET /api/executions` - List executions
- `GET /api/executions/:id` - Get execution details
- `GET /api/executions/:id/logs` - Get execution logs
- `DELETE /api/executions/:id` - Delete execution

### Configuration
- `GET /api/configs` - List configurations
- `GET /api/configs/:key` - Get configuration
- `POST /api/configs` - Set configuration
- `DELETE /api/configs/:key` - Delete configuration

### Health Check
- `GET /health` - Health check
- `GET /api/health` - Health check

## Building

Build the binary:
```bash
go build -o server cmd/server/main.go
```

Build Docker image:
```bash
docker build -t testplatform-backend .
```

## Deployment

Using Docker Compose:
```bash
docker-compose up -d
```

This will start both PostgreSQL and the backend service.

## Database Migrations

Migrations are automatically run on startup. The migration files are embedded in the binary.

Migration files are located in `migrations/`:
- `000001_create_users_table.up.sql`
- `000002_create_test_scripts_table.up.sql`
- `000003_create_test_executions_table.up.sql`
- `000004_create_execution_logs_table.up.sql`
- `000005_create_global_configs_table.up.sql`

## Default Credentials

- Username: `admin`
- Password: `admin123`

**Important**: Change the default password in production!

## Architecture

```
backend-go/
├── cmd/
│   └── server/          # Application entry point
├── internal/
│   ├── auth/            # JWT and password handling
│   ├── config/          # Configuration management
│   ├── database/        # Database connection and migrations
│   ├── executor/        # Test execution engine
│   ├── handlers/        # HTTP request handlers
│   ├── middleware/      # HTTP middleware
│   ├── models/          # Data models
│   ├── repository/      # Database repositories
│   └── server/          # HTTP server setup
├── migrations/          # Database migration files
├── .env.example         # Example environment configuration
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker image definition
└── go.mod              # Go module definition
```

## License

MIT
