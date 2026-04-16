# 云手机测试平台技术设计文档

## Context

### 背景

云手机系统包含三个核心业务网元:BrowserGateway(Java/Spring)、GIDS(Go/Beego)、MediaCache(Go/Beego)。测试开发人员需要对这些系统进行自动化测试,已经编写了各种测试脚本(API测试、单元测试、E2E测试等)。

**核心问题**:
1. **测试脚本分散**: 不同类型、不同语言的测试脚本分散在各处,缺乏统一管理
2. **执行环境不统一**: 测试脚本需要在不同的环境/工具中执行,缺乏统一的执行引擎
3. **结果收集困难**: 测试结果(日志、截图、媒体流)分散存储,难以统一收集和分析
4. **资源调度复杂**: E2E测试需要配置浏览器实例、设备参数等,手动配置复杂易错
5. **协作效率低**: 测试结果和报告缺乏统一的查看和分析平台
6. **监控能力弱**: 测试执行过程不透明,难以实时监控和定位问题

**核心约束**: 本工程无法覆盖全部云手机测试场景,只能覆盖可通过测试脚本验证的场景。部分场景(如验证收到的视频帧是否符合预期)仍需要真实UE终端进行测试验证。设计重点是通过打样场景验证平台核心能力,同时为后续扩展更多场景提供可扩展的架构基础。

### 打样场景选择

**打样场景**: 验证用户UE端的IMSI、IMEI是否为空

**选择理由**:
1. ✅ **代表性**: 这是云手机系统的基础参数验证场景,涵盖了API调用、结果验证等核心测试步骤
2. ✅ **简洁性**: 测试逻辑简单明确,易于理解和实现,适合快速验证平台能力
3. ✅ **可执行性**: 可以通过测试脚本完全自动化执行,不需要真实UE终端参与
4. ✅ **可扩展性**: 从这个基础场景出发,可以逐步扩展到更复杂的场景(如License测试、用户会话测试等)
5. ✅ **脚本灵活性**: 测试人员在脚本中自行控制参数配置,平台不限制参数管理方式

**场景描述**:
```
1. 测试人员编写测试脚本(包含参数配置,如IMSI、IMEI等)
2. 测试人员上传脚本到平台
3. 平台执行脚本,不干预参数配置
4. 验证API调用和结果
5. 记录测试结果和日志
6. 生成测试报告
```

**业务侧测试用例格式参考**:

```json
{
  "TestCase_Number": "TC_SBG_DFx_License_001",
  "TestCase_Name": "License销显控一致性测试",
  "TestCase_Pretreatment Condition": "1、SBG网元部署成功，环境为多Pod环境；\n2、DSP ESN查询设备序列号；\n3、登录ESDP平台申请SBG License文件...",
  "TestCase_Test Steps": "1、 激活License文件，分别覆盖以下两种方式：\n 1）CSP页面ACT LICENSE命令激活；\n 2）CSP页面[Application Lifecycle--> Licenses-->\n2、构造10个用户访问云手机业务并访问流量；\n3、构造用户数增加和减少场景...",
  "TestCase_Expected Result": "1、DSP LICENSE查询：License文件激活成功，申请License项值与实际显示一致；\n2、DSP LICENSERES查询：实际用户数、实际流量，以及对应的使用占比符合预期..."
}
```

**重要说明**:
- 平台**不提供**Web界面的参数配置管理功能
- 测试人员根据业务用例需求,在脚本中自行实现参数配置逻辑
- 平台只负责脚本的执行、日志收集和报告生成
- 参数配置的灵活性和复杂度完全由测试脚本控制

**平台不覆盖的场景**:
- ❌ 真实UE终端的视频帧验证(需要硬件设备)
- ❌ 复杂的端到端用户交互(需要真实的触控设备)
- ❌ 硬件资源相关的测试(需要特定硬件环境)

**平台覆盖的场景**:
- ✅ API接口测试(参数验证、响应验证)
- ✅ 单元测试(代码逻辑验证)
- ✅ E2E测试(模拟虚拟UE设备,通过Mobile服务)
- ✅ 集成测试(多个服务协同)

**核心理念**: 本平台是一个**测试框架执行引擎**。测试开发人员负责编写测试脚本(定义测试点、测试步骤),平台提供:
1. 脚本上传和管理
2. 统一的脚本执行引擎
3. 测试资源自动调度和配置
4. 执行过程实时监控
5. 结果自动收集和报告生成

测试人员无需关心底层执行细节,只需关注测试逻辑的编写。

### 当前状态

**现有测试基础:**
- `BrowserGateway-Blackbox-Test`: 已有基于Java的自动化测试框架
  - JUnit 5 + TestNG测试框架
  - RestAssured API测试
  - Selenium/Playwright浏览器自动化
  - Allure测试报告
- 测试用例存储: 代码仓库中的测试类 + 测试文档(黑盒测试用例0-45.md等)
- 测试执行方式: Maven命令行、IDE运行、CI/CD集成

**被测系统接口:**
- BrowserGateway:
  - REST: `/browsergw/browser/preOpen`, `/browsergw/browser/userdata/delete`, `/browsergw/extension/load`
  - WebSocket: `ws://host/browser/websocket/{imeiAndImsi}`, `ws://host/control/websocket/{imeiAndImsi}`
  - TCP TLV: 控制流和媒体流
- GIDS:
  - REST: `/file/v1/{bucket}/{name}` (upload/download), `/auth/v1/authIMEI`
- MediaCache:
  - 视频流API、媒体控制接口

### 约束条件

1. **部署约束**: 测试平台独立部署,不与生产环境耦合,只需保证与被测网元网络连通
2. **技术约束**: 后端必须使用Python(FastAPI/Flask),前端必须使用React + Ant Design
3. **功能约束**: 不实现性能压测、系统监控仪表盘、角色权限管理
4. **数据约束**: 用户数据通过数据库直接管理,暂无LDAP/SSO集成需求
5. **兼容性**: 需要兼容现有测试用例文档格式

### 利益相关者

- 测试开发人员: 负责编写和维护自动化测试用例
- 测试执行人员: 负责执行测试、查看报告
- 开发人员: 了解测试结果,快速定位问题
- 项目经理: 查看整体测试进度和质量

## Goals / Non-Goals

### Goals

1. **测试脚本管理**: 提供统一的管理界面,支持测试人员上传、版本管理、分类测试脚本
2. **脚本执行引擎**: 提供统一的执行引擎,支持多种脚本类型(API/Unit/E2E)和语言
3. **资源自动调度**: 自动管理测试执行所需的资源(测试环境、浏览器实例、设备配置)
4. **实时执行监控**: 提供监控界面,实时展示执行状态、日志、E2E测试画面
5. **结果自动收集**: 自动收集执行结果(日志、截图、媒体流),统一存储和管理
6. **结果归档管理**: 支持测试结果的归档、查询、版本管理,便于历史追溯
7. **结果下载功能**: 支持导出测试结果(完整归档包/日志/报告/截图等)供问题定位和修复
8. **统一报告生成**: 自动生成测试报告,提供统一的查看和分析界面
9. **批量执行支持**: 支持单个/批量测试脚本执行,提高测试效率
10. **简单用户认证**: 实现基本的用户登录功能,区分测试人员操作记录

### Non-Goals

1. ❌ 不提供测试脚本的具体编写/编辑界面(编写在IDE/文本编辑器中进行)
2. ❌ 不提供测试脚本的调试功能(调试在原开发工具中进行)
3. ❌ 不强制测试脚本的语言/格式(支持多种格式,测试人员自由选择)
4. ❌ 不实现性能压测功能(已明确排除)
5. ❌ 不实现系统监控仪表盘(已明确排除)
6. ❌ 不实现角色权限管理(只需用户认证)
7. ❌ 不管理被测系统的实例部署
8. ❌ 不实现测试结果通知(邮件/钉钉/企微)
9. ❌ 不实现CI/CD集成(作为后续扩展)
10. ❌ 不提供测试脚本的代码审查功能

## Decisions

### D1: 前后端分离架构

**决策**: 采用前后端分离架构,前端React + Ant Design,后端Python + FastAPI

**理由**:
1. **团队技术栈匹配**: 测试开发人员具备Python技术栈,降低学习成本和维护成本
2. **快速开发**: FastAPI提供自动API文档、异步支持、类型检查,开发效率高
3. **生态丰富**: Python测试生态成熟(Pytest、Requests、Selenium、Playwright),与测试脚本语言一致
4. **跨系统集成**: 通过REST API调用BrowserGateway、GIDS、MediaCache,不受语言限制
3. **用户体验**: React生态丰富,Ant Design提供完善的UI组件,快速构建友好界面
4. **部署灵活**: 前后端独立部署,前端可托管在Nginx/CDN,后端可水平扩展
5. **职责清晰**: 前端负责展示和交互,后端负责执行和调度,符合"看护平台"定位

**考虑过的替代方案**:
- 全栈Go(Go + Gin + 模板引擎): 服务端渲染,SEO友好,但前端开发体验差,组件库较少
- 全栈Java(与BrowserGateway一致): 复用现有Java技术栈,但需要额外与Go服务集成
- Python后端(FastAPI): 测试框架丰富,但与被测系统技术栈不一致

**特别说明**: 由于平台主要功能是"看护"现有的自动化测试用例,而不是创建新用例,因此不复杂的前端交互需求,React + Ant Design完全够用。

### D2: RESTful API设计

**决策**: 前后端通过RESTful API通信,E2E测试补充WebSocket实时推送

