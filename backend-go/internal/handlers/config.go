package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type ConfigHandler struct {
	configRepo *repository.ConfigRepository
}

func NewConfigHandler(configRepo *repository.ConfigRepository) *ConfigHandler {
	return &ConfigHandler{
		configRepo: configRepo,
	}
}

type SetConfigRequest struct {
	Key         string `json:"key" binding:"required"`
	Value       string `json:"value" binding:"required"`
	Description string `json:"description"`
}

// List handles listing all configs
func (h *ConfigHandler) List(c *gin.Context) {
	configs, err := h.configRepo.List(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list configs"})
		return
	}

	SuccessResponse(c, gin.H{"items": configs})
}

// Get handles getting a config by key
func (h *ConfigHandler) Get(c *gin.Context) {
	key := c.Param("key")

	config, err := h.configRepo.Get(c.Request.Context(), key)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Config not found"})
		return
	}

	SuccessResponse(c, config)
}

// Set handles creating or updating a config
func (h *ConfigHandler) Set(c *gin.Context) {
	var req SetConfigRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	config := &models.GlobalConfig{
		Key:         req.Key,
		Value:       req.Value,
		Description: req.Description,
	}

	if err := h.configRepo.Set(c.Request.Context(), config); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to set config"})
		return
	}

	SuccessResponse(c, config)
}

// Delete handles deleting a config
func (h *ConfigHandler) Delete(c *gin.Context) {
	key := c.Param("key")

	if err := h.configRepo.Delete(c.Request.Context(), key); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete config"})
		return
	}

	SuccessResponse(c, gin.H{"message": "Config deleted successfully"})
}
