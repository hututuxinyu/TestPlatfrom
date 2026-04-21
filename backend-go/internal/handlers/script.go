package handlers

import (
	"archive/zip"
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
	"github.com/testplatform/backend/internal/config"
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type ScriptHandler struct {
	scriptRepo *repository.ScriptRepository
	config     *config.Config
}

func NewScriptHandler(scriptRepo *repository.ScriptRepository, cfg *config.Config) *ScriptHandler {
	return &ScriptHandler{
		scriptRepo: scriptRepo,
		config:     cfg,
	}
}

type UploadScriptRequest struct {
	Description string `form:"description"`
	Language    string `form:"language"`
	Tags        string `form:"tags"`
}

// Upload handles script file upload (supports single file and zip archive)
func (h *ScriptHandler) Upload(c *gin.Context) {
	var req UploadScriptRequest
	if err := c.ShouldBind(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
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

	// Check if it's a zip file
	if strings.HasSuffix(strings.ToLower(file.Filename), ".zip") {
		h.handleZipUpload(c, file, &req, userIDInt)
		return
	}

	// Handle single file upload
	h.uploadSingleFile(c, file, &req, userIDInt)
}

func (h *ScriptHandler) uploadSingleFile(c *gin.Context, file *multipart.FileHeader, req *UploadScriptRequest, userID int) {
	// Auto-detect language from file extension if not provided
	language := req.Language
	if language == "" {
		ext := strings.ToLower(filepath.Ext(file.Filename))
		extMap := map[string]string{".py": "python", ".sh": "shell", ".js": "javascript"}
		language = extMap[ext]
		if language == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file type"})
			return
		}
	} else {
		// Validate language
		validLanguages := map[string]bool{"python": true, "shell": true, "javascript": true}
		if !validLanguages[language] {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid language"})
			return
		}
	}

	// Open uploaded file
	src, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer src.Close()

	// Calculate file hash
	hash := sha256.New()
	if _, err := io.Copy(hash, src); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to calculate file hash"})
		return
	}
	fileHash := hex.EncodeToString(hash.Sum(nil))

	// Reset file pointer
	src.Seek(0, 0)

	// Create upload directory if not exists
	uploadDir := h.config.Executor.UploadDir
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create upload directory"})
		return
	}

	// Save file
	filename := fmt.Sprintf("%s_%s", fileHash[:16], file.Filename)
	filePath := filepath.Join(uploadDir, filename)
	if err := c.SaveUploadedFile(file, filePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Extract name from filename (remove extension)
	name := strings.TrimSuffix(file.Filename, filepath.Ext(file.Filename))

	// Create script record
	script := &models.TestScript{
		Name:        name,
		Description: req.Description,
		Language:    language,
		FilePath:    filePath,
		FileSize:    file.Size,
		FileHash:    fileHash,
		Tags:        req.Tags,
		CreatedBy:   &userID,
	}

	if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
		// Clean up file if database insert fails
		os.Remove(filePath)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create script record"})
		return
	}

	SuccessResponse(c, script)
}

