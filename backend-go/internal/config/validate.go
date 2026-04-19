package config

import (
	"fmt"
	"os"
)

// Validate validates the configuration
func (c *Config) Validate() error {
	// Validate server config
	if c.Server.Port < 1 || c.Server.Port > 65535 {
		return fmt.Errorf("invalid server port: %d", c.Server.Port)
	}

	// Validate database config
	if c.Database.Host == "" {
		return fmt.Errorf("database host is required")
	}
	if c.Database.Port < 1 || c.Database.Port > 65535 {
		return fmt.Errorf("invalid database port: %d", c.Database.Port)
	}
	if c.Database.User == "" {
		return fmt.Errorf("database user is required")
	}
	if c.Database.Database == "" {
		return fmt.Errorf("database name is required")
	}
	if c.Database.MaxConns < 1 {
		return fmt.Errorf("database max connections must be at least 1")
	}
	if c.Database.MinConns < 0 {
		return fmt.Errorf("database min connections cannot be negative")
	}
	if c.Database.MinConns > c.Database.MaxConns {
		return fmt.Errorf("database min connections cannot exceed max connections")
	}

	// Validate JWT config
	if c.JWT.Secret == "" || c.JWT.Secret == "change-this-secret-in-production" {
		return fmt.Errorf("JWT secret must be set to a secure value")
	}
	if c.JWT.Expiration <= 0 {
		return fmt.Errorf("JWT expiration must be positive")
	}

	// Validate executor config
	if c.Executor.MaxConcurrent < 1 {
		return fmt.Errorf("max concurrent executions must be at least 1")
	}
	if c.Executor.DefaultTimeout <= 0 {
		return fmt.Errorf("default timeout must be positive")
	}
	if c.Executor.UploadDir == "" {
		return fmt.Errorf("upload directory is required")
	}
	if c.Executor.LogDir == "" {
		return fmt.Errorf("log directory is required")
	}

	// Ensure directories exist
	if err := os.MkdirAll(c.Executor.UploadDir, 0755); err != nil {
		return fmt.Errorf("failed to create upload directory: %w", err)
	}
	if err := os.MkdirAll(c.Executor.LogDir, 0755); err != nil {
		return fmt.Errorf("failed to create log directory: %w", err)
	}

	// Validate logging config
	validLevels := map[string]bool{"debug": true, "info": true, "warn": true, "error": true}
	if !validLevels[c.Logging.Level] {
		return fmt.Errorf("invalid log level: %s (must be debug, info, warn, or error)", c.Logging.Level)
	}
	validFormats := map[string]bool{"json": true, "text": true}
	if !validFormats[c.Logging.Format] {
		return fmt.Errorf("invalid log format: %s (must be json or text)", c.Logging.Format)
	}

	return nil
}
