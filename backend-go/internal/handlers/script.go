package handlers

import (
	"archive/zip"
	"bytes"
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
	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
)

type ScriptHandler struct {
	scriptRepo *repository.ScriptRepository
}

func NewScriptHandler(scriptRepo *repository.ScriptRepository) *ScriptHandler {
	return &ScriptHandler{
		scriptRepo: scriptRepo,
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

	// Read file content into memory
	content, err := io.ReadAll(src)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file content"})
		return
	}

	// Calculate file hash
	hash := sha256.New()
	hash.Write(content)
	fileHash := hex.EncodeToString(hash.Sum(nil))

	// Extract name from filename (remove extension)
	name := strings.TrimSuffix(file.Filename, filepath.Ext(file.Filename))

	// Create script record
	script := &models.TestScript{
		Name:        name,
		Description: req.Description,
		Language:    language,
		FileSize:    file.Size,
		FileHash:    fileHash,
		Content:     string(content),
		Tags:        req.Tags,
		CreatedBy:   &userID,
	}

	if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
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

	// Read entire zip into memory
	zipContent, err := io.ReadAll(src)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read zip file"})
		return
	}

	// Open zip from memory
	reader, err := zip.NewReader(bytes.NewReader(zipContent), int64(len(zipContent)))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid zip file"})
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

		// Extract name from filename (remove extension)
		name := strings.TrimSuffix(filepath.Base(zipFile.Name), filepath.Ext(zipFile.Name))
		description := req.Description
		if description == "" {
			description = fmt.Sprintf("Extracted from %s", file.Filename)
		}

		// Create script record with content stored in database
		script := &models.TestScript{
			Name:        name,
			Description: description,
			Language:    language,
			FileSize:    int64(len(content)),
			FileHash:    fileHash,
			Content:     string(content),
			Tags:        req.Tags,
			CreatedBy:   &userID,
		}

		if err := h.scriptRepo.Create(c.Request.Context(), script); err != nil {
			continue
		}

		scripts = append(scripts, script)
	}

	if len(scripts) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No valid script files found in zip"})
		return
	}

	SuccessResponse(c, gin.H{
		"message":  fmt.Sprintf("Uploaded %d scripts from archive", len(scripts)),
		"scripts": scripts,
		"total":   len(scripts),
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

func (h *ScriptHandler) GetContent(c *gin.Context) {
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

	SuccessResponse(c, gin.H{"content": script.Content})
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

func (h *ScriptHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid script ID"})
		return
	}

	if err := h.scriptRepo.Delete(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete script"})
		return
	}

	SuccessResponse(c, gin.H{"message": "Script deleted successfully"})
}

type BatchDeleteRequest struct {
	ScriptIDs []int `json:"script_ids" binding:"required"`
}

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

	if err := h.scriptRepo.DeleteByIDs(ctx, req.ScriptIDs); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete scripts"})
		return
	}

	SuccessResponse(c, gin.H{
		"message":       fmt.Sprintf("Deleted %d scripts successfully", len(req.ScriptIDs)),
		"deleted_count": len(req.ScriptIDs),
	})
}
