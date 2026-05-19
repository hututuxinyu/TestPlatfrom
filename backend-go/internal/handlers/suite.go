package handlers

import (
	"archive/zip"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/testplatform/backend/internal/config"
	"github.com/testplatform/backend/internal/executor"
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type SuiteHandler struct {
	suiteRepo    *repository.SuiteRepository
	scriptRepo   *repository.ScriptRepository
	taskRepo     *repository.TaskRepository
	executionRepo *repository.ExecutionRepository
	executor     *executor.Executor
	config       *config.Config
}

func NewSuiteHandler(
	suiteRepo *repository.SuiteRepository,
	scriptRepo *repository.ScriptRepository,
	taskRepo *repository.TaskRepository,
	executionRepo *repository.ExecutionRepository,
	exec *executor.Executor,
	cfg *config.Config,
) *SuiteHandler {
	return &SuiteHandler{
		suiteRepo:    suiteRepo,
		scriptRepo:   scriptRepo,
		taskRepo:     taskRepo,
		executionRepo: executionRepo,
		executor:     exec,
		config:       cfg,
	}
}

// List handles listing all suites with summary
func (h *SuiteHandler) List(c *gin.Context) {
	summaries, err := h.suiteRepo.ListSummaries(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list suites"})
		return
	}

	SuccessResponse(c, gin.H{
		"items": summaries,
		"total": len(summaries),
	})
}

// Get handles getting a suite by ID
func (h *SuiteHandler) Get(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	suite, err := h.suiteRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Suite not found"})
		return
	}

	summary, _ := h.suiteRepo.GetSummary(c.Request.Context(), id)
	SuccessResponse(c, gin.H{
		"suite":   suite,
		"summary": summary,
	})
}

// Create handles creating a new suite with ZIP upload
func (h *SuiteHandler) Create(c *gin.Context) {
	name := c.PostForm("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Suite name is required"})
		return
	}

	// Check if name already exists
	_, err := h.suiteRepo.GetByName(c.Request.Context(), name)
	if err == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Suite name already exists"})
		return
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	// Create suite record first
	suite := &models.TestSuite{
		Name:      name,
		CreatedBy: &userIDInt,
	}

	if err := h.suiteRepo.Create(c.Request.Context(), suite); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create suite"})
		return
	}

	// Get uploaded file
	file, err := c.FormFile("file")
	if err != nil {
		// No file uploaded, just return the created suite
		SuccessResponse(c, suite)
		return
	}

	// Handle ZIP upload
	if strings.HasSuffix(strings.ToLower(file.Filename), ".zip") {
		h.handleZipUpload(c, suite, file, userIDInt)
		return
	}

	SuccessResponse(c, suite)
}

