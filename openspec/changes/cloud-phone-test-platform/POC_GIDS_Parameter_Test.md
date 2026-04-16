# 打样场景设计: GIDS宫格登录参数异常测试

## 📋 用例信息

**用例编号**: TC_SBG_Func_GIDS_001_004
**用例名称**: 宫格登录身份验证并打开浏览器接口验证-参数值异常测试
**测试类型**: API参数验证测试
**目标服务**: GIDS

## 🎯 测试目标

验证GIDS宫格登录接口 `gridLoginAuthOpenBrowser` 在不同参数组合下的行为:
1. 包含所有参数时的正确行为
2. 仅包含必选参数时的行为
3. 必选参数+1个可选参数时的行为

## 📝 业务侧用例数据

```json
{
  "TestCase_Number": "TC_SBG_Func_GIDS_001_004",
  "TestCase_Name": "宫格登录身份验证并打开浏览器接口验证-参数值异常测试",
  "TestCase_Pretreatment Condition": "1、SBG网元部署成功；\n2、已加载IMEI白名单文件；",
  "TestCase_Test Steps": "1、构造POST HTTP请求：/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser，包含所有参数...其中请求的IMEI在白名单列表中。\n2、构造POST HTTP请求：仅包含必选参数；\n3、构造POST HTTP请求：仅包含必选参数+1个可选参数；",
  "TestCase_Expected Result": "1、产品响应失败，响应码为XX，errocode提示必选信元缺失。"
}
```

## 🐍 Python测试脚本

**脚本文件**: `TC_SBG_Func_GIDS_001_004.py`

**参数配置**:
```python
# ========== 参数配置 ==========
GIDS_ADDR = "http://192.168.1.100:9090"
DEVICE_WHITE_IMEI = "6258412454025411"

# 全量测试数据
TEST_DATA_FULL = {
    "imsi": "68510155565211",
    "imei": "6258412454025411",
    "manufacturer": "xxx 厂商",
    "model": "xx 机型",
    "appType": 1,
    "extendModel": "default",
    "country": "default",
    "platform": "default",
    "width": 240,
    "height": 320,
    "mcc": "460",
    "mnc": "00x",
    "lac": "100",
    "ci": "5.21",
    "rxlev": -72,
    "totalKb": 1424122,
    "freeKb": 1424122,
    "clientLanguage": "en",
    "deviceType": 1000
}

# 必选参数(根据接口文档)
REQUIRED_PARAMS = ["imsi", "imei"]
```

**测试步骤**:
```python
def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║    宫格登录身份验证并打开浏览器接口验证-参数值异常测试          ║
║    TC_SBG_Func_GIDS_001_004                                       ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # 测试结果汇总
    test_results = []

    # 步骤1: 全量参数
    result1 = test_full_params()
    test_results.append(("步骤1: 全量参数", result1))

    # 步骤2: 仅必选参数
    result2 = test_required_only()
    test_results.append(("步骤2: 仅必选参数", result2))

    # 步骤3: 必选+1可选
    result3 = test_required_plus_one()
    test_results.append(("步骤3: 必选+1可选", result3))

    # 输出汇总
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    return 0 if all_passed else 1
```

## 📊 数据库操作

### 1. 上传Python脚本

```sql
INSERT INTO test_scripts (
    id,
    name,
    script_file,
    script_type,
    status,
    created_at,
    updated_at
) VALUES (
    'script_001',  -- UUID
    'GIDS宫格登录参数异常测试',
    '/data/scripts/TC_SBG_Func_GIDS_001_004.py',
    'api',
    'active',
    NOW(),
    NOW()
);
```

### 2. 创建测试集(可选)

```sql
INSERT INTO test_suites (
    id,
    name,
    description,
    script_ids,
    created_by,
    created_at
) VALUES (
    'suite_001',
    'GIDS API参数验证测试集',
    '包含GIDS API参数相关的验证测试',
    'script_001,script_002,script_003',  -- 逗号分隔的脚本ID
    'tester1',
    NOW()
);
```

### 3. 执行测试脚本

```python
# 后端执行引擎伪代码
def execute_script(script_id, executor):
    # 1. 从数据库加载脚本信息
    script = db.query("SELECT * FROM test_scripts WHERE id = ?", script_id)

    # 2. 读取脚本文件
    script_path = script['script_file']
    with open(script_path, 'rb') as f:
        script_files = {'file': (script_path, f)}

    # 3. 执行Python脚本
    import subprocess
    result = subprocess.run(
        ['python3', script_path],
        capture_output=True,
        text=True,
        timeout=300  # 5分钟超时
    )

    # 4. 收集执行日志
    logs = result.stdout + '\n' + result.stderr

    # 5. 记录执行结果
    execution_id = generate_uuid()
    db.execute("""
        INSERT INTO test_executions (
            id,
            script_id,
            status,
            exit_code,
            logs,
            logs_file,
            started_at,
            finished_at,
            duration,
            error_message,
            executor,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
    """, (
        execution_id,
        script_id,
        'passed' if result.returncode == 0 else 'failed',
        result.returncode,
        logs,
        f'/data/logs/execution_{execution_id}.log',
        NOW(),
        NOW(),
        2,  # 假设耗时2秒
        None,
        executor
    ))

    return execution_id
```

