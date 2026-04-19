## Context

The current Python/FastAPI backend uses SQLite and asyncio for test script execution. While functional, it faces scalability issues:
- Python's GIL prevents true parallel execution of CPU-bound tasks
- asyncio subprocess handling requires platform-specific workarounds on Windows (ProactorEventLoop)
- SQLite lacks concurrent write support needed for high-volume test execution
- Thread pool executor limits concurrent execution to ~50-100 tests
- Deployment requires Python virtual environment and dependency management

This design migrates to Golang + PostgreSQL to enable 100+ concurrent test executions with lower resource consumption and simpler deployment.

## Goals / Non-Goals

**Goals:**
- Replace Python backend with Golang while maintaining API compatibility
- Migrate from SQLite to PostgreSQL for production-grade concurrency
- Support 100+ concurrent test script executions using goroutines
- Maintain backward compatibility with existing frontend (no frontend changes)
- Preserve test script compatibility (Python/Shell/JS scripts continue to work)
- Deploy as single binary with embedded migrations
- Achieve <100ms API response time for non-execution endpoints
- Reduce memory footprint by 50% compared to Python implementation

**Non-Goals:**
- Rewriting existing test scripts (they remain in Python/Shell/JS)
- Changing frontend code or API contracts
- Implementing new features beyond current functionality
- Supporting databases other than PostgreSQL
- Backward compatibility with SQLite data (fresh start acceptable)

## Decisions

### Decision 1: Golang with Gin framework
**Choice:** Use Golang 1.21+ with Gin web framework

**Rationale:**
- Gin provides high-performance HTTP routing with middleware support
- Native goroutine support enables true concurrent execution without GIL
- Single binary deployment simplifies operations
- Excellent standard library for subprocess management (os/exec)
- Strong typing catches errors at compile time

**Alternatives considered:**
- Echo framework: Similar performance, but Gin has larger community
- Standard library net/http: More verbose, Gin provides better DX
- Keep Python with multiprocessing: Still has deployment complexity and higher resource usage

### Decision 2: PostgreSQL with pgx driver
**Choice:** Use PostgreSQL 14+ with pgx/v5 driver

