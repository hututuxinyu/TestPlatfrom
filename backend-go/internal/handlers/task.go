package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type TaskHandler struct {
	taskRepo       *repository.TaskRepository
	executionRepo  *repository.ExecutionRepository
	suiteRepo      *repository.SuiteRepository
}

func NewTaskHandler(
	taskRepo *repository.TaskRepository,
	executionRepo *repository.ExecutionRepository,
	suiteRepo *repository.SuiteRepository,
) *TaskHandler {
	return &TaskHandler{
		taskRepo:      taskRepo,
		executionRepo: executionRepo,
		suiteRepo:     suiteRepo,
	}
}

// List handles listing tasks with optional suite filter
func (h *TaskHandler) List(c *gin.Context) {
	suiteID, _ := strconv.Atoi(c.DefaultQuery("suite_id", "0"))
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	offset := (page - 1) * pageSize

	tasks, err := h.taskRepo.List(c.Request.Context(), suiteID, pageSize, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list tasks"})
		return
	}

	total, err := h.taskRepo.Count(c.Request.Context(), suiteID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count tasks"})
		return
	}

	SuccessResponse(c, gin.H{
		"items":     tasks,
		"total":     total,
		"page":      page,
		"page_size": pageSize,
	})
}

// Get handles getting a task by ID
func (h *TaskHandler) Get(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid task ID"})
		return
	}

	task, err := h.taskRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}

	SuccessResponse(c, task)
}

// ListExecutions handles listing executions for a task
func (h *TaskHandler) ListExecutions(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid task ID"})
		return
	}

	// Verify task exists
	_, err = h.taskRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}

	executions, err := h.executionRepo.ListByTaskID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list executions"})
		return
	}

	SuccessResponse(c, gin.H{
		"items": executions,
		"total": len(executions),
	})
}

// Stop handles stopping a task
func (h *TaskHandler) Stop(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid task ID"})
		return
	}

	task, err := h.taskRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}

	if task.Status != "pending" && task.Status != "running" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Task is not running"})
		return
	}

	if err := h.taskRepo.UpdateStatus(c.Request.Context(), id, "stopped"); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to stop task"})
		return
	}

	SuccessResponse(c, gin.H{"message": "Task stopped successfully"})
}

// Delete handles deleting a task
func (h *TaskHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid task ID"})
		return
	}

	_, err = h.taskRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}

	if err := h.taskRepo.Delete(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete task"})
		return
	}

	SuccessResponse(c, gin.H{"message": "Task deleted successfully"})
}

// CreateTaskRequest is used internally for creating tasks from suite execution
type CreateTaskRequest struct {
	SuiteID   *int      `json:"suite_id"`
	SuiteName string    `json:"suite_name"`
	Scripts   []*models.TestScript
	CreatedBy *int      `json:"created_by"`
}

// CreateTask creates a new task for suite batch execution
func (h *TaskHandler) CreateTask(req *CreateTaskRequest) (*models.TestTask, error) {
	task := &models.TestTask{
		SuiteID:     req.SuiteID,
		SuiteName:   req.SuiteName,
		Status:      "pending",
		TotalCount:  len(req.Scripts),
		CreatedBy:   req.CreatedBy,
	}

	if err := h.taskRepo.Create(nil, task); err != nil {
		return nil, err
	}

	return task, nil
}