### 4. 查询执行记录

```sql
-- 查询最新的执行记录
SELECT
    e.id,
    s.name AS script_name,
    e.status,
    e.exit_code,
    e.duration,
    e.started_at,
    e.finished_at,
    e.executor
FROM test_executions e
JOIN test_scripts s ON e.script_id = s.id
WHERE e.id = ?
ORDER BY e.created_at DESC
LIMIT 10;
```

## 📁 文件存储结构

```
/platform_data/
├── scripts/                           # Python脚本存储
│   └── TC_SBG_Func_GIDS_001_004.py
├── logs/                              # 执行日志存储
│   ├── execution_001.log
│   ├── execution_002.log
│   └── ...
├── archives/                          # 测试集归档存储
│   ├── suite_001_archive_20250415.zip
│   ├── suite_002_archive_20250416.zip
│   └── ...
└── screenshots/                       # E2E测试截图(如需要)
    └── ...
```

## 🔄 执行流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 测试人员编写Python脚本                                    │
│    编写: TC_SBG_Func_GIDS_001_004.py                        │
│    配置: GIDS_ADDR, IMEI等参数                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 测试人员上传脚本到平台                                    │
│    通过Web界面上传: TC_SBG_Func_GIDS_001_004.py           │
│    数据库记录: INSERT INTO test_scripts                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 触发测试执行                                            │
│    前端调用: POST /api/v1/executions                       │
│    后端执行: python3 script.py                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 收集执行结果                                            │
│    日志: stdout/stderr收集到logs字段                       │
│    退出码: exit_code (0=成功)                               │
│    文件: 完整日志存储到logs_file                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 更新数据库记录                                           │
│    INSERT INTO test_executions                              │
│    记录: status, exit_code, logs, duration, etc.           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 前端展示执行结果                                        │
│    实时监控: WebSocket推送进度                             │
│    测试报告: 展示详细日志和结果                            │
└─────────────────────────────────────────────────────────────┘
```

## 📈 预期输出示例

**控制台输出**:
```
╔══════════════════════════════════════════════════════════════════╗
║    宫格登录身份验证并打开浏览器接口验证-参数值异常测试          ║
║    TC_SBG_Func_GIDS_001_004                                       ║
╚══════════════════════════════════════════════════════════════════╝

[INFO] GIDS地址: http://192.168.1.100:9090
[INFO] 白名单IMEI: 6258412454025411

[INFO] ========== 测试步骤1: 全量参数请求 ==========
[INFO] 接口: /app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser
[INFO] 请求参数数量: 18
[INFO] IMEI是否在白名单: True
[INFO] 请求参数: {
  "imsi": "68510155565211",
  "imei": "6258412454025411",
  ...
}
[INFO] 响应状态码: 200
[INFO] 响应数据: {"code": 200, "data": {"token": "..."}}
[SUCCESS] 全量参数请求成功

[INFO] ========== 测试步骤2: 仅必选参数请求 ==========
[INFO] 必选参数: ['imsi', 'imei']
[INFO] 请求参数: {"imsi": "68510155565211", "imei": "6258412454025411"}
[INFO] 响应状态码: 400
[INFO] 响应数据: {"code": 200, "data": {...}}
[SUCCESS] 仅必选参数请求成功

[INFO] ========== 测试步骤3: 必选参数+1可选参数请求 ==========
[INFO] 必选参数: ['imsi', 'imei']
[INFO] 额外可选参数: appType
[INFO] 请求参数: {"imsi": "68510155565211", "imei": "6258412454025411", "appType": 1}
[INFO] 响应状态码: 200
[INFO] 响应数据: {"code": 200, "data": {"token": "..."}}
[SUCCESS] 必选参数+1可选参数请求成功

[INFO] ========== 测试结果汇总 ==========
[PASS] 步骤1: 全量参数
[PASS] 步骤2: 仅必选参数
[PASS] 步骤3: 必选+1可选

[SUCCESS] ========== 测试完成 ==========
```

## ✅ 打样验证清单

**平台能力验证**:
- [ ] 能否上传Python脚本 `TC_SBG_Func_GIDS_001_004.py`
- [ ] 能否成功执行Python脚本
- [ ] 能否正确收集stdout/stderr日志
- [ ] 能否根据exit_code判断测试结果
- [ ] 能否将执行记录存储到PostgreSQL
- [ ] 能否前端展示执行日志
- [ ] 能否前端展示测试报告

**打样成功标准**:
1. ✅ Python脚本上传成功
2. ✅ Python脚本执行成功,返回正确的exit_code
3. ✅ 日志正确收集并存储到日志字段
4. ✅ 数据库正确记录执行状态和结果
5. ✅ 前端能查看完整的执行日志
6. ✅ 前端能查看测试报告
7. ✅ 整个端到端流程跑通

## 🚀 后续扩展路径

从这个打样用例出发,可以扩展:

1. **更多API测试**: GIDS其他接口(API上传下载、授权等)
2. **BrowserGateway测试**: 预打开浏览器、删除用户数据等
3. **MediaCache测试**: 视频流获取、媒体控制等
4. **E2E测试**: 集成mobile项目进行端到端测试
5. **参数化测试**: 使用不同参数组合运行同一脚本
6. **测试集归档**: 将多个测试脚本组织成测试集并归档