func (h *SuiteHandler) handleZipUpload(c *gin.Context, suite *models.TestSuite, file *multipart.FileHeader, userID int) {
	// Open uploaded file
	src, err := file.Open()
	if err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer src.Close()

	// Create temp directory for extraction
	tempDir := filepath.Join(os.TempDir(), fmt.Sprintf("suite_upload_%d", file.Size))
	if err := os.MkdirAll(tempDir, 0755); err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp directory"})
		return
	}
	defer os.RemoveAll(tempDir)

	// Save zip file temporarily
	zipPath := filepath.Join(tempDir, file.Filename)
	if err := c.SaveUploadedFile(file, zipPath); err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save zip file"})
		return
	}

	// Open and extract zip
	reader, err := zip.OpenReader(zipPath)
	if err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid zip file"})
		return
	}
	defer reader.Close()

	// Create suite directory
	suiteDir := filepath.Join(h.config.Executor.UploadDir, "suites", fmt.Sprintf("%d", suite.ID))
	if err := os.MkdirAll(suiteDir, 0755); err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create suite directory"})
		return
	}

	var scripts []*models.TestScript
	validExtensions := map[string]string{
		".py":  "python",
		".sh":  "shell",
		".js":  "javascript",
	}

	// Extract and process each file
	for _, zipFile := range reader.File {
		ext := strings.ToLower(filepath.Ext(zipFile.Name))
		language, ok := validExtensions[ext]
		if !ok {
			continue // Skip non-script files
		}

		// Skip directories
		if strings.HasSuffix(zipFile.Name, "/") {
			continue
		}

		// Open zip file
		rc, err := zipFile.Open()
		if err != nil {
			continue
		}

		// Read content
		content, err := io.ReadAll(rc)
		rc.Close()
		if err != nil {
			continue
		}

		// Calculate hash and generate UUID
		hash := sha256.New()
		hash.Write(content)
		fileHash := hex.EncodeToString(hash.Sum(nil))
		scriptUUID := uuid.New().String()

		// Save file
		filename := fmt.Sprintf("%s_%s", scriptUUID[:16], filepath.Base(zipFile.Name))
		filePath := filepath.Join(suiteDir, filename)
		if err := os.WriteFile(filePath, content, 0644); err != nil {
			continue
		}

		// Extract name from filename (remove extension)
		name := strings.TrimSuffix(filepath.Base(zipFile.Name), filepath.Ext(zipFile.Name))

		// Create script record
		script := &models.TestScript{
			UUID:     scriptUUID,
			Name:     name,
			Language: language,
			FilePath: filePath,
			FileSize: int64(len(content)),
			FileHash: fileHash,
			SuiteID:  &suite.ID,
			CreatedBy: &userID,
		}

		if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
			os.Remove(filePath)
			continue
		}

		scripts = append(scripts, script)
	}

	if len(scripts) == 0 {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		os.RemoveAll(suiteDir)
		c.JSON(http.StatusBadRequest, gin.H{"error": "No valid script files found in zip"})
		return
	}

	SuccessResponse(c, gin.H{
		"suite":   suite,
		"scripts": scripts,
		"total":   len(scripts),
	})
}