**理由**:
1. **标准规范**: RESTful API是业界标准,易于理解和维护
2. **工具支持**: 前端可用Axios等HTTP客户端,后端可用Swagger/OpenAPI生成文档
3. **无状态**: 便于水平扩展和负载均衡
4. **WebSocket补强**: E2E测试需要实时推送执行状态和浏览器画面,使用WebSocket补充

**API设计原则**:
```
GET    /api/v1/testcases                    # 获取用例列表
POST   /api/v1/testcases                    # 创建用例
GET    /api/v1/testcases/:id                # 获取用例详情
PUT    /api/v1/testcases/:id                # 更新用例
DELETE /api/v1/testcases/:id                # 删除用例
POST   /api/v1/testcases/import             # 导入用例

POST   /api/v1/executions                   # 创建执行任务
GET    /api/v1/executions/:id               # 获取执行详情
GET    /api/v1/executions/:id/report        # 获取测试报告
POST   /api/v1/executions/:id/retry         # 重试执行
DELETE /api/v1/executions/:id               # 停止执行

POST   /api/v1/e2e/tests                    # 创建E2E测试
GET    /api/v1/e2e/tests/:id                # 获取E2E测试详情
WS     /api/v1/e2e/tests/:id/stream         # E2E实时流推送

POST   /api/v1/auth/login                   # 用户登录
POST   /api/v1/auth/logout                  # 用户登出
GET    /api/v1/auth/profile                 # 获取用户信息
```

**考虑过的替代方案**:
- GraphQL: 灵活的查询语言,但增加复杂度,学习成本高
- gRPC: 高性能,适合服务间通信,但不适合前端直接调用
- 纯WebSocket: 实时性好,但不适合所有场景(如静态资源查询)

### D3: 数据库设计

**决策**: 使用PostgreSQL作为主数据库,采用关系型模型存储测试元数据

**理由**:
1. **与被测系统一致**: 被测系统使用PostgreSQL,统一技术栈降低维护成本
2. **元数据存储**: 测试平台只存储测试用例的元数据(名称、描述、目标服务等),不存储测试代码
3. **关系数据适合**: 测试用例、执行记录、报告等元数据具有强关联性,关系型数据库更合适
4. **事务支持**: 保证数据一致性(如测试执行的状态变更)
5. **查询能力**: 支持复杂查询(如测试历史统计、报告聚合)

**核心数据模型**(测试脚本和执行数据):

