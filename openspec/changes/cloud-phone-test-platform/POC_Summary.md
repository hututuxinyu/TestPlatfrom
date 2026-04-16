# 打样场景总结文档

## 📁 文档位置

所有打样相关文档位于:
```
D:\Code\云手机\SBG\openspec\changes\cloud-phone-test-platform\
```

**核心文档**:
1. **TC_SBG_Func_GIDS_001_004.py** - API参数异常测试脚本(可直接运行)
2. **TC_SBG_Func_GIDS_001_005.py** - API数据类型异常测试脚本(可直接运行)
3. **POC_GIDS_Parameter_Test.md** - 打样场景详细设计
4. **API_Design.md** - 平台API接口定义
5. **proposal.md** - 需求提案文档
6. **design.md** - 系统设计文档

## 🎯 打样用例列表

**打样用例1**: TC_SBG_Func_GIDS_001_004
**用例名称**: 宫格登录身份验证并打开浏览器接口验证-参数值异常测试
**测试类型**: API参数验证测试
**测试目标**: 验证GIDS宫格登录接口在不同参数组合下的行为
**测试步骤**:
1. 包含所有参数的请求
2. 仅包含必选参数的请求
3. 必选参数+1个可选参数的请求

**打样用例2**: TC_SBG_Func_GIDS_001_005
**用例名称**: 宫格登录身份验证并打开浏览器接口验证-数据类型异常测试
**测试类型**: API数据类型验证测试
**测试目标**: 验证GIDS宫格登录接口对数据类型的严格性
**测试步骤**:
1. 正常数据类型(基准测试)
2. IMSI数据类型异常(String→Integer)
3. DeviceType数据类型异常(Integer→String)
4. 混合数据类型异常
5. 额外字段数据类型测试

## 📊 数据库表结构 (轻量级)

使用 **PostgreSQL** 数据库,6个核心表:

```sql
-- 1. 测试脚本表
CREATE TABLE test_scripts (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    script_file VARCHAR(500) NOT NULL,
    script_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 2. 测试执行记录表
CREATE TABLE test_executions (
    id VARCHAR(36) PRIMARY KEY,
    script_id VARCHAR(36) NOT NULL,
    status VARCHAR(20) NOT NULL,
    exit_code INT,
    logs TEXT,
    logs_file VARCHAR(500),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration INT,
    error_message TEXT,
    executor VARCHAR(100),
    created_at TIMESTAMP
);

-- 3. 测试集表
CREATE TABLE test_suites (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    script_ids TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP
);

-- 4. 测试集执行记录表
CREATE TABLE suite_executions (
    id VARCHAR(36) PRIMARY KEY,
    suite_id VARCHAR(36) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_count INT DEFAULT 0,
    passed_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration INT,
    executor VARCHAR(100),
    created_at TIMESTAMP
);

-- 5. 测试结果归档表
CREATE TABLE test_archives (
    id VARCHAR(36) PRIMARY KEY,
    suite_execution_id VARCHAR(36) NOT NULL,
    archive_name VARCHAR(255) NOT NULL,
    archive_file VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_count INT,
    created_at TIMESTAMP
);

-- 6. 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    last_login TIMESTAMP,
    created_at TIMESTAMP
);
```

## 🐍 Python测试脚本

**脚本特点**:
- ✅ 测试人员自行控制所有参数配置
- ✅ 通过`sys.exit(returncode)`返回结果(0=成功, 非0=失败)
- ✅ 使用`print()`输出日志,被平台收集
- ✅ 可以使用任何Python库

**关键代码片段**:
```python
# 参数配置
GIDS_ADDR = "http://192.168.1.100:9090"
DEVICE_WHITE_IMEI = "6258412454025411"

# 测试步骤
def test_full_params():
    response = requests.post(url, json=full_data)
    print(f"[INFO] 响应状态码: {response.status_code}")
    return True  # 成功返回True

# 主函数
def main():
    test_results = []
    test_results.append(("步骤1", test_full_params()))

    all_passed = all(result for _, result in test_results)
    return 0 if all_passed else 1  # 0=成功, 非0=失败

if __name__ == "__main__":
    sys.exit(main())
```

## 🔄 执行流程

```
1. 测试人员编写Python脚本 (本地IDE)
         ↓
2. 通过Web界面上传脚本到平台
         ↓
3. 平台将脚本保存到文件系统 (/data/scripts/)
         ↓
4. 平台将脚本信息写入数据库 (test_scripts表)
         ↓
5. 用户点击"执行"按钮
         ↓
6. 后端执行引擎调用: python3 script.py
         ↓
7. 收集执行日志: stdout + stderr
         ↓
8. 检查退出码: exit_code (0=成功, 非0=失败)
         ↓
9. 将执行结果写入数据库 (test_executions表)
         ↓
10. 前端WebSocket实时推送执行进度
         ↓
11. 测试完成,生成测试报告
```

## 📦 测试集归档

**归档粒度**: 测试集 (Suite)

**归档内容**: 测试集内所有测试脚本的执行结果
```
归档包结构:
suite_001_archive_20250415.zip
├── scripts/
│   ├── TC_SBG_Func_GIDS_001_004.py
│   └── ...
├── logs/
│   ├── execution_001.log
│   ├── execution_002.log
│   └── ...
├── reports/
│   ├── test_report.html
│   └── test_report.json
└── metadata.json
```

**归档目的**:
- ✅ 问题定位和修复
- ✅ 历史追溯
- ✅ 对比分析
- ✅ 审计支持

## ✅ 打样验证清单

**功能验证**:
- [ ] 上传Python脚本
- [ ] 执行Python脚本
- [ ] 收集执行日志(stdout/stderr)
- [ ] 检查exit_code判断结果
- [ ] 存储执行记录到PostgreSQL
- [ ] 前端展示执行记录
- [ ] 前端展示详细日志
- [ ] WebSocket实时推送进度
- [ ] 生成测试报告
- [ ] 创建测试集
- [ ] 执行测试集
- [ ] 归档测试结果
- [ ] 下载归档包

**非功能验证**:
- [ ] 用户登录认证
- [ ] API响应时间 < 500ms (不包括脚本执行时间)
- [ ] 前端界面响应友好
- [ ] 数据库事务一致性
- [ ] 错误处理和异常捕获
- [ ] 日志记录完整性
- [ ] 文件路径安全 (防止路径遍历攻击)

## 🚀 下一步行动

1. **环境准备**
   - 部署PostgreSQL数据库
   - 创建数据库和表结构
   - 安装Go和Python运行环境

2. **后端开发** (Go + Gin)
   - 实现API接口 (参考API_Design.md)
   - 实现Python脚本执行引擎
   - 实现日志收集和存储
   - 实现WebSocket实时推送
   - 实现归档管理功能

3. **前端开发** (React + Ant Design)
   - 实现登录页面
   - 实现脚本上传界面
   - 实现执行监控界面
   - 实现测试报告页面
   - 实现归档管理界面

4. **集成测试**
   - 使用打样用例TC_SBG_Func_GIDS_001_004.py进行端到端测试
   - 验证所有核心功能
   - 修复发现的问题

5. **文档完善**
   - 更新用户使用手册
   - 更新API文档
   - 更新部署文档

## 📞 联系方式

如有问题或需要进一步说明,请参考:
- 需求提案: proposal.md
- 系统设计: design.md
- API设计: API_Design.md
- 打样设计: POC_GIDS_Parameter_Test.md

设计完成时间: 2025-04-15
文档版本: v1.0