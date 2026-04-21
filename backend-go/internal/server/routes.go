package server

import (
	"database/sql"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/testplatform/backend/internal/database"
	"github.com/testplatform/backend/internal/executor"
	"github.com/testplatform/backend/internal/handlers"
	"github.com/testplatform/backend/internal/middleware"
	"github.com/testplatform/backend/internal/repository"
)

// SetupRoutes configures all routes
func (s *Server) SetupRoutes(db *sql.DB, exec *executor.Executor) {
	// Setup middleware
	s.router.Use(middleware.CORS())
	s.router.Use(middleware.Logger())
	s.router.Use(middleware.Recovery())
	s.router.Use(middleware.ErrorHandler())

	// Initialize repositories
	userRepo := repository.NewUserRepository(db)
	scriptRepo := repository.NewScriptRepository(db)
	executionRepo := repository.NewExecutionRepository(db)
	executionLogRepo := repository.NewExecutionLogRepository(db)
	configRepo := repository.NewConfigRepository(db)

	// Initialize handlers
	authHandler := handlers.NewAuthHandler(userRepo, s.config)
	scriptHandler := handlers.NewScriptHandler(scriptRepo, s.config)
	executionHandler := handlers.NewExecutionHandler(executionRepo, executionLogRepo, scriptRepo, exec)
	configHandler := handlers.NewConfigHandler(configRepo)

	// Health check endpoints
	s.router.GET("/health", s.healthCheck)
	s.router.GET("/api/health", s.healthCheck)

	// API routes
	api := s.router.Group("/api/v1")
	{
		// Auth routes (no auth required)
		api.POST("/auth/login", authHandler.Login)
		api.POST("/auth/logout", authHandler.Logout)

		// Protected routes
		protected := api.Group("")
		protected.Use(middleware.AuthMiddleware(s.config.JWT.Secret))
		{
			// Script routes
			protected.POST("/scripts", scriptHandler.Upload)
			protected.POST("/scripts/upload", scriptHandler.Upload)
			protected.GET("/scripts", scriptHandler.List)
			protected.GET("/scripts/:id/content", scriptHandler.GetContent)
			protected.GET("/scripts/:id", scriptHandler.Get)
			protected.PUT("/scripts/:id", scriptHandler.Update)
			protected.DELETE("/scripts/:id", scriptHandler.Delete)
			protected.POST("/scripts/batch-delete", scriptHandler.BatchDelete)

			// Execution routes
			protected.POST("/executions", executionHandler.Start)
			protected.POST("/executions/batch", executionHandler.BatchStart)
			protected.POST("/executions/batch-all", executionHandler.BatchExecuteAll)
			protected.GET("/executions", executionHandler.List)
			protected.GET("/executions/batch-all", executionHandler.BatchExecuteAll)
			protected.GET("/executions/:id", executionHandler.Get)
			protected.GET("/executions/:id/logs", executionHandler.GetLogs)
			protected.DELETE("/executions/:id", executionHandler.Delete)

			// Config routes
			protected.GET("/configs", configHandler.List)
			protected.GET("/configs/:key", configHandler.Get)
			protected.POST("/configs", configHandler.Set)
			protected.DELETE("/configs/:key", configHandler.Delete)
		}
	}
}

// healthCheck handles health check requests
func (s *Server) healthCheck(c *gin.Context) {
	// Check database connection
	if err := database.HealthCheck(c.Request.Context()); err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status":   "unhealthy",
			"database": "disconnected",
			"error":    err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":   "healthy",
		"database": "connected",
	})
}
