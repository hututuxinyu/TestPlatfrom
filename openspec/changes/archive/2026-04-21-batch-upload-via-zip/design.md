## Context

后端已有完整的 ZIP 批量上传实现（`handleZipUpload`），但前端界面没有明确提示这一功能。用户上传时只看到"支持 .py, .sh, .js 文件"，不知道可以打包成 ZIP 批量上传。

## Goals / Non-Goals

**Goals:**
- 更新前端上传区域提示文字，明确说明支持 ZIP 包批量上传

**Non-Goals:**
- 不修改后端 ZIP 上传逻辑（已有完整实现）
- 不添加新的 API

## Decisions

### 提示文字更新

**决策**: 将"支持 .py, .sh, .js 文件"改为"支持 .py, .sh, .js 文件及 ZIP 打包批量上传"

## Risks / Trade-offs

无风险，仅修改提示文字。
