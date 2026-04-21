## Why

当前平台缺少批量操作能力，用户需要逐个执行脚本和删除记录，效率低下。批量执行可以提升测试效率，批量删除需要明确确认以防止误操作。

## What Changes

1. **一键批量执行所有脚本**: 在脚本管理页面添加"批量执行"按钮，一键触发所有已上传脚本的执行
2. **脚本管理批量删除**: 支持多选脚本进行批量删除，删除前必须手动输入 "delete" 进行二次确认
3. **执行管理单记录删除确认**: 执行记录删除时弹出确认对话框，用户需点击确认才能删除

## Capabilities

### New Capabilities
- `batch-script-execution`: 支持一键执行所有已上传的测试脚本
- `script-batch-delete`: 支持批量选择并删除脚本，删除前需手动输入 "delete" 确认
- `execution-record-delete-confirmation`: 执行记录删除时显示确认对话框

### Modified Capabilities
<!-- 无现有 spec，当前为全新功能 -->

## Impact

- **前端**: 脚本管理页面增加批量操作 UI，执行管理页面增加删除确认
- **后端**: 新增批量执行 API，删除操作增加二次确认机制