func (h *ScriptHandler) handleZipUpload(c *gin.Context, file *multipart.FileHeader, req *UploadScriptRequest, userID int) {
	// Open uploaded file
	src, err := file.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer src.Close()

	// Create temp directory for extraction
	tempDir := filepath.Join(os.TempDir(), fmt.Sprintf("upload_%d", file.Size))
	if err := os.MkdirAll(tempDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp directory"})
		return
	}
	defer os.RemoveAll(tempDir)

	// Save zip file temporarily
	zipPath := filepath.Join(tempDir, file.Filename)
	if err := c.SaveUploadedFile(file, zipPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save zip file"})
		return
	}

	// Open and extract zip
	reader, err := zip.OpenReader(zipPath)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid zip file"})
		return
	}
	defer reader.Close()

	// Upload directory
	uploadDir := h.config.Executor.UploadDir
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create upload directory"})
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

		// Calculate hash
		hash := sha256.New()
		hash.Write(content)
		fileHash := hex.EncodeToString(hash.Sum(nil))

		// Save file
		filename := fmt.Sprintf("%s_%s", fileHash[:16], filepath.Base(zipFile.Name))
		filePath := filepath.Join(uploadDir, filename)
		if err := os.WriteFile(filePath, content, 0644); err != nil {
			continue
		}

		// Extract name from filename (remove extension)
		name := strings.TrimSuffix(filepath.Base(zipFile.Name), filepath.Ext(zipFile.Name))
		description := req.Description
		if description == "" {
			description = fmt.Sprintf("Extracted from %s", file.Filename)
		}

		// Create script record
		script := &models.TestScript{
			Name:        name,
			Description: description,
			Language:    language,
			FilePath:    filePath,
			FileSize:    int64(len(content)),
			FileHash:    fileHash,
			Tags:        req.Tags,
			CreatedBy:   &userID,
		}

		if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
			os.Remove(filePath)
			continue
		}

		scripts = append(scripts, script)
	}

	if len(scripts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No valid script files found in zip"})
		return
	}

	SuccessResponse(c, gin.H{
		"message":     fmt.Sprintf("Uploaded %d scripts from archive", len(scripts)),
		"scripts":    scripts,
		"total":      len(scripts),
	})
}

// List handles listing scripts
func (h *ScriptHandler) List(c *gin.Context) {
	language := c.Query("language")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	offset := (page - 1) * pageSize

	scripts, err := h.scriptRepo.List(c.Request.Context(), language, pageSize, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list scripts"})
		return
	}

	total, err := h.scriptRepo.Count(c.Request.Context(), language)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count scripts"})
		return
	}

	SuccessResponse(c, gin.H{
		"items": scripts,
		"total": total,
		"page":  page,
		"page_size": pageSize,
	})
}

// Get handles getting a script by ID
func (h *ScriptHandler) Get(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid script ID"})
		return
	}

	script, err := h.scriptRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Script not found"})
		return
	}

	SuccessResponse(c, script)
}

// Update handles updating a script
func (h *ScriptHandler) Update(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid script ID"})
		return
	}

	var req struct {
		Description string `json:"description"`
		Tags        string `json:"tags"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	script, err := h.scriptRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Script not found"})
		return
	}

	script.Description = req.Description
	script.Tags = req.Tags

	if err := h.scriptRepo.Update(c.Request.Context(), script); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update script"})
		return
	}

	SuccessResponse(c, script)
}

// Delete handles deleting a script
func (h *ScriptHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid script ID"})
		return
	}

	script, err := h.scriptRepo.GetByID(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Script not found"})
		return
	}

	if err := h.scriptRepo.Delete(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete script"})
		return
	}

	// Clean up file
	os.Remove(script.FilePath)

	SuccessResponse(c, gin.H{"message": "Script deleted successfully"})
}

type BatchDeleteRequest struct {
	ScriptIDs []int `json:"script_ids" binding:"required"`
}

// BatchDelete handles batch deletion of scripts
func (h *ScriptHandler) BatchDelete(c *gin.Context) {
	var req BatchDeleteRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if len(req.ScriptIDs) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "script_ids cannot be empty"})
		return
	}

	ctx := c.Request.Context()

	// Get scripts to delete files
	scripts, err := h.scriptRepo.ListByIDs(ctx, req.ScriptIDs)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get scripts"})
		return
	}

	// Delete from database
	if err := h.scriptRepo.DeleteByIDs(ctx, req.ScriptIDs); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete scripts"})
		return
	}

	// Clean up files
	for _, script := range scripts {
		os.Remove(script.FilePath)
	}

	SuccessResponse(c, gin.H{
		"message":       fmt.Sprintf("Deleted %d scripts successfully", len(req.ScriptIDs)),
		"deleted_count": len(req.ScriptIDs),
	})
}
