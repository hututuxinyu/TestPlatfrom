package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/testplatform/backend/internal/auth"
	"github.com/testplatform/backend/internal/config"
	"github.com/testplatform/backend/internal/repository"
)

type AuthHandler struct {
	userRepo *repository.UserRepository
	config   *config.Config
}

func NewAuthHandler(userRepo *repository.UserRepository, cfg *config.Config) *AuthHandler {
	return &AuthHandler{
		userRepo: userRepo,
		config:   cfg,
	}
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	Username    string `json:"username"`
}

// Login handles user login
func (h *AuthHandler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Get user by username
	user, err := h.userRepo.GetByUsername(c.Request.Context(), req.Username)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials", "debug": "user not found"})
		return
	}

	// Check if user is active
	if !user.IsActive {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User account is disabled"})
		return
	}

	// Verify password
	if !auth.CheckPassword(req.Password, user.Password) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials", "debug": "password mismatch"})
		return
	}

	// Generate JWT token
	token, err := auth.GenerateToken(user.ID, user.Username, h.config.JWT.Secret, h.config.JWT.Expiration)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"code": 0,
		"message": "success",
		"data": LoginResponse{
			AccessToken: token,
			TokenType:   "bearer",
			Username:    user.Username,
		},
	})
}

// Logout handles user logout (client-side token removal)
func (h *AuthHandler) Logout(c *gin.Context) {
	SuccessResponse(c, gin.H{"message": "Logged out successfully"})
}
