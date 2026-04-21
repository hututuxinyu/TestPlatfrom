## Why

当前批量上传脚本需要用户打包成 ZIP 文件后上传，但前端界面上传区域只提示"支持 .py, .sh, .js 文件"，没有明确说明 ZIP 批量上传的功能。用户可能不知道可以使用 ZIP 包批量上传脚本。

## What Changes

- 前端上传区域提示文字增加 ZIP 包上传说明
- 标签选择支持批量上传的所有脚本

## Capabilities

### New Capabilities

- `zip-batch-upload-ui`: 优化前端界面，清晰展示 ZIP 批量上传功能

## Impact

- 仅修改前端提示文字
- 后端已有完整 ZIP 上传实现，无需修改