```sql
-- 测试脚本表
**核心数据模型**(功能最小集,Python脚本)

```sql
-- 测试脚本表
CREATE TABLE test_scripts (
    id VARCHAR(36) PRIMARY KEY,                    -- 脚本ID (使用UUID字符串)
    name VARCHAR(255) NOT NULL,                    -- 脚本名称
    script_file VARCHAR(500) NOT NULL,             -- 脚本文件路径
    script_type VARCHAR(50),                       -- 脚本类型(api/test/e2e)
    status VARCHAR(20) DEFAULT 'active',           -- 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 测试执行记录表
CREATE TABLE test_executions (
    id VARCHAR(36) PRIMARY KEY,                    -- 执行ID
    script_id VARCHAR(36) NOT NULL,                 -- 关联的脚本ID
    status VARCHAR(20) NOT NULL,                    -- 执行状态
    exit_code INT,                                  -- Python退出码
    logs TEXT,                                      -- 执行日志(20KB以内存储,更大存文件)
    logs_file VARCHAR(500),                         -- 完整日志文件路径
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration INT,                                   -- 执行耗时(秒)
    error_message TEXT,                             -- 错误信息
    executor VARCHAR(100),                          -- 执行人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 测试集表(用于批量执行和归档)
CREATE TABLE test_suites (
    id VARCHAR(36) PRIMARY KEY,                    -- 测试集ID
    name VARCHAR(255) NOT NULL,                    -- 测试集名称
    description TEXT,                               -- 测试集描述
    script_ids TEXT,                                -- 关联的脚本ID列表(逗号分隔)
    created_by VARCHAR(100),                        -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 测试集执行记录表(归档粒度)
CREATE TABLE suite_executions (
    id VARCHAR(36) PRIMARY KEY,                    -- 测试集执行ID
    suite_id VARCHAR(36) NOT NULL,                  -- 关联的测试集ID
    status VARCHAR(20) NOT NULL,                    -- 执行状态
    total_count INT DEFAULT 0,                      -- 总用例数
    passed_count INT DEFAULT 0,                     -- 通过数
    failed_count INT DEFAULT 0,                     -- 失败数
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration INT,                                   -- 总耗时(秒)
    executor VARCHAR(100),                          -- 执行人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 测试结果归档表(测试集粒度)
CREATE TABLE test_archives (
    id VARCHAR(36) PRIMARY KEY,                    -- 归档ID
    suite_execution_id VARCHAR(36) NOT NULL,         -- 关联的测试集执行ID
    archive_name VARCHAR(255) NOT NULL,             -- 归档名称
    archive_file VARCHAR(500) NOT NULL,             -- 归档文件路径
    file_size BIGINT,                               -- 文件大小(字节)
    file_count INT,                                 -- 文件数量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**设计说明**:
1. **轻量级**: 只保留核心字段,去除重型JSONB字段和复杂关联
2. **Python适配**: 使用exit_code判断Python脚本执行结果
3. **测试集归档**: 归档粒度为测试集,通过suite_executions和test_archives关联
4. **最小功能集**: 满足脚本上传、执行、结果收集、归档下载的基本需求
5. **简单查询**: 避免复杂的JOIN查询,提高查询性能

-- E2E测试监控会话表(用于E2E测试的实时监控)
CREATE TABLE e2e_monitor_sessions (
    id UUID PRIMARY KEY,
    execution_id UUID REFERENCES script_executions(id) ON DELETE CASCADE,
    mobile_instance_id VARCHAR(255),          -- Mobile实例ID
    device_config JSONB,                     -- 设备配置(IMEI/IMSI/屏幕等)
    browser_config JSONB,                    -- 浏览器配置
    status VARCHAR(20) DEFAULT 'idle',
    current_step_index INT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    screenshot_path VARCHAR(500),            -- 最新截图路径
    video_url VARCHAR(500),                  -- 视频录制URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    role VARCHAR(50) DEFAULT 'tester',      -- 角色(admin/tester/viewer)
    last_login_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表(包括GIDS地址、Mobile路径等)
CREATE TABLE configs (
    id UUID PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    config_type VARCHAR(50),                -- 配置类型(system/resource/environment)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**考虑过的替代方案**:
- MongoDB: 文档型数据库,适合JSON数据,但关系查询能力弱
- Redis: 内存数据库,性能高,但数据持久化弱,不适合存储测试记录
- MySQL/PostgreSQL: 成熟稳定,但与现有PostgreSQL不一致,增加维护成本

### D4: E2E测试技术选型

**决策**: 复用mobile项目的测试逻辑,测试平台通过WebSocket连接到mobile服务进行E2E测试

**理由**:
1. **复用现有**: mobile项目已经实现了完整的虚拟手机设备模拟逻辑(BrowserContext、ControlChannel、MediaChannel)
2. **技术一致**: mobile使用Java Spring Boot + Netty,已与BrowserGateway/GIDS集成验证
3.降低风险**: 直接复用已验证的逻辑,避免重新开发浏览器控制、TLV编码等复杂功能
4. **维护简单**: mobile项目的更新可以同步应用于测试

**E2E测试架构**:

```
┌─────────────────────────────────────────────────────────────┐
│                     前端                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  E2E测试监控页面                                      │   │
│  │  ├─ WebSocket接收实时画面和日志                       │   │
│  │  ├─ 展示执行进度和步骤状态                            │   │
│  │  └─ 控制测试执行(开始/停止)                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     ▲ HTTP/WebSocket
                     │ 实时推送
┌─────────────────────────────────────────────────────────────┐
│                     后端测试平台                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  E2E测试引擎                                          │   │
│  │  ├─ 启动mobile服务(Spring Boot应用)                  │   │
│  │  ├─ 调用mobile登录API(gridLoginAuth)                 │   │
│  │  ├─ 通过WebSocket连接到mobile服务                     │   │
│  │  ├─ 接收并转发媒体流(视频/音频)到前端                 │   │
│  │  ├─ 发送控制指令(按键/触控)到mobile                   │   │
│  │  ├─ 监听测试步骤,通过WebSocket推进度                 │   │
│  │  └─ 验证测试结果                                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Mobile服务 (Spring Boot)                          │
│  现有项目: D:\Code\云手机\SBG\mobile                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  BrowserContext                                      │   │
│  │  ├─ 设备登录(gridLoginAuth/gridLoginAuthOpenBrowser) │  │
│  │  ├─ 控制通道(ControlChannelHandler)                   │   │
│  │  ├─ 媒体通道(MediaChannelHandler)                     │   │
│  │  └─ TLV编解码控制媒体传输的全流程已实现)             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │ HTTP/TLV/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              被测系统                                         │
│  GIDS              BrowserGateway          MediaCache          │
│  (授权/文件)        (虚拟浏览器)            (视频流)             │
└─────────────────────────────────────────────────────────────┘
```

**测试执行架构**:

```
┌─────────────────────────────────────────────────────────────┐
│                     前端                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  自动化测试用例列表                                    │   │
│  │  ├─ 查看用例元数据(名称/描述/目标服务等)              │   │
│  │  └─ 一键执行按钮                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  执行监控页面                                         │   │
│  │  ├─ WebSocket接收执行进度                             │   │
│  │  ├─ 展示执行日志                                      │   │
│  │  └─ 显示执行状态和结果                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     ▲ HTTP/WebSocket
                     │ 实时推送
┌─────────────────────────────────────────────────────────────┐
│                     后端测试平台                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试执行引擎                                          │   │
│  │  ├─ API测试: 直接调用HTTP接口 (curl/Go HTTP)         │   │
│  │  ├─ 单元测试: 调用测试CLI (mvn test/go test)          │   │
│  │  ├─ E2E测试: 复用mobile服务                           │   │
│  │  │   ├─ 启动mobile服务(Spring Boot)                   │   │
│  │  │   ├─ 调用mobile登录API                             │   │
│  │  │   ├─ 通过WebSocket连接mobile                       │   │
│  │  │   ├─ 接收媒体流并转发到前端                        │   │
│  │  │   ├─ 发送控制指令(按键/触控)                       │   │
│  │  │   └─ 监听测试完成状态                              │   │
│  │  ├─ 监听执行日志(通过文件/管道)                        │   │
│  │  ├─ 通过WebSocket推送进度到前端                        │   │
│  │  ├─ 收集执行结果并写入数据库                          │   │
│  │  └─ 生成测试报告                                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │ 调用
           ▼
┌─────────────────────────────────────────────────────────────┐
│       现有测试框架和Mobile服务                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ BrowserGW    │  │  GIDS        │  │  Mobile      │   │
│  │  黑盒测试项目  │  │              │  │ (Spring Boot)│   │
│  │  (Maven)     │  │              │  │  D:\Code\...  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```
┌─────────────────────────────────────────────────────────────┐
│                     前端                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  自动化测试用例列表                                    │   │
│  │  ├─ 查看用例元数据(名称/描述/目标服务等)              │   │
│  │  └─ 一键执行按钮                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  执行监控页面                                         │   │
│  │  ├─ WebSocket接收执行进度                             │   │
│  │  ├─ 展示执行日志                                      │   │
│  │  ├─ 展示E2E测试的实时截图                             │   │
│  │  └─ 显示执行状态和结果                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     ▲ HTTP/WebSocket
                     │ 实时推送
┌─────────────────────────────────────────────────────────────┐
│                     后端测试平台                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试执行引擎                                          │   │
│  │  ├─ 从数据库读取用例元数据                              │   │
│  │  ├─ 调用测试框架的CLI/API                             │   │
│  │  │   ├─ API测试: curl HTTP请求                         │   │
│  │  │   ├─ 单元测试: mvn test / go test                  │   │
│  │  │   └─ E2E测试: 调用Playwright Go                    │   │
│  │  ├─ 监听执行日志(通过文件/管道)                        │   │
│  │  ├─ 通过WebSocket推送进度到前端                        │   │
│  │  ├─ 收集执行结果并写入数据库                          │   │
│  │  └─ 生成测试报告                                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │ 调用
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              现有测试框架和被测系统                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ BrowserGW    │  │  GIDS        │  │ MediaCache   │   │
│  │  黑盒测试项目  │  │              │  │              │   │
│  │  (Maven)     │  │              │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**考虑过的替代方案**:
- Selenium Go: 成熟稳定,但API设计较旧,自动等待机制不如Playwright
- Cypress: JavaScript主导,与Go后端集成复杂
- Puppeteer: 仅支持Chrome,Playwright支持多浏览器

### D5: 测试报告生成

**决策**: 前端基于后端API数据渲染HTML报告,支持导出为PDF

**理由**:
1. **灵活性**: 前端可灵活定制报告样式和交互
2. **实时性**: 报告与测试数据同步,无需额外生成过程
3. **用户体验**: 前端支持交互式报告(折叠/展开、筛选、排序)
4. **导出能力**: 使用html2pdf等库导出PDF,满足归档需求

**报告结构**:
```javascript
{
  "executionId": "EX001",
  "testCaseId": "TC001",
  "testCaseName": "YouTube视频搜索",
  "status": "passed",
  "startedAt": "2025-04-15T10:30:00Z",
  "finishedAt": "2025-04-15T10:30:02Z",
  "durationMs": 2300,
  "executedBy": "admin",
  "summary": {
    "totalSteps": 4,
    "passedSteps": 4,
    "failedSteps": 0,
    "skippedSteps": 0,
    "passRate": 100
  },
  "steps": [
    {
      "stepNumber": 1,
      "action": "输入搜索内容",
      "expectedResult": "能正常输入",
      "actualResult": "能正常输入",
      "status": "passed",
      "durationMs": 500,
      "screenshot": "/screenshots/EX001_step1.png"
    },
    // ...
  ],
  "logs": "[10:30:00.000] INFO  开始执行测试用例 TC001\n...",
  "error": null
}
```

**考虑过的替代方案**:
- 后端生成静态HTML报告: 生成简单,但样式定制受限
- 使用Allure报告: 功能强大,但需要集成Allure服务,增加复杂度
- 纯文本日志: 简单直接,但缺乏可视化

### D6: 用户认证实现

**决策**: 使用JWT(JSON Web Token)实现无状态认证

**理由**:
1. **无状态**: 服务器不存储会话,便于水平扩展
2. **跨域友好**: 前后端分离场景下,CORS配置简单
3. **自包含**: Token包含用户信息,减少数据库查询
4. **安全性**: 支持过期时间、refresh token等机制

**认证流程**:
```
1. 用户登录
   POST /api/v1/auth/login
   Request: { username, password }
   Response: { accessToken, refreshToken, expiresIn }

2. 访问受保护资源
   GET /api/v1/testcases
   Headers: Authorization: Bearer <accessToken>

3. Token刷新
   POST /api/v1/auth/refresh
   Request: { refreshToken }
   Response: { accessToken, refreshToken }

4. 用户登出
   POST /api/v1/auth/logout
   Request: { refreshToken }
```

**考虑过的替代方案**:
- Session + Cookie: 传统方案,但前后端分离下需要CORS和session共享
- OAuth 2.0: 适合第三方登录,但过于复杂,当前不需要
- Basic Auth: 简单直接,但安全性低,需要每次传输密码

### D7: 测试用例导入格式支持

**决策**: 支持Excel、CSV、JSON、Markdown多格式导入

**理由**:
1. **兼容现有**: 支持现有的Markdown测试用例文档
2. **用户习惯**: 测试人员常用Excel管理用例
3. **灵活性**: JSON适合程序化生成,适合CI/CD集成
4. **标准化**: CSV格式简单,易于跨工具迁移

**导入流程**:
```
1. 用户上传文件
2. 后端解析文件(Excel github.com/360EntSecGroup-Skylar/excelize)
3. 转换为标准JSON格式
4. 批量插入数据库(事务保证一致性)
5. 返回导入结果(成功/失败数量)
6. 前端展示导入报告
```

**Markdown解析示例**:
```markdown
| 用例ID | 用例名称 | 特性名称 | 级别 | 预置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|------|----------|----------|----------|
| TC001  | YouTube搜索 | 功能验证 | 0 | P1,P2,P3 | S1,S2,S3,S4 | E1,E2,E3,E4 |
```

### D8: 批量执行策略

**决策**: 采用任务队列 + Worker池的批量执行模式

**理由**:
1. **并发控制**: 通过Worker池控制并发数,避免资源耗尽
2. **任务调度**: 任务队列支持优先级、重试、超时等特性
3. **实时反馈**: 通过WebSocket推送执行进度
4. **可扩展**: 后续可扩展为分布式执行

**执行架构**:
```
┌─────────────────────────────────────────────────────────────┐
│  前端                                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  用例列表 → 批量选中 → 点击"批量执行"               │   │
│  │  └─ WebSocket接收执行进度                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │ POST /batch-execution
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  后端任务调度器                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐          │   │
│  │  任务队列  │▶ │  Worker池  │▶ │  状态存储  │          │   │
│  │ (channel)  │  │ (goroutine)│  │ (Redis/Mem)│          │   │
│  └────────────┘  └────────────┘  └────────────┘          │   │
│         │                │                                   │   │
│         │                ▼                                   │   │
│         │        ┌──────────────┐                          │   │
│         │        │  API调用模块 │                          │   │
│         │        │  │ TIID服务) │                          │   │
│         │        └──────────────┘                          │   │
│         └────────────────────────────────────────┐         │   │
│             ▼                        ▼             │         │   │
│        定时器推送                 WebSocket推送   │         │   │
│        执行进度                  实时日志          │         │   │
│                                                     │         │   │
└─────────────────────────────────────────────────────┘         │
```

**Worker池配置**:
- 默认并发数: 5个
- 每个Worker处理一个测试用例
- 超时时间: 300秒
- 重试次数: 1次

## Risks / Trade-offs

### 风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| BrowserGateway API不稳定导致测试失败 | 测试结果不准确 | 中 | 增加重试机制,记录失败原因,提供手动重试 |
| E2E测试浏览器启动慢/失败 | 用户体验差 | 中 | 设置合理的超时时间,提供进度提示,支持手动重试 |
| 测试数据量过大导致数据库性能问题 | 系统响应慢 | 低 | 定期清理历史数据,添加索引,考虑分表 |
| WebSocket连接不稳定导致实时监控中断 | 用户体验差 | 中 | 实现自动重连,提供手动刷新,保留历史记录 |
| 测试用例导入格式解析错误 | 数据丢失/错误 | 低 | 严格校验,预览模式,事务回滚 |
| 并发测试导致资源耗尽 | 系统崩溃 | 低 | 控制并发数,资源池管理,限流 |

### 权衡

1. **实时性 vs 稳定性**:
   - 实时推送执行状态提升用户体验,但增加WebSocket复杂度
   - **权衡**: 采用WebSocket + 轮询混合模式,WebSocket断开时自动降级为轮询

2. **功能完整性 vs 开发速度**:
   - 完整功能(报告导出、定时任务等)需要更多开发时间
   - **权衡**: 分阶段实现,v1.0优先核心功能,v1.5扩展高级功能

3. **测试覆盖率 vs 测试效率**:
   - 全量测试覆盖全面但耗时长,快速测试效率高但遗漏风险
   - **权衡**: 支持测试组合(冒烟测试、回归测试、完整测试)

4. **数据保留 vs 存储成本**:
   - 长期保留测试历史便于追溯,但占用存储空间
   - **权衡**: 默认保留30天,支持手动归档和清理配置

## Migration Plan

### 部署步骤

1. **环境准备**
   - 部署PostgreSQL数据库(复用或新建)
   - 创建数据库和用户,执行SQL脚本
   - 配置网络连接(测试平台 ↦ 被测系统)

2. **后端部署**
   ```bash
   # 编译
   cd backend
   go build -o test-platform-server

   # 配置文件(config.yaml)
   database:
     host: 192.168.x.x
     port: 5432
     database: test_platform
     user: test_user
     password: xxxx

   services:
     browser_gateway: http://192.168.x.x:9090
     gids: http://192.168.x.x:8080
     media_cache: http://192.168.x.x:8888

   # 启动
   ./test-platform-server --config=config.yaml
   ```

3. **前端部署**
   ```bash
   # 构建
   cd frontend
   npm install
   npm run build

   # 部署到Nginx
   cp -r dist/* /var/www/test-platform/

   # Nginx配置
   server {
       listen 80;
       server_name test-platform.local;

       root /var/www/test-platform;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8080;
       }
   }
   ```

4. **初始化数据**
   ```sql
   -- 创建默认管理员
   INSERT INTO users (username, password_hash, nickname) VALUES
   ('admin', '$2a$10$...', '管理员');

   -- 插入配置
   INSERT INTO configs (config_key, config_value, description) VALUES
   ('browser_timeout', '30', '浏览器超时时间(秒)'),
   ('max_concurrent_tests', '5', '最大并发测试数');
   ```

5. **导入现有测试用例**
   - 从测试用例文档(Excel/Markdown)导入
   - 验证导入数据的正确性
   - 测试执行流程

### 回滚策略

1. **后端回滚**
   - 保留上一个版本的可执行文件
   - 测试新版本前备份数据库
   - 回滚时停止新版本,启动旧版本

2. **前端回滚**
   - 使用版本化部署(如dist-v1.0/, dist-v1.1/)
   - Nginx切换到旧版本目录
   - 清空浏览器缓存或使用版本号控制

3. **数据回滚**
   - 每次重要变更前备份数据库
   ```bash
   pg_dump test_platform > backup_$(date +%Y%m%d).sql
   ```
   - 紧急回滚时恢复数据库
   ```bash
   psql test_platform < backup_20250415.sql
   ```

4. **快速回滚步骤**
   ```bash
   # 1. 停止服务
   systemctl stop test-platform-backend
   systemctl stop nginx

   # 2. 回滚代码
   cd /opt/test-platform
   git checkout v1.0  # 回滚到稳定版本

   # 3. 重新部署
   ./deploy.sh version=v1.0

   # 4. 回滚数据库(如需要)
   psql test_platform < backup_20250410.sql

   # 5. 启动服务
   systemctl start test-platform-backend
   systemctl start nginx
   ```

## Open Questions

1. **Q1: 测试数据的隔离机制?**
   - 不同测试用例是否需要独立的测试数据?
   - 测试失败后是否自动清理测试数据?
   - **待解决**: v1.5阶段考虑实现测试数据管理模块

2. **Q2: 测试步骤的断言机制?**
   - 如何定义和验证测试步骤的预期结果?
   - 是否支持自定义断言脚本?
   - **待解决**: v1.0支持简单的文本匹配,v1.5扩展为支持表达式断言

3. **Q3: 测试报告的持久化?**
   - 执行记录是永久保存还是定期清理?
   - 报告是否支持版本化?
   - **决策**: 默认保留30天,支持配置和历史归档

4. **Q4: E2E测试的并发执行?**
   - 多个E2E测试是否可以并行执行?
   - 浏览器资源如何管理?
   - **决策**: v1.0顺序执行,v1.5支持并发执行(限制浏览器实例数)

5. **Q5: 测试用例的版本管理?**
   - 用例修改是否有历史记录?
   - 是否支持用例回滚?
   - **待解决**: v2.0引入用例版本管理

6. **Q6: 与CI/CD的集成方式?**
   - 是否提供命令行工具?
   - 支持哪些CI平台?
   - **待解决**: v2.0提供CLI工具和Jenkins/GitLab CI插件

## 核心定位说明

### 平台定位

本测试平台的核心理念是:**测试框架执行引擎**。

**平台提供的是:**
- ✅ 测试脚本上传和管理(支持多种脚本格式/语言)
- ✅ 统一的脚本执行引擎(API/Unit/E2E等)
- ✅ 测试资源自动调度和配置(环境、设备、实例)
- ✅ 执行过程实时监控(日志、进度、E2E画面)
- ✅ 测试结果自动收集(日志、截图、媒体流)
- ✅ 统一的报告生成和展示

**平台不做的是:**
- ❌ 不编写测试脚本(测试人员提供)
- ❌ 不调试测试脚本(调试在原开发工具中进行)
- ❌ 不强制脚本格式(支持多种格式,测试人员自由选择)
- ❌ 不审查测试逻辑(测试人员负责)

### 职责划分

```
┌─────────────────────────────────────────────────────────────┐
│                     测试开发人员                                │
└─────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   IDE / 文本编辑器       │  │      本测试平台         │
│                          │  │                          │
│  ✓ 编写测试脚本          │  │  ✓ 上传测试脚本         │
│  ✓ 调试测试逻辑          │  │  ✓ 配置脚本元数据       │
│  ✓ 运行本地测试          │  │  ✓ 执行测试脚本         │
│  ✓ 查看本地日志          │  │  ✓ 调度测试资源         │
│  ✓ Git版本管理          │  │  ✓ 监控执行进度         │
│  └─ 脚本语言自由选择     │  │  ✓ 收集测试结果         │
│     (Java/Go/Python等)   │  │  ✓ 生成测试报告         │
│                          │  │  └─ 支持多种脚本类型    │
│                          │  │    (API/Unit/E2E)      │
└──────────────────────────┘  └──────────────────────────┘
```

### 支持的脚本类型

平台作为测试框架执行引擎,支持以下脚本类型:

1. **API测试脚本**
   - 格式: HTTP请求文件、Postman Collection、cURL命令
   - 执行: 直接调用HTTP接口,验证响应
   - 示例: `GET /auth/v1/authIMEI → 验证200响应`

2. **单元测试脚本**
   - 格式: JUnit测试类、Go test文件、Python pytest
   - 执行: 调用测试框架CLI (mvn test / go test / pytest)
   - 示例: `mvn test -Dtest=AuthServiceTest`

3. **E2E测试脚本**
   - 格式: 自定义JSON/YAML配置,定义测试步骤
   - 执行: 通过Mobile服务执行,监听事件流
   - 示例: 定义"搜索→点击→验证"的步骤序列

4. **集成测试脚本**
   - 格式: 混合脚本(调用多个服务)
   - 执行: 按顺序执行多个测试步骤
   - 示例: 登录→上传文件→验证→删除

### 工作流程

1. **脚本开发阶段**(测试人员在本地完成):
   - 选择脚本语言和格式(自由选择)
   - 编写测试逻辑和步骤
   - 本地调试和验证

2. **脚本上传阶段**(在平台中完成):
   - 测试人员上传测试脚本文件
   - 配置脚本元数据(名称、描述、类型、资源需求)
   - 平台存储脚本文件和元数据

3. **测试执行阶段**(在平台中完成):
   - 测试人员选择需要执行的脚本
   - 平台自动调度测试资源(环境、设备、实例)
   - 平台执行脚本并收集结果

4. **结果查看阶段**(在平台中完成):
   - 查看自动生成的测试报告
   - 对比历史执行记录
   - 如需详细调试,回到本地开发环境

### 测试脚本格式示例

**E2E测试脚本格式(JSON示例)**:

```json
{
  "script_name": "YouTube视频搜索测试",
  "script_type": "E2E",
  "device_config": {
    "imei": "6258412454025411",
    "imsi": "68510155565211",
    "manufacturer": "default",
    "model": "default",
    "width": 240,
    "height": 320,
    "language": "zh_CN"
  },
  "test_steps": [
    {
      "step_number": 1,
      "step_name": "启动YouTube",
      "action": "navigate",
      "target": "https://www.youtube.com",
      "expected": "页面加载成功"
    },
    {
      "step_number": 2,
      "step_name": "输入搜索内容",
      "action": "input",
      "selector": "#search-input",
      "value": "测试视频",
      "expected": "输入框内容为'测试视频'"
    },
    {
      "step_number": 3,
      "step_name": "点击搜索按钮",
      "action": "click",
      "selector": "#search-button",
      "expected": "搜索结果页面加载"
    },
    {
      "step_number": 4,
      "step_name": "验证搜索结果",
      "action": "verify",
      "condition": "搜索结果包含'测试视频'",
      "expected": "验证通过"
    }
  ]
}
```

**API测试脚本格式(cURL示例)**:

```bash
# 测试GIDS文件上传
curl -X POST 'http://192.168.1.100:9090/file/v1/test-bucket/filename.txt' \
  -H 'Content-Type: text/plain' \
  -d 'This is test content' \
  --expect 200
```

### 资源调度机制

平台作为测试框架,负责自动调度和管理测试资源:

| 资源类型 | 调度方式 | 配置示例 |
|---------|---------|---------|
| 测试环境 | 动态分配 | 测试环境A/B/C轮询使用 |
| Mobile实例 | 按需创建 | E2E测试时启动Mobile服务 |
| 浏览器配置 | 脚本指定 | width/height/language等 |
| 设备参数 | 脚本指定 | IMEI/IMSI/厂商等 |
| 执行超时 | 全局配置 | 默认300秒,可脚本覆盖 |

### 数据分离

平台存储的是**测试脚本文件**和**执行结果**,不存储测试逻辑:

| 数据类型 | 存储位置 | 说明 |
|---------|---------|------|
| 测试脚本 | 文件系统(或S3) | 实际的脚本文件(.java/.py/.json/.sh等) |
| 脚本元数据 | 测试平台数据库 | 脚本名称、类型、配置等 |
| 执行日志 | 文件系统(或S3) | 每次执行的日志文件 |
| 执行结果 | 测试平台数据库 | 执行状态、统计、错误信息 |
| 截图/媒体 | 文件系统(或S3) | 测试过程中的截图和视频 |
| 配置信息 | 测试平台数据库 | 系统配置和资源信息 |

这种设计的好处:
- 测试脚本可以在任何地方开发,只需上传到平台
- 支持多种脚本语言和格式,测试人员自由选择
- 平台专注于执行和管理,不限制测试开发的方式
- 降低平台复杂度,专注于"执行引擎"功能

---

## 打样场景设计: IMSI/IMEI空值验证

### 场景概述

**打样目标**: 验证云手机测试平台的核心能力,通过一个简单但典型的测试场景

**测试场景**: 验证用户UE端的IMSI、IMEI参数不为空

**覆盖能力**:
- ✅ 测试脚本上传和管理
- ✅ 测试脚本执行引擎
- ✅ API测试能力
- ✅ 测试结果收集和存储
- ✅ 测试报告生成
- ✅ 实时监控和日志展示

### 测试脚本设计

**脚本格式**: JSON模板文件(使用参数占位符)

**脚本内容**:
```json
{
  "script_name": "GIDS设备登录参数验证-IMSI/IMEI非空检查",
  "script_type": "API",
  "script_language": "HTTP",
  "script_format": "JSON",
  "version": "1.0",
  "author": "test_team",
  "description": "验证GIDS设备登录API返回的IMSI、IMEI参数不为空",
  "target_service": "GIDS",
  "test_category": "功能测试",
  
  "parameter_template": {
    "imsi": {
      "type": "string",
      "required": true,
      "default": "68510155565211",
      "description": "IMSI参数"
    },
    "imei": {
      "type": "string",
      "required": true,
      "default": "6258412454025411",
      "description": "IMEI参数"
    },
    "manufacturer": {
      "type": "string",
      "required": false,
      "default": "default",
      "description": "设备厂商"
    },
    "model": {
      "type": "string",
      "required": false,
      "default": "default",
      "description": "设备型号"
    },
    "appType": {
      "type": "string",
      "required": true,
      "default": "5",
      "description": "应用类型"
    },
    "platform": {
      "type": "string",
      "required": true,
      "default": "1",
      "description": "平台类型"
    },
    "deviceType": {
      "type": "string",
      "required": true,
      "default": "1",
      "description": "设备类型"
    }
  },
  
  "test_config": {
    "gids_addr": "{{gids_addr}}",
    "timeout_ms": 5000
  },
  
  "test_steps": [
    {
      "step_number": 1,
      "step_name": "调用设备登录API",
      "step_type": "action",
      "method": "POST",
      "url": "/app-api/devicetcp/app/login/v1/gridLoginAuth",
      "request_body": {
        "imsi": "{{imsi}}",
        "imei": "{{imei}}",
        "manufacturer": "{{manufacturer}}",
        "model": "{{model}}",
        "appType": "{{appType}}",
        "platform": "{{platform}}",
        "deviceType": "{{deviceType}}"
      },
      "expected_status": 200
    },
    {
      "step_number": 2,
      "step_name": "验证IMSI不为空",
      "step_type": "verification",
      "verification_type": "not_null",
      "field": "data.token",
      "description": "验证返回的IMSI通过token字段存在"
    },
    {
      "step_number": 3,
      "step_name": "验证响应包含必要字段",
      "step_type": "verification",
      "verification_type": "contains_fields",
      "fields": ["token", "expiresTime", "timeAxis"],
      "description": "验证响应包含必要的登录字段"
    }
  ],
  
  "resource_requirements": {
    "environment": "test",
    "dependencies": ["GIDS服务"],
    "network": "内网"
  }
}
```

### 测试脚本设计

**脚本格式**: 支持多种格式,测试人员自行控制参数配置逻辑

**格式1: 平台原生JSON格式** (用于简单API测试)
```json
{
  "script_name": "GIDS设备登录参数验证-IMSI/IMEI非空检查",
  "script_type": "API",
  "script_language": "HTTP",
  "script_format": "JSON",
  "version": "1.0",
  "author": "test_team",
  "description": "验证GIDS设备登录API返回的IMSI、IMEI参数不为空",
  "target_service": "GIDS",
  "test_category": "功能测试",
  
  "test_config": {
    "gids_addr": "http://192.168.1.100:9090",
    "timeout_ms": 5000,
    "imsi": "68510155565211",
    "imei": "6258412454025411",
    "manufacturer": "default",
    "model": "default",
    "appType": "5",
    "platform": "1",
    "deviceType": "1"
  },
  
  "test_steps": [
    {
      "step_number": 1,
      "step_name": "调用设备登录API",
      "step_type": "action",
      "method": "POST",
      "url": "/app-api/devicetcp/app/login/v1/gridLoginAuth",
      "request_body": {
        "imsi": "{{gids_addr/imsi}}",
        "imei": "{{gids_addr/imei}}",
        "manufacturer": "{{gids_addr/manufacturer}}",
        "model": "{{gids_addr/model}}",
        "appType": "{{gids_addr/appType}}",
        "platform": "{{gids_addr/platform}}",
        "deviceType": "{{gids_addr/deviceType}}"
      },
      "expected_status": 200
    },
    {
      "step_number": 2,
      "step_name": "验证IMSI不为空",
      "step_type": "verification",
      "verification_type": "not_null",
      "field": "data.token",
      "description": "验证返回的IMSI通过token字段存在"
    },
    {
      "step_number": 3,
      "step_name": "验证响应包含必要字段",
      "step_type": "verification",
      "verification_type": "contains_fields",
      "fields": ["token", "expiresTime", "timeAxis"],
      "description": "验证响应包含必要的登录字段"
    }
  ],
  
  "resource_requirements": {
    "environment": "test",
    "dependencies": ["GIDS服务"],
    "network": "内网"
  }
}
```

### 执行流程设计

```
┌─────────────────────────────────────────────────────────────┐
│                     测试人员                                    │
└─────────────────────────────────────────────────────────────┘
           │
           │ 1. 编写测试脚本,自行配置参数
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  本地开发环境                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试脚本编写(参数配置在脚本中)                       │   │
│  │  ├─ JSON格式: test_config包含所有参数配置            │   │
│  │  ├─ Bash格式: 脚本变量定义参数                       │   │
│  │  ├─ Python格式: 代码中定义参数                       │   │
│  │  └─ 其他格式: 自行实现参数配置                       │   │
│  │                                                        │   │
│  │  示例(Bash脚本):                                     │   │
│  │  GIDS_ADDR="http://192.168.1.100:9090"              │   │
│  │  IMSI="68510155565211"                               │   │
│  │  IMEI="6258412454025411"                              │   │
│  │  ...                                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 2. 上传测试脚本到平台
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 脚本管理                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  上传测试脚本文件                                     │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  [选择文件]  test-script.json  test.sh      │   │   │
│  │  │                                                │   │   │
│  │  │  脚本解析结果:                                   │   │   │
│  │  │  ✓ 脚本格式: BusinessCase                      │   │   │
│  │  │  ✓ 业务用例编号: TC_SBG_DFx_License_001       │   │   │
│  │  │  ✓ 目标服务: BrowserGateway                   │   │   │
│  │  │                                                │   │   │
│  │  │                    [保存脚本]                  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 3. 脚本入库
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 脚本存储服务                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 保存脚本文件到文件系统(/data/scripts/)          │   │
│  │  2. 解析脚本元数据                                   │   │
│  │  3. 插入数据库:                                      │   │
│  │     INSERT INTO test_scripts                        │   │
│  │     (name, script_type, business_case_data, ...)    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 4. 触发执行
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 脚本执行界面                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试脚本列表                                        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ ✓ [脚本1] GIDS设备登录参数验证               │   │   │
│  │  │   格式: JSON  参数: 已在脚本中配置            │   │   │
│  │  │                    [执行] [查看]             │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │   [脚本2] License销显控一致性测试             │   │   │
│  │  │   格式: BusinessCase  参数: 已在脚本中配置    │   │   │
│  │  │                    [执行] [查看]             │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 5. 创建执行任务
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 执行引擎                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 从数据库加载脚本信息                             │   │
│  │  2. 读取脚本文件                                     │   │
│  │  3. 创建执行记录:                                    │   │
│  │     INSERT INTO script_executions (status='pending') │   │
│  │  4. 推送进度: WebSocket → status=running            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 6. 执行测试(使用脚本中的参数配置)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  执行引擎                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  根据脚本格式执行:                                    │   │
│  │                                                        │   │
│  │  格式1: JSON格式                                      │   │
│  │  - 解析test_config中的参数配置                       │   │
│  │  - 按顺序执行test_steps                              │   │
│  │  - 验证expected_result                               │   │
│  │                                                        │   │
│  │  格式2: BusinessCase格式                             │   │
│  │  - 解析business_case字段                             │   │
│  │  - 提取Test Steps/Test Steps Expected Result        │   │
│  │  - 转换为可执行步骤链                                │   │
│  │  - 执行并验证                                        │   │
│  │                                                        │   │
│  │  格式3: 可执行脚本(Bash/Python等)                    │   │
│  │  - 直接执行脚本文件                                  │   │
│  │  - 捕获stdout/stderr作为日志                         │   │
│  │  - 检查退出码(0=成功, 非0=失败)                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 7. 收集执行结果
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  结果收集服务                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  执行日志(从stdout/stderr收集):                      │   │
│  │  [INFO] 2025-04-15 10:30:00 开始执行测试脚本           │   │
│  │  [INFO] 2025-04-15 10:30:00 参数配置: GIDS_ADDR=...   │   │
│  │  [INFO] 2025-04-15 10:30:00 参数配置: IMSI=...        │   │
│  │  [INFO] 2025-04-15 10:30:01 步骤1: 调用设备登录API       │   │
│  │  [INFO] 2025-04-15 10:30:01 收到响应: 200 OK              │   │
│  │  [INFO] 2025-04-15 10:30:01 验证步骤通过                  │   │
│  │  [INFO] 2025-04-15 10:30:02 测试脚本执行完成               │   │
│  │                                                        │   │
│  │  执行结果:                                              │   │
│  │  - status: 'passed' 或 'failed'                     │   │
│  │  - exit_code: 0 或 非0                              │   │
│  │  - duration_ms: 2000                                │   │
│  │  - error_message: (失败时的错误信息)                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 8. 更新数据库
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 数据更新服务                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  UPDATE script_executions                             │   │
│  │  SET status='passed'/'failed',                        │   │
│  │      finished_at=NOW(),                                │   │
│  │      duration_ms=2000,                                 │   │
│  │      logs='/data/logs/execution_001.log',              │   │
│  │      error_message='...'                              │   │
│  │  WHERE id='exec_001'                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 9. 推送结果
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 实时监控                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  实时执行监控                                            │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  执行状态: ✓通过                                 │   │   │
│  │  │  总耗时: 2.0秒  退出码: 0                         │   │   │
│  │  │                                                │   │   │
│  │  │  实时日志:                                        │   │   │
│  │  │  > [10:30:00] 开始执行...                          │   │   │
│  │  │  > [10:30:00] 参数配置已加载                        │   │   │
│  │  │  > [10:30:01] 步骤1完成: 200 OK                    │   │   │
│  │  │  > [10:30:02] 测试完成                             │   │   │
│  │  │                                                │   │   │
│  │  │                    [查看报告] [重新执行]          │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 10. 查看报告
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 测试报告                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试报告 - exec_001                                   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  执行概览                                       │   │   │
│  │  │  状态: ✓通过  耗时: 2.0秒  退出码: 0        │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │  脚本信息                                       │   │   │
│  │  │  名称: GIDS设备登录参数验证                       │   │   │
│  │  │  格式: JSON                                      │   │   │
│  │  │  参数: 已在脚本中配置(平台不管理)               │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │  执行日志                                       │   │   │
│  │  │  [10:30:00] 开始执行...                          │   │   │
│  │  │  [10:30:01] 步骤1完成                            │   │   │
│  │  │  ...                                           │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```
**格式3: 可执行脚本** (Bash/Python/Java/Go等,测试人员自行控制参数)
```bash
#!/bin/bash
# imsi-imei-validation.sh

# 参数配置由测试人员自行控制
GIDS_ADDR="http://192.168.1.100:9090"
IMSI="68510155565211"
IMEI="6258412454025411"
MANUFACTURER="default"
MODEL="default"
APPTYPE="5"
PLATFORM="1"
DEVICETYPE="1"

# 执行测试步骤
echo "[INFO] 步骤1: 调用设备登录API"
RESPONSE=$(curl -s -X POST "${GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuth" \
  -H "Content-Type: application/json" \
  -d "{
    \"imsi\": \"${IMSI}\",
    \"imei\": \"${IMEI}\",
    \"manufacturer\": \"${MANUFACTURER}\",
    \"model\": \"${MODEL}\",
    \"appType\": \"${APPTYPE}\",
    \"platform\": \"${PLATFORM}\",
    \"deviceType\": \"${DEVICETYPE}\"
  }")

echo "[INFO] 收到响应: ${RESPONSE}"

# 验证步骤
python3 -c "
import json
import sys

resp = json.loads('${RESPONSE}')
if resp.get('code') == 200:
    print('[INFO] 步骤1通过: 200 OK')
    token = resp.get('data', {}).get('token')
    if token and len(token) > 0:
        print('[INFO] 步骤2通过: Token存在')
        sys.exit(0)
    else:
        print('[ERROR] 步骤2失败: Token不存在')
        sys.exit(1)
else:
    print('[ERROR] 步骤1失败: 非200响应')
    sys.exit(1)
"
```

**关键特性**:
- ✅ 平台不提供参数配置界面
- ✅ 测试人员在脚本中自行管理所有参数配置
- ✅ 支持多种脚本格式,测试人员自由选择
- ✅ 参数配置的灵活性和复杂度完全由脚本控制
- ✅ 平台只负责执行、日志收集和报告生成
- ✅ 支持业务侧提供的JSON用例格式

### 执行流程设计

```
┌─────────────────────────────────────────────────────────────┐
│                     测试人员                                    │
└─────────────────────────────────────────────────────────────┘
           │
           │ 1. 配置测试参数
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 参数配置管理                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试参数配置                                        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ 配置名称: 测试场景A                             │   │   │
│  │  │                                                │   │   │
│  │  │ 设备参数:                                       │   │   │
│  │  │ IMSI:      [68510155565211___________]          │   │   │
│  │  │ IMEI:      [6258412454025411_________]          │   │   │
│  │  │ 厂商:      [default______]                     │   │   │
│  │  │ 型号:      [default______]                     │   │   │
│  │  │                                                │   │   │
│  │  │ 系统参数:                                       │   │   │
│  │  │ GIDS地址: [192.168.1.100:9090______]          │   │   │
│  │  │ 超时时间: [5000___] 秒                          │   │   │
│  │  │                                                │   │   │
│  │  │                    [保存配置]                  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                │   │   │
│  │  已有配置:                                        │   │   │
│  │  • 测试场景A  [编辑] [删除]                     │   │   │
│  │  • 测试环境B  [编辑] [删除]                     │   │   │
│  │  + 新建配置                                      │   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 2. 上传测试脚本
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 脚本管理                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  上传测试脚本(JSON模板文件)                             │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  [选择文件]  imsi-imei-validation.json      │   │   │
│  │  │                                                │   │   │
│  │  │  脚本解析结果:                                   │   │   │
│  │  │  ✓ 发现7个参数占位符                             │   │   │
│  │  │  - imsi (string, 必填)                        │   │   │
│  │  │  - imei (string, 必填)                        │   │   │
│  │  │  - manufacturer (string, 可填)                │   │   │
│  │  │  - model (string, 可填)                       │   │   │
│  │  │  - appType (string, 必填)                    │   │   │
│  │  │  - platform (string, 必填)                   │   │   │
│  │  │  - deviceType (string, 必填)                  │   │   │
│  │  │                                                │   │   │
│  │  │                    [保存脚本]                  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 3. 脚本和参数入库
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 脚本和参数存储                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 保存测试脚本文件                                 │   │   │
│  │     → /data/scripts/imsi-imei-validation.json          │   │   │
│  │  → INSERT INTO test_scripts (parameter_template={...})│   │
│  │                                                        │   │   │
│  │  2. 保存参数配置                                      │   │   │
│  │     → INSERT INTO test_param_values (param_id,    │   │   │
│  │           param_value, config_name)                  │   │   │
│  │                                                        │   │   │
│  │  示例数据:                                            │   │   │
│  │  (param_id='imsi', value='68510155565211',          │   │   │
│  │   config_name='测试场景A')                             │   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 4. 选择配置并执行
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 脚本执行界面                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  执行测试脚本                                        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  脚本: GIDS设备登录参数验证                     │   │   │
│  │  │                                                │   │   │
│  │  │  选择参数配置:                                   │   │   │
│  │  │  ○ 测试场景A (当前选中)                         │   │   │
│  │  │  ○ 测试环境B                                     │   │   │
│  │  │  ○ 测试环境C                                     │   │   │
│  │  │                                                │   │   │
│  │  │  当前配置预览:                                   │   │   │
│  │  │  IMSI: 68510155565211                            │   │   │
│  │  │  IMEI: 6258412454025411                           │   │   │
│  │  │  厂商: default                                    │   │   │
│  │  │                                                │   │   │
│  │  │                    [开始执行]                  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 5. 参数注入和脚本执行
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 参数注入和执行引擎                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 加载脚本模板                                     │   │   │
│  │     script_template = 读取JSON文件                    │   │   │
│  │                                                        │   │   │
│  │  2. 加载参数配置                                      │   │   │
│  │     params[imsi] = "68510155565211"                   │   │   │
│  │     params[imei] = "6258412454025411"                  │   │   │
│  │     params[manufacturer] = "default"                 │   │   │
│  │     params[model] = "default"                         │   │   │
│  │     params[appType] = "5"                            │   │   │
│  │     params[platform] = "1"                           │   │   │
│  │     params[deviceType] = "1"                         │   │   │
│  │     params[gids_addr] = "192.168.1.100:9090"         │   │   │
│  │                                                        │   │   │
│  │  3. 参数注入(替换占位符)                             │   │   │
│  │     request_body:                                    │   │   │
│  │     {                                               │   │   │
│  │       "imsi": "{{imsi}}",        → "68510155565211"  │   │   │
│  │       "imei": "{{imei}}",        → "6258412454025411" │   │   │
│  │       "manufacturer": "{{manufacturer}}", → "default"│   │   │
│  │       ...                                             │   │   │
│  │     }                                               │   │   │
│  │                                                        │   │   │
│  │  4. 保存执行配置(包含实际参数)                        │   │   │
│  │     INSERT INTO script_executions                  │   │   │
│  │     (execution_config = 注入后的完整参数)           │   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 6. 执行测试(使用注入后的参数)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  API测试引擎                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  步骤1: 调用设备登录API (使用注入后的参数)            │   │
│  │  POST http://192.168.1.100:9090/app-api/...          │   │
│  │  Request Body: {                                       │   │
│  │    "imsi": "68510155565211",  ← 从配置读取            │   │
│  │    "imei": "6258412454025411",  ← 从配置读取            │   │
│  │    "manufacturer": "default",   ← 从配置读取            │   │
│  │    "model": "default",          ← 从配置读取            │   │
│  │    "appType": "5",              ← 从配置读取            │   │
│  │    "platform": "1",            ← 从配置读取            │   │
│  │    "deviceType": "1"           ← 从配置读取            │   │
│  │  }                                                      │   │
│  │                                                        │   │
│  │  → Response: {                                          │   │
│  │      "code": 200,                                       │   │
│  │      "msg": "success",                                   │   │
│  │      "data": {                                          │   │
│  │        "token": "8352b6da-0313-439f-9946-0a06e2fd7144",│   │
│  │        "expiresTime": 1774321223548944,                 │   │
│  │        "timeAxis": 1774317623                           │   │
│  │      }                                                   │   │
│  │    }                                                     │   │
│  │                                                        │   │
│  │  ✓ 步骤1通过(200 OK)                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 7. 生成报告(包含使用的配置参数)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 测试报告                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试报告 - exec_001                                   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  执行概览                                       │   │   │
│  │  │  状态: ✓通过  耗时: 1.5秒  执行人: admin      │   │   │
│  │  │  使用配置: 测试场景A                               │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │  使用的参数配置:                                 │   │   │
│  │  │  ├─ IMSI: 68510155565211                         │   │   │
│  │  │  ├─ IMEI: 6258412454025411                        │   │   │
│  │  │  ├─ 厂商: default                                 │   │   │
│  │  │  ├─ 型号: default                                 │   │   │
│  │  │  ├─ 应用类型: 5                                  │   │   │
│  │  │  └─ GIDS地址: 192.168.1.100:9090                 │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │  步骤详情                                       │   │   │
│  │  │  ┌─────────────────────────────────────┐   │   │   │
│  │  │  │ 步骤  │ 操作          │请求参数        │状态│   │   │
│  │  │  ├─────────────────────────────────────┤   │   │   │
│  │  │  │ 1     │ 调用登录API   │imsi=685...✓   │ ✓  │   │   │
│  │  │  │       │               │imei=625...     │    │   │   │
│  │  │  │ 2     │ 验证IMSI      │                │ ✓  │   │   │
│  │  │  │ 3     │ 验证字段      │                │ ✓  │   │   │
│  │  │  └─────────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```
┌─────────────────────────────────────────────────────────────┐
│                     测试人员                                    │
└─────────────────────────────────────────────────────────────┘
           │
           │ 1. 上传测试脚本
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 脚本管理                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  上传测试脚本(JSON文件)                                 │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  [选择文件]  imsi-imei-validation.json      │   │   │
│  │  │                                                │   │   │
│  │  │  脚本名称: GIDS设备登录参数验证               │   │   │
│  │  │  脚本类型: API                                   │   │   │
│  │  │  目标服务: GIDS                                 │   │   │
│  │  │                                                │   │   │
│  │  │                    [上传脚本]                  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 2. 脚本入库
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 脚本管理服务                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - 验证JSON格式                                     │   │
│  │  - 存储脚本文件到文件系统(/data/scripts/)          │   │
│  │  - 插入元数据到数据库:                             │   │
│  │    INSERT INTO test_scripts (...) VALUES (...)     │   │
│  │  - 插入测试步骤到数据库:                           │   │
│  │    INSERT INTO test_steps (...) VALUES (...)        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 3. 触发执行
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 脚本列表                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试脚本列表                                        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ ✓ [脚本1] GIDS设备登录参数验证               │   │   │
│  │  │   类型: API  状态: 未执行                     │   │   │
│  │  │                    [执行] [查看]             │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │   [脚本2] 文件上传测试                        │   │   │
│  │  │   类型: API  状态: 已通过                     │   │   │
│  │  │                    [执行] [查看]             │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 4. 创建执行任务
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 执行引擎                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 从数据库加载脚本配置                             │   │
│  │  2. 创建执行记录:                                    │   │
│  │     INSERT INTO script_executions (status='pending') │   │
│  │  3. 推送进度: WebSocket → status=running            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 5. 执行测试步骤
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  API测试引擎                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  步骤1: 调用设备登录API                               │   │
│  │  POST http://192.168.1.100:9090/app-api/...          │   │
│  │  Request Body: {"imsi":"68510155565211",...}          │   │
│  │                                                        │   │
│  │  → Response: {                                           │   │
│  │       "code": 200,                                       │   │
│  │       "msg": "success",                                   │   │
│  │       "data": {                                          │   │
│  │         "token": "8352b6da-0313-439f-9946-0a06e2fd7144",│   │
│  │         "expiresTime": 1774321223548944,                 │   │
│  │         "timeAxis": 1774317623                           │   │
│  │       }                                                   │   │
│  │     }                                                     │   │
│  │                                                        │   │
│  │  ✓ 步骤1通过(200 OK)                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 6. 验证测试步骤
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  验证引擎                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  步骤2: 验证IMSI不为空                                 │   │
│  │  - 检查 data.token 字段是否存在                       │   │
│  │  - 验证 token 长度 > 0                                │   │
│  │  ✓ 验证通过                                             │   │
│  │                                                        │   │
│  │  步骤3: 验证必要字段存在                               │   │
│  │  - 检查 ["token", "expiresTime", "timeAxis"]          │   │
│  │  - 所有字段都存在                                      │   │
│  │  ✓ 验证通过                                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 7. 收集结果
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  结果收集服务                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  执行日志:                                              │   │
│  │  [INFO] 2025-04-15 10:30:00 开始执行测试脚本           │   │
│  │  [INFO] 2025-04-15 10:30:01 步骤1: 调用设备登录API       │   │
│  │  [INFO] 2025-04-15 10:30:01 收到响应: 200 OK              │   │
│  │  [INFO] 2025-04-15 10:30:01 步骤2: 验证IMSI不为空         │   │
│  │  [INFO] 2025-04-15 10:30:01 验证通过: token存在            │   │
│  │  [INFO] 2025-04-15 10:30:01 步骤3: 验证必要字段存在       │   │
│  │  [INFO] 2025-04-15 10:30:01 验证通过: 所有字段存在         │   │
│  │  [INFO] 2025-04-15 10:30:01 测试脚本执行完成               │   │
│  │                                                        │   │
│  │  执行结果:                                              │   │
│  │  - status: 'passed'                                    │   │
│  │  - total_steps: 3                                      │   │
│  │  - passed_steps: 3                                     │   │
│  │  - failed_steps: 0                                     │   │
│  │  - duration_ms: 1500                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 8. 更新数据库
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  后端 - 数据更新服务                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  UPDATE script_executions                             │   │
│  │  SET status='passed',                                  │   │
│  │      finished_at=NOW(),                                │   │
│  │      duration_ms=1500,                                 │   │
│  │      logs='/data/logs/execution_001.log',              │   │
│  │  WHERE id='exec_001'                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 9. 推送结果
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 实时监控                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  实时执行监控                                            │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  执行状态: ✓通过                                 │   │
│  │  │  总耗时: 1.5秒                                    │   │   │
│  │  │  步骤: 3/3 完成                                   │   │   │
│  │  │                                                │   │   │
│  │  │  实时日志:                                        │   │   │
│  │  │  > [10:30:01] 步骤1: 调用设备登录API              │   │   │
│  │  │  > [10:30:01] ✓ 收到响应: 200 OK                │   │   │
│  │  │  > [10:30:01] 步骤2: 验证IMSI不为空               │   │   │
│  │  │  > [10:30:01] ✓ 验证通过                          │   │   │
│  │  │                                                │   │   │
│  │  │                    [查看报告] [重新执行]          │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           │ 10. 查看报告
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  前端 - 测试报告                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  测试报告 - exec_001                                   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  执行概览                                       │   │   │
│  │  │  状态: ✓通过  耗时: 1.5秒  执行人: admin      │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │  步骤详情                                       │   │   │
│  │  │  ┌─────────────────────────────────────┐   │   │   │
│  │  │  │ 步骤  │ 操作                    │状态  │ │   │   │
│  │  │  ├─────────────────────────────────────┤   │   │   │
│  │  │  │ 1     │ 调用设备登录API (200)   │  ✓   │ │   │   │
│  │  │  │ 2     │ 验证IMSI不为空           │  ✓   │ │   │   │
│  │  │  │ 3     │ 验证必要字段存在       │  ✓   │ │   │   │
│  │  │  └─────────────────────────────────────┘   │   │   │
│  │  ├─────────────────────────────────────────────┤   │   │
│  │  │  执行日志                                       │   │   │
│  │  │  [10:30:00] 开始执行...                          │   │   │
│  │  │  [10:30:01] 步骤1完成: 200 OK                    │   │   │
│  │  │  ...                                           │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 预期结果

**成功场景**:
```
✅ 脚本上传成功,元数据正确存储到数据库
✅ 测试执行成功,调用GIDS API返回200 OK
✅ 所有验证步骤通过(IMSI/IMEI参数验证有效)
✅ 执行日志完整记录到数据库
✅ 测试报告自动生成,展示执行结果
✅ 前端实时监控正确显示执行进度
```

**失败场景(用于验证错误处理)**:
```
❌ 脚本上传失败(格式错误) → 平台给出明确错误提示
❌ GIDS服务不可达 → 执行失败,记录错误日志
❌ API返回非200状态 → 步骤失败,报告显示失败原因
❌ 验证步骤失败(IMSI为空) → 测试失败,报告显示具体失败点
```

### 打样验证清单
- [ ] 支持参数正则表达式验证
- [ ] 支持参数默认值
- [ ] 支持参数分组(device/browser/test)
- [ ] 支持敏感参数隐藏(如token)

### 打样成功标准

打样场景成功的标准是:

1. ✅ **脚本能上传**: 测试人员能够成功JSON脚本文件到平台
2. ✅ **脚本能执行**: 平台能够成功解析并执行测试脚本
3. ✅ **结果能收集**: 平台能够收集并记录测试执行日志和结果
4. ✅ **报告能生成**: 平台能够自动生成并展示测试报告
5. ✅ **过程能监控**: 前端能够实时显示测试执行进度和状态
6. ✅ **失败能处理**: 测试失败时能够明确显示失败原因和日志

**打样时间规划**:
- 脚本上传功能: 3-5天
- 执行引擎实现: 5-7天
- 结果收集和报告: 3-4天
- 前端界面开发: 5-7天
- 集成测试和调试: 3-5天
- **总计**: 约20-30个工作日(4-6周)

### 扩展路径

从打样场景出发,可以按以下路径扩展更多测试场景:

**阶段1: 基础API测试** (当前打样)
- ✅ GIDS设备登录参数验证
- → GIDS文件上传/下载测试
- → BrowserGateway预打开浏览器测试
- → 辅助功能API测试(授权、证书等)

**阶段2: E2E测试** (引入Mobile服务)
- 集成mobile项目,模拟虚拟UE设备
- E2E场景: YouTube搜索、BBC视频播放
- 通过WebSocket实时展示虚拟设备画面

**阶段3: 复杂场景** (组合测试)
- 用户登录流程(多个API组合)
- 文件操作流程(上传+验证+下载+删除)
- 视频播放全流程(打开+播放+控制+关闭)

**阶段4: 特定场景** (基于实际需求)
- 限流验证(并发请求)
- 主备倒换(数据库切换过程中的测试)
- 异常处理(服务不可达、网络超时等)

---

## 技术栈总结

| 层次 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | React 18.x | UI框架 |
|      | Ant Design 5.x | UI组件库 |
|      | TypeScript | 类型安全 |
|      | Vite | 构建工具 |
|      | Axios | HTTP客户端 |
|      | React Router DOM | 路由管理 |
|      | WebSocket API | 实时通信 |
| 后端 | Python 3.10+ | 编程语言 |
|      | FastAPI | Web框架 |
|      | SQLAlchemy | ORM框架 |
|      | AsyncPG/psycopg2 | PostgreSQL异步数据库驱动 |
|      | subprocess/asyncio | 调用测试框架CLI |
|      | websockets | 实时通信 |
|      | python-jose | JWT认证机制 |
| 数据库 | PostgreSQL | 关系型数据库 |
| 部署 | Docker | 容器化部署(可选) |
|      | Nginx | 反向代理 |
|      | Systemd/Gunicorn | 服务管理 |

## 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       自动化测试看护平台概览                              │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐              ┌──────────────────┐
  │   测试人员       │              │   开发人员       │
  │   (查看/执行)    │              │   (查看结果)     │
  └────────┬─────────┘              └────────┬─────────┘
           │                                 │
           ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           浏览器                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                  React + Ant Dashboard                             │ │
│  │  ├─ 自动化测试用例列表 (查看/筛选/搜索)                             │ │
│  │  ├─ 一键执行功能 (单个/批量)                                       │ │
│  │  ├─ 执行监控页面 (实时日志/进度)                                    │ │
│  │  ├─ 测试报告查看 (统计/步骤/详情)                                   │ │
│  │  ├─ E2E测试监控 (实时画面/进度)                                     │ │
│  │  └─ 系统设置 (用户/配置)                                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
           │ HTTP/WebSocket
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          API网关(Nginx)                                 │
└─────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          后端测试平台                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                   Go + Gin API Server                               │ │
│  │  ├─ 认证中间件 (JWT)                                               │ │
│  │  ├─ 测试用例API (查看/导入)                                         │ │
│  │  ├─ 测试执行API (触发/停止/监控)                                    │ │
│  │  ├─ 测试报告API (查询/展示)                                         │ │
│  │  ├─ 执行引擎 (调用测试框架CLI)                                      │ │
│  │  └─ WebSocket服务 (实时推送执行进度)                                │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                       Worker池 (执行引擎)                            │ │
│  │  Worker1  Worker2  Worker3  Worker4  Worker5                        │ │
│  │  ├─ 调用 mvn test / go test                                      │ │
│  │  ├─ 调用 curl API测试                                             │ │
│  │  └─ 调用 Playwright Go (E2E)                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
           │ 调用                              │ 查看元数据
           ▼                                  ▼
┌──────────────────┐            ┌──────────────────┐
│   被测系统       │            │   测试数据库     │
│  BrowserGateway  │            │   PostgreSQL      │
│  GIDS           │            │  ┌────────────┐  │
│  MediaCache     │            │  │automation  │  │
│                 │            │  │ _tests     │  │
│                 │            │  │executions  │  │
│                 │            │  │reports     │  │
│                 │            │  │e2e_sessions│  │
│                 │            │  │users       │  │
│                 │            │  │configs     │  │
│                 │            │  └────────────┘  │
└──────────────────┘            └──────────────────┘
           ▲
           │ 测试代码存储
┌──────────────────┐
│   Git仓库       │
│  (测试代码)     │
└──────────────────┘
```
┌─────────────────────────────────────────────────────────────────────────┐
│                          测试平台概览                                    │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐              ┌──────────────────┐
  │   测试人员       │              │   开发人员       │
  └────────┬─────────┘              └────────┬─────────┘
           │                                 │
           ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           浏览器                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                  React + Ant Dashboard                             │ │
│  │  ├─ 测试用例管理 (列表/详情/导入导出)                               │ │
│  │  ├─ 测试执行管理 (执行/监控/日志)                                   │ │
│  │  ├─ 测试报告查看 (统计/步骤/详情)                                   │ │
│  │  ├─ E2E测试监控 (实时画面/进度)                                     │ │
│  │  └─ 系统设置 (用户/配置)                                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
           │ HTTP/WebSocket
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          API网关(Nginx)                                 │
└─────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          后端服务                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                   Go + Gin API Server                               │ │
│  │  ├─ 认证中间件 (JWT)                                               │ │
│  │  ├─ 测试用例API (CRUD/导入导出)                                    │ │
│  │  ├─ 测试执行API (执行/停止/监控)                                   │ │
│  │  ├─ E2E测试引擎 (Playwright/任务调度)                              │ │
│  │  └─ WebSocket服务 (实时推送)                                       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                       Worker池                                      │ │
│  │  Worker1  Worker2  Worker3  Worker4  Worker5                        │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
           │                                │
           ▼                                ▼
┌──────────────────┐            ┌──────────────────┐
│   测试数据库     │            │   被测系统       │
│   PostgreSQL      │            │  BrowserGateway  │
│  ┌────────────┐  │            │  GIDS           │
│  │test_cases  │  │            │  MediaCache     │
│  │executions  │  │            └──────────────────┘
│  │e2e_sessions│  │
│  │users       │  │
│  │configs     │  │
│  └────────────┘  │
└──────────────────┘
```### 打样验证清单

**平台核心能力验证**:
- [ ] 测试脚本上传功能
- [ ] 多脚本格式支持(JSON/BusinessCase/Bash/Python等)
- [ ] 业务JSON用例格式解析
- [ ] 可执行脚本执行能力(Bash/Python/Java/Go)
- [ ] 测试脚本执行引擎
- [ ] API测试能力(HTTP请求/响应验证)
- [ ] 测试步骤执行和验证
- [ ] 执行日志收集和存储(从stdout/stderr)
- [ ] 执行结果数据库更新
- [ ] 测试报告自动生成
- [ ] 实时监控和进度推送
- [ ] 前端脚本管理界面
- [ ] 前端执行监控界面
- [ ] 前端测试报告界面

**非功能验证**:
- [ ] 用户登录和认证
- [ ] 后端API响应时间(< 500ms,不包括实际测试执行)
- [ ] 前端界面响应友好
- [ ] 数据库事务一致性
- [ ] 错误处理和异常捕获
- [ ] 日志记录完整性
- [ ] 脚本文件安全性(路径遍历防护)
- [ ] 执行隔离性(不同脚本不互相影响)
- [ ] 资源释放(执行后清理)

**关键设计验证**:
- [x] 平台不提供Web参数配置界面
- [x] 测试人员在脚本中自行控制参数配置
- [x] 参数配置的灵活性和复杂度完全由脚本控制
- [x] 平台只负责执行、日志收集和报告生成
- [x] 支持业务侧提供的JSON用例格式