**Rationale:**
- pgx is the fastest PostgreSQL driver for Go (pure Go, no CGO)
- Built-in connection pooling with configurable limits
- Excellent support for prepared statements and transactions
- PostgreSQL handles concurrent writes efficiently (vs SQLite's write lock)
- Production-ready with ACID guarantees

**Alternatives considered:**
- MySQL: Less robust JSON support, weaker transaction isolation
- database/sql with pq driver: pgx is faster and has better features
- Keep SQLite: Cannot handle concurrent writes, not production-ready

### Decision 3: Goroutine-based execution with semaphore
**Choice:** Use goroutines with weighted semaphore for concurrency control

**Rationale:**
- Goroutines are lightweight (~2KB vs 8MB for threads)
- Semaphore prevents resource exhaustion while allowing high concurrency
- context.Context provides timeout and cancellation support
- No event loop complexity or platform-specific issues

**Implementation:**
```go
// Semaphore limits concurrent executions
sem := semaphore.NewWeighted(100)

// Each execution runs in a goroutine
go func(executionID int) {
    sem.Acquire(ctx, 1)
    defer sem.Release(1)

    cmd := exec.CommandContext(ctx, "python", scriptPath)
    // Execute and capture output
}(id)
```

**Alternatives considered:**
- Worker pool pattern: More complex, semaphore is simpler and sufficient
- Unlimited goroutines: Risk of resource exhaustion
- Channel-based queue: Adds complexity without clear benefit

### Decision 4: Dual log storage (database + files)
**Choice:** Write logs to both PostgreSQL and file system simultaneously

**Rationale:**
- Database logs enable fast querying and filtering via API
- File logs provide long-term retention and external tool analysis
- Redundancy protects against data loss
- File logs can be rotated/archived independently

**Implementation:**
- Database: execution_logs table with execution_id, log_type, content, timestamp
- Files: logs/executions/execution_{id}.log with structured format
- Async writes to prevent blocking execution

**Alternatives considered:**
- Database only: Harder to analyze with external tools, retention issues
- Files only: Slower API queries, no structured filtering
- Message queue (Kafka/Redis): Over-engineered for current scale

### Decision 5: Database migration with golang-migrate
**Choice:** Use golang-migrate library with embedded migration files

**Rationale:**
- Migrations run automatically on startup
- Version tracking prevents duplicate application
- Rollback support for failed migrations
- Embed migration files in binary using go:embed

**Implementation:**
```go
//go:embed migrations/*.sql
var migrationsFS embed.FS

// Apply migrations on startup
m, _ := migrate.NewWithSourceInstance("iofs", driver, dbURL)
m.Up()
```

**Alternatives considered:**
- Manual SQL scripts: Error-prone, no version tracking
- ORM migrations (GORM): Adds dependency, less control
- External migration tool: Requires separate deployment step

### Decision 6: API compatibility layer
**Choice:** Maintain exact same REST API paths and response formats

**Rationale:**
- Frontend requires zero changes
- Gradual migration possible (run both backends temporarily)
- Reduces risk and testing burden

**Mapping:**
- POST /api/v1/auth/login → JWT generation (same format)
- GET /api/v1/scripts → Script listing (same JSON structure)
- POST /api/v1/executions → Create execution (same response)
- All error responses maintain same format: {code, message, data}

### Decision 7: Environment-based configuration
**Choice:** Use environment variables with .env file support

**Rationale:**
- 12-factor app compliance
- Easy to configure in different environments
- No hardcoded credentials
- Compatible with Docker/Kubernetes

**Configuration:**
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testplatform
DB_USER=postgres
DB_PASSWORD=secret
SERVER_PORT=8011
JWT_SECRET=...
MAX_CONCURRENT_EXECUTIONS=100
```

## Risks / Trade-offs

### Risk 1: PostgreSQL dependency
**Risk:** Requires PostgreSQL server, more complex than SQLite
**Mitigation:**
- Provide docker-compose.yml for local development
- Document PostgreSQL installation for all platforms
- Include health checks to detect connection issues early

### Risk 2: Data migration complexity
**Risk:** Existing SQLite data cannot be automatically migrated
**Mitigation:**
- Accept fresh start (test platform is new, limited production data)
- Provide manual migration script if needed
- Export/import scripts via API if users need to preserve data

### Risk 3: Golang learning curve
**Risk:** Team may be more familiar with Python
**Mitigation:**
- Provide clear code structure and documentation
- Use standard patterns (repository, service layers)
- Golang is simpler than Python for this use case (no async complexity)

### Risk 4: Concurrent execution resource limits
**Risk:** 100+ concurrent subprocesses may exhaust system resources
**Mitigation:**
- Configurable semaphore limit (default 100, adjustable)
- Monitor system resources and adjust limits
- Implement graceful degradation (queue requests when at limit)
- Document recommended system requirements

### Risk 5: Log file disk space
**Risk:** High execution volume could fill disk with log files
**Mitigation:**
- Implement log rotation (100MB per file)
- Automatic cleanup of logs older than 30 days
- Configurable retention policy
- Monitor disk usage and alert when low

### Trade-off 1: Compile time vs runtime flexibility
**Trade-off:** Golang requires compilation, Python is interpreted
**Benefit:** Catch errors at compile time, faster execution, single binary deployment
**Cost:** Need to rebuild for code changes (acceptable for backend service)

### Trade-off 2: Memory vs speed
**Trade-off:** Dual log storage uses more memory/disk
**Benefit:** Fast API queries + long-term file analysis
**Cost:** ~2x storage for logs (acceptable given benefits)

## Migration Plan

### Phase 1: Setup (Week 1)
1. Initialize Golang project structure
2. Set up PostgreSQL database (local + CI)
3. Create database schema and migrations
4. Implement configuration management

### Phase 2: Core Implementation (Week 2-3)
1. Implement database layer (repositories)
2. Build API server with Gin (routes, middleware)
3. Implement authentication (JWT)
4. Create service layer (business logic)

### Phase 3: Execution Engine (Week 3-4)
1. Implement goroutine-based execution engine
2. Add subprocess management with context
3. Implement dual log storage
4. Add execution status tracking

### Phase 4: Testing & Migration (Week 4-5)
1. Integration testing with existing frontend
2. Load testing (100+ concurrent executions)
3. Documentation updates
4. Deploy alongside Python backend for validation

### Phase 5: Cutover (Week 5)
1. Switch frontend to Golang backend
2. Monitor for issues
3. Decommission Python backend after 1 week of stable operation

### Rollback Strategy
- Keep Python backend running in parallel during migration
- Frontend can switch back via environment variable change
- Database rollback: restore PostgreSQL backup or revert to SQLite
- Code rollback: revert Git commit and redeploy Python version

## Open Questions

1. **PostgreSQL hosting:** Self-hosted or managed service (AWS RDS, Azure Database)?
   - Decision: Start with self-hosted, document managed service setup

2. **Log retention policy:** How long to keep execution logs?
   - Proposal: 30 days in database, 90 days in files (configurable)

3. **Concurrent execution limit:** What's the optimal default?
   - Proposal: 100 (adjustable via config), validate with load testing

4. **Authentication migration:** Migrate existing user accounts or fresh start?
   - Proposal: Fresh start acceptable (test platform is new)

5. **Monitoring and observability:** Prometheus metrics? Structured logging format?
   - Proposal: Add Prometheus metrics endpoint, use JSON structured logging
