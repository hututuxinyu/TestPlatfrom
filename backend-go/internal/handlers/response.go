package handlers

import "github.com/gin-gonic/gin"

// SuccessResponse returns a standardized success response
func SuccessResponse(c *gin.Context, data interface{}) {
	c.JSON(200, gin.H{
		"code":    0,
		"message": "success",
		"data":    data,
	})
}

// ErrorResponse returns a standardized error response
func ErrorResponse(c *gin.Context, status int, message string) {
	c.JSON(status, gin.H{
		"code":    status,
		"message": message,
	})
}