package config

import (
	"fmt"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	JWT      JWTConfig
	Executor ExecutorConfig
	Logging  LoggingConfig
}

type ServerConfig struct {
	Port            int
	ReadTimeout     time.Duration
	WriteTimeout    time.Duration
	ShutdownTimeout time.Duration
}

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	Database string
	MaxConns int32
	MinConns int32
}

type JWTConfig struct {
	Secret     string
	Expiration time.Duration
}

type ExecutorConfig struct {
	MaxConcurrent int
	DefaultTimeout time.Duration
	UploadDir     string
	LogDir        string
}

type LoggingConfig struct {
	Level  string
	Format string
}

// Load loads configuration from environment variables and config file
func Load() (*Config, error) {
	viper.SetConfigName(".env")
	viper.SetConfigType("env")
	viper.AddConfigPath(".")
	viper.AutomaticEnv()

	// Set defaults
	setDefaults()

	// Read config file (optional)
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("failed to read config file: %w", err)
		}
	}

	cfg := &Config{
		Server: ServerConfig{
			Port:            viper.GetInt("SERVER_PORT"),
			ReadTimeout:     viper.GetDuration("SERVER_READ_TIMEOUT"),
			WriteTimeout:    viper.GetDuration("SERVER_WRITE_TIMEOUT"),
			ShutdownTimeout: viper.GetDuration("SERVER_SHUTDOWN_TIMEOUT"),
		},
		Database: DatabaseConfig{
			Host:     viper.GetString("DB_HOST"),
			Port:     viper.GetInt("DB_PORT"),
			User:     viper.GetString("DB_USER"),
			Password: viper.GetString("DB_PASSWORD"),
			Database: viper.GetString("DB_NAME"),
			MaxConns: int32(viper.GetInt("DB_MAX_CONNS")),
			MinConns: int32(viper.GetInt("DB_MIN_CONNS")),
		},
		JWT: JWTConfig{
			Secret:     viper.GetString("JWT_SECRET"),
			Expiration: viper.GetDuration("JWT_EXPIRATION"),
		},
		Executor: ExecutorConfig{
			MaxConcurrent:  viper.GetInt("MAX_CONCURRENT_EXECUTIONS"),
			DefaultTimeout: viper.GetDuration("DEFAULT_TIMEOUT"),
			UploadDir:      viper.GetString("UPLOAD_DIR"),
			LogDir:         viper.GetString("LOG_DIR"),
		},
		Logging: LoggingConfig{
			Level:  viper.GetString("LOG_LEVEL"),
			Format: viper.GetString("LOG_FORMAT"),
		},
	}

	return cfg, nil
}

func setDefaults() {
	// Server defaults
	viper.SetDefault("SERVER_PORT", 8011)
	viper.SetDefault("SERVER_READ_TIMEOUT", 30*time.Second)
	viper.SetDefault("SERVER_WRITE_TIMEOUT", 30*time.Second)
	viper.SetDefault("SERVER_SHUTDOWN_TIMEOUT", 10*time.Second)

	// Database defaults
	viper.SetDefault("DB_HOST", "localhost")
	viper.SetDefault("DB_PORT", 3306)
	viper.SetDefault("DB_USER", "root")
	viper.SetDefault("DB_PASSWORD", "")
	viper.SetDefault("DB_NAME", "testplatform")
	viper.SetDefault("DB_MAX_CONNS", 25)
	viper.SetDefault("DB_MIN_CONNS", 5)

	// JWT defaults
	viper.SetDefault("JWT_SECRET", "change-this-secret-in-production")
	viper.SetDefault("JWT_EXPIRATION", 24*time.Hour)

	// Executor defaults
	viper.SetDefault("MAX_CONCURRENT_EXECUTIONS", 100)
	viper.SetDefault("DEFAULT_TIMEOUT", 3600*time.Second)
	viper.SetDefault("UPLOAD_DIR", "data/uploads")
	viper.SetDefault("LOG_DIR", "logs")

	// Logging defaults
	viper.SetDefault("LOG_LEVEL", "info")
	viper.SetDefault("LOG_FORMAT", "json")
}
