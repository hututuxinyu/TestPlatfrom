package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/sirupsen/logrus"
	"github.com/testplatform/backend/internal/config"
	"github.com/testplatform/backend/internal/database"
	"github.com/testplatform/backend/internal/executor"
	"github.com/testplatform/backend/internal/middleware"
	"github.com/testplatform/backend/internal/repository"
	"github.com/testplatform/backend/internal/server"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to load config: %v\n", err)
		os.Exit(1)
	}

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		fmt.Fprintf(os.Stderr, "Invalid configuration: %v\n", err)
		os.Exit(1)
	}

	// Setup logger
	logger := logrus.New()
	if cfg.Logging.Format == "json" {
		logger.SetFormatter(&logrus.JSONFormatter{})
	} else {
		logger.SetFormatter(&logrus.TextFormatter{})
	}
	level, _ := logrus.ParseLevel(cfg.Logging.Level)
	logger.SetLevel(level)
	middleware.SetLogger(logger)

	// Initialize database
	dbConfig := database.Config{
		Host:     cfg.Database.Host,
		Port:     cfg.Database.Port,
		User:     cfg.Database.User,
		Password: cfg.Database.Password,
		Database: cfg.Database.Database,
		MaxConns: cfg.Database.MaxConns,
		MinConns: cfg.Database.MinConns,
	}

	if err := database.InitDB(dbConfig); err != nil {
		logger.Fatalf("Failed to initialize database: %v", err)
	}
	defer database.Close()

	logger.Info("Database connection established")

	// Run migrations
	databaseURL := fmt.Sprintf("mysql://%s:%s@tcp(%s:%d)/%s",
		cfg.Database.User, cfg.Database.Password, cfg.Database.Host, cfg.Database.Port, cfg.Database.Database)
	if err := database.RunMigrations(databaseURL); err != nil {
		logger.Fatalf("Failed to run migrations: %v", err)
	}

	logger.Info("Database migrations completed")

	// Get database connection
	db := database.GetDB()

	// Initialize repositories
	executionRepo := repository.NewExecutionRepository(db)
	executionLogRepo := repository.NewExecutionLogRepository(db)
	configRepo := repository.NewConfigRepository(db)

	// Initialize executor
	exec := executor.NewExecutor(
		executionRepo,
		executionLogRepo,
		configRepo,
		cfg.Executor.MaxConcurrent,
		cfg.Executor.LogDir,
		cfg.Executor.DefaultTimeout,
	)

	// Create and setup server
	srv := server.NewServer(cfg)
	srv.SetupRoutes(db, exec)

	// Start server in goroutine
	go func() {
		if err := srv.Start(); err != nil {
			logger.Fatalf("Server failed: %v", err)
		}
	}()

	logger.Infof("Server started on port %d", cfg.Server.Port)

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// Graceful shutdown
	ctx := context.Background()
	if err := srv.Shutdown(ctx); err != nil {
		logger.Errorf("Server shutdown error: %v", err)
	}

	logger.Info("Server stopped")
}