// Update handles updating a suite (rename)
func (h *SuiteHandler) Update(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	var req struct {
		Name string `json:"name" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Check if name already exists for another suite
	existing, err := h.suiteRepo.GetByName(c.Request.Context(), req.Name)
	if err == nil && existing.ID != id {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Suite name already exists"})
		return
	}

	suite, err := h.suiteRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Suite not found"})
		return
	}

	suite.Name = req.Name
	if err := h.suiteRepo.Update(c.Request.Context(), suite); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update suite"})
		return
	}

	SuccessResponse(c, suite)
}

// Delete handles deleting a suite (requires deleting scripts first)
func (h *SuiteHandler) Delete(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	// Delete all scripts in the suite first
	scripts, err := h.scriptRepo.ListBySuiteID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	// Delete script files
	for _, script := range scripts {
		os.Remove(script.FilePath)
	}

	// Delete scripts from database
	if err := h.scriptRepo.DeleteBySuiteID(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete scripts"})
		return
	}

	// Delete suite directory
	suiteDir := filepath.Join(h.config.Executor.UploadDir, "suites", fmt.Sprintf("%d", id))
	os.RemoveAll(suiteDir)

	// Delete suite
	if err := h.suiteRepo.Delete(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete suite"})
		return
	}

	SuccessResponse(c, gin.H{"message": "Suite deleted successfully"})
}

// ListScripts handles listing scripts in a suite
func (h *SuiteHandler) ListScripts(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	scripts, err := h.scriptRepo.ListBySuiteID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	SuccessResponse(c, gin.H{
		"items": scripts,
		"total": len(scripts),
	})
}

// UploadScript handles uploading a single script to a suite
func (h *SuiteHandler) UploadScript(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	// Check if suite exists
	_, err = h.suiteRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Suite not found"})
		return
	}

	// Get uploaded file
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File is required"})
		return
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	// Open uploaded file
	src, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer src.Close()

	// Read content
	content, err := io.ReadAll(src)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
		return
	}

	// Calculate hash and generate UUID
	hash := sha256.New()
	hash.Write(content)
	fileHash := hex.EncodeToString(hash.Sum(nil))
	scriptUUID := uuid.New().String()

	// Determine language from extension
	ext := strings.ToLower(filepath.Ext(file.Filename))
	extMap := map[string]string{".py": "python", ".sh": "shell", ".js": "javascript"}
	language := extMap[ext]
	if language == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file type"})
		return
	}

	// Create suite directory if not exists
	suiteDir := filepath.Join(h.config.Executor.UploadDir, "suites", fmt.Sprintf("%d", id))
	if err := os.MkdirAll(suiteDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create suite directory"})
		return
	}

	// Save file
	filename := fmt.Sprintf("%s_%s", scriptUUID[:16], file.Filename)
	filePath := filepath.Join(suiteDir, filename)
	if err := os.WriteFile(filePath, content, 0644); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Extract name from filename (remove extension)
	name := strings.TrimSuffix(file.Filename, filepath.Ext(file.Filename))

	// Create script record
	script := &models.TestScript{
		UUID:     scriptUUID,
		Name:     name,
		Language: language,
		FilePath: filePath,
		FileSize: file.Size,
		FileHash: fileHash,
		SuiteID:  &id,
		CreatedBy: &userIDInt,
	}

	if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
		os.Remove(filePath)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create script record"})
		return
	}

	SuccessResponse(c, script)
}

// Export handles exporting a suite as ZIP
func (h *SuiteHandler) Export(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	suite, err := h.suiteRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Suite not found"})
		return
	}

	scripts, err := h.scriptRepo.ListBySuiteID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	if len(scripts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Suite has no scripts to export"})
		return
	}

	// Create ZIP
	zipFilename := fmt.Sprintf("%s.zip", suite.Name)
	c.Header("Content-Type", "application/zip")
	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", zipFilename))

	zipWriter := zip.NewWriter(c.Writer)
	defer zipWriter.Close()

	for _, script := range scripts {
		content, err := os.ReadFile(script.FilePath)
		if err != nil {
			continue
		}

		f, err := zipWriter.Create(script.Name + "." + getExtByLanguage(script.Language))
		if err != nil {
			continue
		}

		f.Write(content)
	}
}

func getExtByLanguage(language string) string {
	switch language {
	case "python":
		return ".py"
	case "shell":
		return ".sh"
	case "javascript":
		return ".js"
	default:
		return ".txt"
	}
}

// ExecuteSuite handles batch execution of all scripts in a suite
func (h *SuiteHandler) ExecuteSuite(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	suite, err := h.suiteRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Suite not found"})
		return
	}

	scripts, err := h.scriptRepo.ListBySuiteID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	if len(scripts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Suite has no scripts to execute"})
		return
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	// Create task record
	task := &models.TestTask{
		SuiteID:     suite.ID,
		SuiteName:   suite.Name,
		Status:      "pending",
		TotalCount:  len(scripts),
		SuccessCount: 0,
		FailedCount:  0,
		CreatedBy:   &userIDInt,
	}

	if err := h.taskRepo.Create(c.Request.Context(), task); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create task"})
		return
	}

	// Create execution records and start executions
	ctx := context.Background()
	for _, script := range scripts {
		// Create execution record
		execution := &models.TestExecution{
			TaskID:     &task.ID,
			ScriptID:   script.ID,
			ScriptUUID: script.UUID,
			ScriptName: script.Name,
			Status:     "pending",
			CreatedBy:  &userIDInt,
		}

		if err := h.executionRepo.Create(ctx, execution); err != nil {
			continue
		}

		// Start execution in background
		go h.executor.Execute(ctx, execution, script.FilePath, script.Language)
	}

	// Update task status to running
	h.taskRepo.UpdateStatus(ctx, task.ID, "running")

	SuccessResponse(c, gin.H{
		"message":      fmt.Sprintf("Suite execution started with %d scripts", len(scripts)),
		"suite_id":     suite.ID,
		"suite_name":   suite.Name,
		"script_count": len(scripts),
		"task_id":      task.ID,
	})
}

func strconvAtoi(s string) (int, error) {
	return strconv.Atoi(s)
}
