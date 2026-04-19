package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message,omitempty"`
}

// Recovery middleware recovers from panics and returns 500
func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				log.WithField("error", err).Error("Panic recovered")
				c.JSON(http.StatusInternalServerError, ErrorResponse{
					Error:   "Internal Server Error",
					Message: "An unexpected error occurred",
				})
				c.Abort()
			}
		}()
		c.Next()
	}
}

// ErrorHandler middleware handles errors from handlers
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		if len(c.Errors) > 0 {
			err := c.Errors.Last()
			log.WithField("error", err.Error()).Error("Request error")

			// Return error response if not already sent
			if !c.Writer.Written() {
				c.JSON(http.StatusInternalServerError, ErrorResponse{
					Error:   "Internal Server Error",
					Message: err.Error(),
				})
			}
		}
	}
}
