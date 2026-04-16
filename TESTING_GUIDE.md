# 测试平台功能验证指南

## 已完成功能

### M1 阶段 - 本地启动与最小闭环

#### 1. 平台与工程初始化 ✅
- 前端工程（React 18 + Vite + Ant Design 5 + TypeScript）
- 后端工程（Python 3.9+ + FastAPI）
- SQLite 数据库初始化
- 统一 API 错误码与响应结构
- 本地一键启动脚本

#### 2. 用户认证 ✅
- 登录 API（JWT 令牌）
- 密码哈希验证（bcrypt）
- 鉴权中间件（Bearer Token）
- 登出 API
- 前端登录页与路由守卫

#### 3. 测试脚本管理 ✅
- 脚本上传（支持 .py, .sh, .js）
- 文件格式校验（最大 10MB）
- 脚本元数据 CRUD
- 列表查询、分页、搜索、筛选
- 前端脚本管理页面

## 快速开始

### 1. 启动后端

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 启动前端

```bash
cd frontend
npm run dev
```

### 3. 访问系统

- 前端地址：http://localhost:5173
- 后端地址：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 4. 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 功能测试

### 测试脚本管理

1. 登录系统
2. 进入"脚本管理"页面
3. 点击"上传脚本"按钮
4. 填写脚本信息：
   - 名称：IMSI 非空验证测试
   - 描述：验证云手机的 IMSI 是否正确配置
   - 语言：Python
   - 标签：IMSI,功能测试
   - 文件：选择 `test_imsi_validation.py`
5. 点击确定上传
6. 在列表中查看、编辑、删除脚本

### API 测试

#### 登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### 上传脚本
```bash
TOKEN="your_access_token"
curl -X POST http://localhost:8000/api/v1/scripts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_imsi_validation.py" \
  -F "name=IMSI非空验证测试" \
  -F "description=验证云手机的IMSI是否正确配置" \
  -F "language=python" \
  -F "tags=IMSI,功能测试"
```

#### 获取脚本列表
```bash
curl -X GET "http://localhost:8000/api/v1/scripts?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```

## 下一步开发

### 任务 4：测试脚本执行
- [ ] 4.1 实现执行任务创建 API
- [ ] 4.2 实现单脚本执行引擎主流程
- [ ] 4.3 实现执行完成回写
- [ ] 4.4 实现执行停止 API
- [ ] 4.5 实现前端执行触发与详情页

### 任务 5：测试结果收集
- [ ] 5.1 实现 stdout/stderr 实时采集
- [ ] 5.2 实现执行日志查询 API
- [ ] 5.3 实现执行摘要聚合
- [ ] 5.4 实现结果与日志关联

### 任务 6：测试报告生成
- [ ] 6.1 实现单执行报告组装
- [ ] 6.2 实现报告详情 API
- [ ] 6.3 实现前端报告展示页
- [ ] 6.4 实现 HTML/JSON 报告导出

## 技术栈

### 后端
- FastAPI 0.128.8
- Python 3.9+
- SQLite
- bcrypt（密码哈希）
- PyJWT（JWT 令牌）

### 前端
- React 19.2.4
- TypeScript 6.0.2
- Vite 8.0.4
- Ant Design 6.3.5
- React Router 7.14.1
- Axios 1.15.0

## 数据库结构

### users 表
- id, username, password_hash, created_at

### test_scripts 表
- id, name, description, file_path, file_size, file_hash
- language, tags, created_by, created_at, updated_at

### test_executions 表
- id, script_id, status, exit_code
- started_at, completed_at, duration_seconds
- created_by, created_at

### execution_logs 表
- id, execution_id, log_type, content, timestamp
