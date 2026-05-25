package handlers

import (
	"archive/zip"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/testplatform/backend/internal/executor"
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type SuiteHandler struct {
	suiteRepo     *repository.SuiteRepository
	scriptRepo    *repository.ScriptRepository
	taskRepo      *repository.TaskRepository
	executionRepo *repository.ExecutionRepository
	executor      *executor.Executor
}

func NewSuiteHandler(
	suiteRepo *repository.SuiteRepository,
	scriptRepo *repository.ScriptRepository,
	taskRepo *repository.TaskRepository,
	executionRepo *repository.ExecutionRepository,
	exec *executor.Executor,
) *SuiteHandler {
	return &SuiteHandler{
		suiteRepo:     suiteRepo,
		scriptRepo:    scriptRepo,
		taskRepo:      taskRepo,
		executionRepo: executionRepo,
		executor:      exec,
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

	// Read entire zip into memory
	zipContent, err := io.ReadAll(src)
	if err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read zip file"})
		return
	}

	// Open zip from memory
	reader, err := zip.NewReader(bytes.NewReader(zipContent), int64(len(zipContent)))
	if err != nil {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid zip file"})
		return
	}

	var testScripts []*models.TestScript
	var libScripts []*models.TestScript
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

		// Extract name from filename (remove extension)
		name := strings.TrimSuffix(filepath.Base(zipFile.Name), filepath.Ext(zipFile.Name))

		// Determine script type based on path
		scriptType := "test_case"
		filePath := zipFile.Name
		if isLibFile(zipFile.Name) {
			scriptType = "lib_file"
		}

		// Create script record with content stored in database
		script := &models.TestScript{
			UUID:        scriptUUID,
			Name:        name,
			Language:    language,
			FilePath:    filePath,
			ScriptType:  scriptType,
			FileSize:    int64(len(content)),
			FileHash:    fileHash,
			Content:     string(content),
			SuiteID:     &suite.ID,
			CreatedBy:   &userID,
		}

		if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
			continue
		}

		if scriptType == "test_case" {
			testScripts = append(testScripts, script)
		} else {
			libScripts = append(libScripts, script)
		}
	}

	if len(testScripts) == 0 {
		h.suiteRepo.Delete(c.Request.Context(), suite.ID)
		c.JSON(http.StatusBadRequest, gin.H{"error": "No valid test script files found in zip"})
		return
	}

	SuccessResponse(c, gin.H{
		"suite":        suite,
		"scripts":      testScripts,
		"lib_files":    len(libScripts),
		"total":        len(testScripts),
	})
}

// isLibFile checks if a file path indicates it's a library file
func isLibFile(path string) bool {
	// Normalize path separators
	normalizedPath := strings.ReplaceAll(path, "\\", "/")
	
	// Check if path contains /lib/ directory or starts with lib/
	if strings.Contains(normalizedPath, "/lib/") ||
		strings.HasPrefix(normalizedPath, "lib/") ||
		strings.HasPrefix(normalizedPath, "test/lib/") {
		return true
	}
	return false
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

// Delete handles deleting a suite
func (h *SuiteHandler) Delete(c *gin.Context) {
	id, err := strconvAtoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid suite ID"})
		return
	}

	// Delete all scripts in the suite from database
	if err := h.scriptRepo.DeleteBySuiteID(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete scripts"})
		return
	}

	// Delete suite record
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

	// Extract name from filename (remove extension)
	name := strings.TrimSuffix(file.Filename, filepath.Ext(file.Filename))

	// Create script record with content stored in database
	script := &models.TestScript{
		UUID:      scriptUUID,
		Name:      name,
		Language:  language,
		FileSize:  file.Size,
		FileHash:  fileHash,
		Content:   string(content),
		SuiteID:   &id,
		CreatedBy: &userIDInt,
	}

	if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
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
		f, err := zipWriter.Create(script.Name + "." + getExtByLanguage(script.Language))
		if err != nil {
			continue
		}
		// Write content from database
		f.Write([]byte(script.Content))
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

	// Get test case scripts (excluding lib files)
	testScripts, err := h.scriptRepo.ListBySuiteID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	if len(testScripts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Suite has no scripts to execute"})
		return
	}

	// Get all scripts including lib files for directory structure restoration
	allScripts, err := h.scriptRepo.ListAllBySuiteID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list all scripts"})
		return
	}

	// Separate lib files for passing to executor
	var libFiles []*models.TestScript
	for _, script := range allScripts {
		if script.ScriptType == "lib_file" {
			libFiles = append(libFiles, script)
		}
	}

	// Get user ID from context
	userID, _ := c.Get("user_id")
	userIDInt := userID.(int)

	// Create task record
	task := &models.TestTask{
		TaskType:    "suite_batch",
		SuiteID:     &suite.ID,
		SuiteName:   suite.Name,
		Status:      "pending",
		TotalCount:  len(testScripts),
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
	for _, script := range testScripts {
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

		go h.executor.ExecuteWithLibs(ctx, execution, script, libFiles)
	}

	// Update task status to running
	h.taskRepo.UpdateStatus(ctx, task.ID, "running")

	SuccessResponse(c, gin.H{
		"message":      fmt.Sprintf("Suite execution started with %d scripts", len(testScripts)),
		"suite_id":     suite.ID,
		"suite_name":   suite.Name,
		"script_count": len(testScripts),
		"lib_count":    len(libFiles),
		"task_id":      task.ID,
		"total":        len(testScripts),
		"succeeded":    0,
		"failed":       0,
	})
}

func strconvAtoi(s string) (int, error) {
	return strconv.Atoi(s)
}
