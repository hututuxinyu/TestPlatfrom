package handlers

import (
	"context"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/testplatform/backend/internal/executor"
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type ExecutionHandler struct {
	executionRepo    *repository.ExecutionRepository
	executionLogRepo *repository.ExecutionLogRepository
	scriptRepo       *repository.ScriptRepository
	executor         *executor.Executor
}

func NewExecutionHandler(
	executionRepo *repository.ExecutionRepository,
	executionLogRepo *repository.ExecutionLogRepository,
	scriptRepo *repository.ScriptRepository,
	exec *executor.Executor,
) *ExecutionHandler {
	return &ExecutionHandler{
		executionRepo:    executionRepo,
		executionLogRepo: executionLogRepo,
		scriptRepo:       scriptRepo,
		executor:         exec,
	}
}

type StartExecutionRequest struct {
	ScriptID int `json:"script_id" binding:"required"`
}

type BatchStartExecutionRequest struct {
	ScriptIDs []int `json:"script_ids" binding:"required"`
}

// Start handles starting a test execution
func (h *ExecutionHandler) Start(c *gin.Context) {
	var req StartExecutionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Get script
	script, err := h.scriptRepo.GetByID(c.Request.Context(), req.ScriptID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Script not found"})
		return
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	// Create execution record
	execution := &models.TestExecution{
		ScriptID:   script.ID,
		ScriptName: script.Name,
		Status:     "pending",
		CreatedBy:  &userIDInt,
	}

	if err := h.executionRepo.Create(c.Request.Context(), execution); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create execution"})
		return
	}

	// Start execution in background
	go h.executor.Execute(context.Background(), execution, script.FilePath, script.Language)

	SuccessResponse(c, execution)
}

// BatchStart handles starting multiple test executions
func (h *ExecutionHandler) BatchStart(c *gin.Context) {
	var req BatchStartExecutionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if len(req.ScriptIDs) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "script_ids cannot be empty"})
		return
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	ctx := c.Request.Context()
	var executions []*models.TestExecution
	var failed []struct {
		ScriptID int    `json:"script_id"`
		Error   string `json:"error"`
	}

	for _, scriptID := range req.ScriptIDs {
		// Get script
		script, err := h.scriptRepo.GetByID(ctx, scriptID)
		if err != nil {
			failed = append(failed, struct {
				ScriptID int    `json:"script_id"`
				Error   string `json:"error"`
			}{ScriptID: scriptID, Error: "Script not found"})
			continue
		}

		// Create execution record
		execution := &models.TestExecution{
			ScriptID:   script.ID,
			ScriptName: script.Name,
			Status:     "pending",
			CreatedBy:  &userIDInt,
		}

		if err := h.executionRepo.Create(ctx, execution); err != nil {
			failed = append(failed, struct {
				ScriptID int    `json:"script_id"`
				Error   string `json:"error"`
			}{ScriptID: scriptID, Error: "Failed to create execution"})
			continue
		}

		// Start execution in background
		go h.executor.Execute(context.Background(), execution, script.FilePath, script.Language)
		executions = append(executions, execution)
	}

	response := gin.H{
		"total":     len(req.ScriptIDs),
		"succeeded": len(executions),
		"failed":    len(failed),
	}

	if len(executions) > 0 {
		response["executions"] = executions
	}
	if len(failed) > 0 {
		response["failed_items"] = failed
	}

	SuccessResponse(c, response)
}

// BatchExecuteAll handles executing all scripts
func (h *ExecutionHandler) BatchExecuteAll(c *gin.Context) {
	// Get all scripts
	scripts, err := h.scriptRepo.ListAll(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	if len(scripts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No scripts found"})
		return
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	ctx := c.Request.Context()
	var executions []*models.TestExecution
	var failed []struct {
		ScriptID int    `json:"script_id"`
		Error   string `json:"error"`
	}

	for _, script := range scripts {
		// Create execution record
		execution := &models.TestExecution{
			ScriptID:   script.ID,
			ScriptName: script.Name,
			Status:     "pending",
			CreatedBy:  &userIDInt,
		}

		if err := h.executionRepo.Create(ctx, execution); err != nil {
			failed = append(failed, struct {
				ScriptID int    `json:"script_id"`
				Error   string `json:"error"`
			}{ScriptID: script.ID, Error: "Failed to create execution"})
			continue
		}

		// Start execution in background
		go h.executor.Execute(context.Background(), execution, script.FilePath, script.Language)
		executions = append(executions, execution)
	}

	response := gin.H{
		"total":     len(scripts),
		"succeeded": len(executions),
		"failed":    len(failed),
	}

	if len(executions) > 0 {
		response["executions"] = executions
	}
	if len(failed) > 0 {
		response["failed_items"] = failed
	}

	SuccessResponse(c, response)
}

// List handles listing executions
func (h *ExecutionHandler) List(c *gin.Context) {
	scriptID, _ := strconv.Atoi(c.Query("script_id"))
	status := c.Query("status")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	offset := (page - 1) * pageSize

	executions, err := h.executionRepo.List(c.Request.Context(), scriptID, status, pageSize, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list executions"})
		return
	}

	total, err := h.executionRepo.Count(c.Request.Context(), scriptID, status)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count executions"})
		return
	}

	SuccessResponse(c, gin.H{
		"items":     executions,
		"total":     total,
		"page":      page,
		"page_size": pageSize,
	})
}

// Get handles getting an execution by ID
func (h *ExecutionHandler) Get(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid execution ID"})
		return
	}

	execution, err := h.executionRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Execution not found"})
		return
	}

	SuccessResponse(c, execution)
}

// GetLogs handles getting logs for an execution
func (h *ExecutionHandler) GetLogs(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid execution ID"})
		return
	}

	logs, err := h.executionLogRepo.GetByExecutionID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get logs"})
		return
	}

	SuccessResponse(c, gin.H{"logs": logs})
}

// Delete handles deleting an execution
func (h *ExecutionHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid execution ID"})
		return
	}

	if err := h.executionRepo.Delete(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete execution"})
		return
	}

	SuccessResponse(c, gin.H{"message": "Execution deleted successfully"})
}
