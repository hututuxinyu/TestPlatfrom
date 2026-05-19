## 背景与问题

当前测试平台执行脚本后，仅能验证脚本本身的成功/失败状态，无法评估测试对业务代码的覆盖程度。当测试失败时，难以快速定位是业务代码问题、测试场景缺失还是环境问题。

缺乏测试覆盖率统计导致：
1. 不知道测试用例覆盖了哪些业务函数
2. 难以发现未覆盖的业务场景
3. 测试质量无法量化评估

## 解决方案

采用埋点日志 + Debug 模式方案，在业务关键函数入口/出口打点，执行测试后收集日志分析覆盖率。

### 核心技术选型

| 组件 | 技术方案 | 说明 |
|------|---------|------|
| GIDS (Go) | 函数入口/出口埋点 | 在关键 Service 方法加 Coverage 日志 |
| BGW (Java) | AOP Aspect 拦截 | 统一拦截 service 层方法，自动打点 |
| 日志收集 | 结构化日志文件 | [COVERAGE] 标记统一格式 |
| 覆盖率解析 | 测试平台解析服务 | 解析日志，匹配目录，生成报告 |
| 覆盖率目录 | YAML 配置 | 定义所有需统计的业务函数 |

### 埋点日志格式

```bash
# GIDS 日志示例
[COVERAGE] FUNC enter|AUTH-001|CheckIMEI|imei=6258412454025411
[COVERAGE] FUNC exit|AUTH-001|CheckIMEI|success=true

# BGW 日志示例
[COVERAGE] FUNC enter|AuthServiceImpl|exportIMEIList
[COVERAGE] FUNC exit|AuthServiceImpl|exportIMEIList
```

### 覆盖率目录结构

```yaml
# coverage_catalog.yaml

gids:
  - id: AUTH-001
    service: AuthService
    method: ExportIMEIList
    category: 认证管理
    description: 导出IMEI白名单列表

  - id: AUTH-002
    service: AuthService
    method: CheckIMEI
    category: 认证管理
    description: 校验IMEI有效性

  - id: BROWSER-001
    service: BrowserService
    method: CreateBrowser
    category: 浏览器管理
    description: 创建浏览器实例

bgw:
  - id: BG-001
    class: ChromeApi
    method: deleteUserData
    category: 用户数据管理
    description: 删除用户数据

  - id: BG-002
    class: ChromeApi
    method: initBrowser
    category: 浏览器管理
    description: 初始化浏览器
```

## 实现内容

### 1. GIDS (Go) 埋点实现

**新增文件：**
- `src/common/coverage/coverage.go` - 覆盖率埋点核心库
- `src/common/coverage/catalog.go` - 覆盖率目录管理

**改动文件：**
- `src/service/auth_service.go` - AuthService 方法埋点
- `src/service/browser_service.go` - BrowserService 方法埋点
- 其他关键 Service 方法埋点

### 2. BGW (Java) 埋点实现

**新增文件：**
- `src/main/java/com/huawei/browsergateway/aspect/CoverageAspect.java` - AOP 切面
- `src/main/java/com/huawei/browsergateway/coverage/CoverageCollector.java` - 收集器
- `src/main/resources/coverage_catalog.yaml` - 覆盖率目录

### 3. 测试平台功能增强

**新增功能：**
- 覆盖率目录管理页面（配置 GIDS/BGW 需统计的函数）
- 测试执行时日志收集配置
- 覆盖率报告展示页面
- 未覆盖函数建议功能

## 影响范围

| 模块 | 影响 | 说明 |
|------|------|------|
| GIDS | 代码改动 | 在关键函数加埋点日志 |
| BGW | 代码改动 | 添加 AOP Aspect |
| 测试平台 | 新增功能 | 覆盖率管理、报告展示 |
| 运维 | 日志收集 | 需配置日志收集到测试平台 |

## 非功能需求

1. **Debug 模式可控**：通过配置开关控制，默认关闭
2. **性能影响**：Debug 关闭时无性能影响
3. **日志规范**：统一 [COVERAGE] 标记，便于过滤解析
4. **可扩展**：目录配置化，新增函数只需更新配置
