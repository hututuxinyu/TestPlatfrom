# 端到端测试评测平台 - 完整使用指南

## 🎯 功能概述

本平台实现了完整的测试脚本管理和执行流程：

1. **用户登录** - JWT 认证，安全可靠
2. **脚本管理** - 上传、查看、编辑、删除测试脚本
3. **执行管理** - 一键执行脚本，实时查看日志和结果
4. **结果收集** - 自动采集 stdout/stderr，记录执行状态

## 🚀 快速开始

### 1. 启动后端服务

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

### 3. 访问系统

- 前端地址：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 4. 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 📝 完整测试流程

### 步骤 1：登录系统

1. 打开浏览器访问 http://localhost:5173
2. 输入用户名 `admin` 和密码 `admin123`
3. 点击"登录"按钮

### 步骤 2：上传测试脚本

1. 进入"脚本管理"页面
2. 点击"上传脚本"按钮
3. 填写脚本信息：
   - **脚本名称**：IMSI 非空验证测试
   - **描述**：验证云手机的 IMSI 是否正确配置
   - **语言**：Python
   - **标签**：IMSI,功能测试
   - **文件**：选择项目根目录下的 `test_imsi_validation.py`
4. 点击"确定"完成上传

### 步骤 3：执行测试脚本

**方式一：从脚本管理页面执行**
1. 在脚本列表中找到刚上传的脚本
2. 点击"执行"按钮
3. 系统会自动跳转到执行管理页面

**方式二：从执行管理页面执行**
1. 进入"执行管理"页面
2. 在"快速执行脚本"下拉框中选择脚本
3. 系统自动创建执行任务并开始执行

### 步骤 4：查看执行结果

1. 在"执行管理"页面，可以看到：
   - 执行状态（等待中/执行中/已完成/失败/已停止）
   - 退出码（0 表示成功）
   - 执行时长
   - 开始和完成时间
2. 点击"日志"按钮查看详细执行日志
3. 日志包含：
   - 系统日志（开始执行、完成等）
   - 标准输出（脚本的 print 输出）
   - 错误输出（脚本的错误信息）

### 步骤 5：停止执行（可选）

如果脚本正在执行且需要停止：
1. 找到状态为"执行中"的任务
2. 点击"停止"按钮
3. 确认停止操作

## 📊 测试脚本示例

项目根目录下的 `test_imsi_validation.py` 是一个完整的测试脚本示例：

```python
#!/usr/bin/env python3
"""
IMSI 非空验证测试脚本
用于验证云手机的 IMSI 是否正确配置
"""

import sys
import time

def test_imsi_not_empty():
    """测试 IMSI 是否非空"""
    print("开始执行 IMSI 非空验证测试...")
    print("=" * 50)

    # 模拟获取 IMSI
    print("[步骤 1] 获取设备 IMSI...")
    time.sleep(1)
    imsi = "460001234567890"
    print(f"获取到 IMSI: {imsi}")

    # 验证 IMSI 非空
    print("[步骤 2] 验证 IMSI 是否非空...")
    time.sleep(1)
    if not imsi:
        print("❌ 测试失败: IMSI 为空")
        return False
    print("✓ IMSI 非空验证通过")

    # 验证 IMSI 格式
    print("[步骤 3] 验证 IMSI 格式...")
    time.sleep(1)
    if len(imsi) != 15:
        print(f"❌ 测试失败: IMSI 长度不正确")
        return False
    print("✓ IMSI 格式验证通过")

    print("=" * 50)
    print("✓ 测试通过: IMSI 验证成功")
    return True

if __name__ == "__main__":
    success = test_imsi_not_empty()
    sys.exit(0 if success else 1)
```

## 🔧 支持的脚本类型

- **Python** (.py) - 使用系统 Python 解释器执行
- **Shell** (.sh) - 使用 bash 执行
- **JavaScript** (.js) - 使用 Node.js 执行

## 📈 执行状态说明

| 状态 | 说明 |
|------|------|
| 等待中 (pending) | 任务已创建，等待执行 |
| 执行中 (running) | 脚本正在执行 |
| 已完成 (completed) | 脚本执行成功（退出码 0） |
| 失败 (failed) | 脚本执行失败（退出码非 0） |
| 已停止 (stopped) | 用户手动停止执行 |

## 🎨 界面功能

### 脚本管理页面
- ✅ 上传脚本（支持拖拽）
- ✅ 查看脚本内容
- ✅ 编辑脚本元数据
- ✅ 删除脚本
- ✅ 搜索和筛选
- ✅ 一键执行

### 执行管理页面
- ✅ 执行列表（自动刷新）
- ✅ 按脚本筛选
- ✅ 按状态筛选
- ✅ 查看执行日志
- ✅ 停止执行
- ✅ 快速执行

## 🔐 API 测试

### 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 上传脚本

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

### 创建执行任务

```bash
curl -X POST http://localhost:8000/api/v1/executions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script_id":1}'
```

### 查看执行日志

```bash
curl -X GET http://localhost:8000/api/v1/executions/1/logs \
  -H "Authorization: Bearer $TOKEN"
```

## 📦 数据库结构

### users 表
存储用户信息和认证数据

### test_scripts 表
存储测试脚本元数据和文件信息

### test_executions 表
存储执行记录和状态

### execution_logs 表
存储执行日志（stdout/stderr/system）

## 🎯 已实现功能

### M1 阶段 - 本地启动与最小闭环 ✅

- ✅ 平台与工程初始化
- ✅ 统一 API 错误码与响应结构
- ✅ 用户认证（JWT + bcrypt）
- ✅ 测试脚本管理（上传、CRUD、搜索）
- ✅ 测试脚本执行（异步执行、状态管理）
- ✅ 测试结果收集（日志采集、查询）

## 🚧 下一步开发

### 任务 6：测试报告生成
- [ ] 6.1 实现单执行报告组装逻辑
- [ ] 6.2 实现报告详情 API
- [ ] 6.3 实现前端报告展示页
- [ ] 6.4 实现 HTML/JSON 报告导出

### 任务 7：打样场景闭环
- [ ] 7.1 准备并上传打样脚本
- [ ] 7.2 打通"上传 -> 执行 -> 监控 -> 报告"全流程
- [ ] 7.3 形成打样验收记录与问题清单

## 💡 使用技巧

1. **自动刷新**：执行管理页面每 3 秒自动刷新，无需手动刷新
2. **快速执行**：在脚本管理页面可以直接点击"执行"按钮
3. **日志查看**：执行完成后可以随时查看完整日志
4. **状态筛选**：可以按状态筛选执行记录，快速找到失败的任务

## 🐛 故障排查

### 脚本执行失败
1. 检查脚本语法是否正确
2. 查看执行日志中的错误信息
3. 确认脚本文件权限

### 无法上传脚本
1. 检查文件格式（.py, .sh, .js）
2. 确认文件大小不超过 10MB
3. 确保文件是 UTF-8 编码

### 执行卡在"等待中"
1. 检查后端服务是否正常运行
2. 查看后端日志是否有错误
3. 尝试重启后端服务

## 📞 技术支持

如有问题，请查看：
- 后端日志：控制台输出
- 前端日志：浏览器开发者工具 Console
- API 文档：http://localhost:8000/docs
