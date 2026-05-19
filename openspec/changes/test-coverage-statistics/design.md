## 技术方案设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           测试覆盖率统计架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      业务服务 (Debug 模式)                          │   │
│  │                                                                  │   │
│  │  ┌─────────────┐                      ┌─────────────┐             │   │
│  │  │    GIDS    │                      │     BGW     │             │   │
│  │  │    (Go)    │                      │   (Java)   │             │   │
│  │  │             │                      │             │             │   │
│  │  │ Service层   │                      │ @Aspect     │             │   │
│  │  │ 埋点日志   │                      │ 自动拦截    │             │   │
│  │  └──────┬──────┘                      └──────┬──────┘             │   │
│  │         │                                    │                    │   │
│  │         │ [COVERAGE] 格式日志                  │                    │   │
│  │         │                                    │                    │   │
│  └─────────┼────────────────────────────────────┼────────────────────┘   │
│            │                                    │                        │
│            ▼                                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      日志收集层                                    │   │
│  │  ┌─────────────────┐    ┌─────────────────┐                       │   │
│  │  │  GIDS 日志文件  │    │  BGW 日志文件   │                       │   │
│  │  │  (stdout/file) │    │  (log4j2)      │                       │   │
│  │  └────────┬────────┘    └────────┬────────┘                       │   │
│  │           │                    │                                │   │
│  │           └────────────┬────────┘                                │   │
│  │                        │                                          │   │
│  │                        ▼                                          │   │
│  │              ┌─────────────────────┐                             │   │
│  │              │   Log Agent       │                             │   │
│  │              │ (测试平台拉取/推送) │                             │   │
│  │              └─────────┬──────────┘                             │   │
│  └────────────────────────┼────────────────────────────────────────┘   │
│                           │                                            │
│                           ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      测试平台                                      │   │
│  │                                                                  │   │
│  │  ┌─────────────────┐    ┌─────────────────┐                       │   │
│  │  │  覆盖率目录管理   │    │   覆盖率报告     │                       │   │
│  │  │  (YAML 配置)    │    │   生成服务      │                       │   │
│  │  └────────┬────────┘    └────────┬────────┘                       │   │
│  │           │                       │                               │   │
│  │           └───────────┬───────────┘                               │   │
│  │                       ▼                                           │   │
│  │              ┌─────────────────┐                                  │   │
│  │              │   Web Dashboard │                                  │   │
│  │              └─────────────────┘                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 一、GIDS (Go) 埋点实现

#### 1.1 覆盖率日志库

```go
// src/common/coverage/coverage.go

package coverage

import (
    "fmt"
    "sync"
    "time"
)

// CoverageHit 记录一次命中
type CoverageHit struct {
    FuncID      string    // 函数唯一标识
    ServiceName string    // 服务名
    MethodName  string    // 方法名
    EnterTime  time.Time // 进入时间
    ExitTime   time.Time // 退出时间
    Success    bool      // 是否成功
}

// Collector 覆盖率收集器
type Collector struct {
    mu    sync.Mutex
    hits  []CoverageHit
    enable bool
}

// 全局收集器
var globalCollector = &Collector{enable: false}

// SetEnable 开关控制
func SetEnable(enable bool) {
    globalCollector.mu.Lock()
    defer globalCollector.mu.Unlock()
    globalCollector.enable = enable
}

// RecordEnter 记录函数进入
func RecordEnter(funcID, serviceName, methodName string) {
    globalCollector.mu.Lock()
    defer globalCollector.mu.Unlock()
    if !globalCollector.enable {
        return
    }
    globalCollector.hits = append(globalCollector.hits, CoverageHit{
        FuncID:      funcID,
        ServiceName: serviceName,
        MethodName:  methodName,
        EnterTime:  time.Now(),
    })
}

// RecordExit 记录函数退出
func RecordExit(funcID string, success bool) {
    globalCollector.mu.Lock()
    defer globalCollector.mu.Unlock()
    if !globalCollector.enable {
        return
    }
    // 找到对应的 enter 记录，更新
    for i := len(globalCollector.hits) - 1; i >= 0; i-- {
        if globalCollector.hits[i].FuncID == funcID && globalCollector.hits[i].ExitTime.IsZero() {
            globalCollector.hits[i].ExitTime = time.Now()
            globalCollector.hits[i].Success = success
            break
        }
    }
}

// GetHits 获取所有命中记录
func GetHits() []CoverageHit {
    globalCollector.mu.Lock()
    defer globalCollector.mu.Unlock()
    result := make([]CoverageHit, len(globalCollector.hits))
    copy(result, globalCollector.hits)
    return result
}

// Clear 清空记录
func Clear() {
    globalCollector.mu.Lock()
    defer globalCollector.mu.Unlock()
    globalCollector.hits = nil
}
```

#### 1.2 日志输出封装

```go
// 在 logger 包中添加 Coverage 方法

func Coverage(format string, args ...interface{}) {
    if !coverageEnabled {
        return
    }
    log.Printf("[COVERAGE] "+format, args...)
}

// 使用示例
func (a *AuthServiceImpl) CheckIMEI(imei string, checkType string) (bool, error) {
    logger.Coverage("FUNC enter|%s|%s|imei=%s", "AUTH-002", "CheckIMEI", imei)
    defer logger.Coverage("FUNC exit|%s|%s|success=%v", "AUTH-002", "CheckIMEI", err == nil)

    // 业务逻辑
    ...
}
```

#### 1.3 需要埋点的函数列表

| 函数 ID | Service | Method | Category |
|---------|---------|--------|----------|
| AUTH-001 | AuthService | ExportIMEIList | 认证管理 |
| AUTH-002 | AuthService | CheckIMEI | 认证管理 |
| AUTH-003 | AuthService | ImportIMEIList | 认证管理 |
| AUTH-004 | AuthService | IsEscape | 认证管理 |
| BROWSER-001 | BrowserService | CreateBrowser | 浏览器管理 |
| BROWSER-002 | BrowserService | DeleteBrowser | 浏览器管理 |
| BROWSER-003 | BrowserService | GetBrowserStatus | 浏览器管理 |
| LOGIN-001 | LoginController | GridLoginAuth | 登录认证 |
| LOGIN-002 | LoginController | GridLoginAuthOpenBrowser | 登录认证 |

### 二、BGW (Java) 埋点实现

#### 2.1 AOP 切面

```java
// src/main/java/com/huawei/browsergateway/aspect/CoverageAspect.java

package com.huawei.browsergateway.aspect;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class CoverageAspect {
    private static final Logger log = LoggerFactory.getLogger(CoverageAspect.class);
    private static final String COVERAGE_PREFIX = "[COVERAGE]";

    // 拦截 service 包下所有方法
    @Pointcut("execution(* com.huawei.browsergateway.service..*(..))")
    public void servicePointcut() {}

    @Around("servicePointcut()")
    public Object around(ProceedingJoinPoint point) throws Throwable {
        String className = point.getTarget().getClass().getSimpleName();
        String methodName = point.getSignature().getName();
        String key = className + "." + methodName;

        // 入口打点
        log.info("{} FUNC enter|{}", COVERAGE_PREFIX, key);

        long startTime = System.currentTimeMillis();
        Throwable exception = null;

        try {
            return point.proceed();
        } catch (Throwable t) {
            exception = t;
            throw t;
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            String status = exception != null ? "error" : "success";
            log.info("{} FUNC exit|{}|duration={}|status={}",
                    COVERAGE_PREFIX, key, duration, status);
        }
    }
}
```

#### 2.2 拦截范围

| Package | 说明 |
|---------|------|
| `com.huawei.browsergateway.service.*` | Service 层所有类 |
| `com.huawei.browsergateway.adapter.*` | Adapter 层所有类 |

### 三、测试平台功能设计

#### 3.1 覆盖率目录管理

```
┌─────────────────────────────────────────────────────────────────┐
│                     覆盖率目录管理                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  服务选择: [GIDS ▼]  [+ 添加函数]                                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 函数ID    │ 服务名         │ 方法名      │ 分类     │ 操作 │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ AUTH-001 │ AuthService   │ ExportIMEI │ 认证管理 │ 编辑 │  │
│  │ AUTH-002 │ AuthService   │ CheckIMEI   │ 认证管理 │ 编辑 │  │
│  │ BROWSER- │ BrowserService│ CreateBr.. │ 浏览器   │ 编辑 │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2 覆盖率报告页面

```
┌─────────────────────────────────────────────────────────────────┐
│                     测试覆盖率报告                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  测试用例: TC_SBG_Func_GIDS_001_004                            │
│  执行时间: 2026-04-21 10:00:00 ~ 10:05:00                      │
│  状态: ✅ 成功                                                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ API 覆盖率: 18/25 (72%)                                 │    │
│  │ ████████████████████████████████████░░░░░░░░           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 业务函数覆盖率: 22/40 (55%)                             │    │
│  │ ████████████████████████░░░░░░░░░░░░░░░░░░░░          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  未覆盖函数 (建议补充测试场景):                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ⚠️ AUTH-004 AuthService.IsEscape                       │    │
│  │    建议: 增加退出逃生场景测试                             │    │
│  │ ⚠️ BROWSER-002 BrowserService.DeleteBrowser          │    │
│  │    建议: 增加浏览器关闭场景测试                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 四、日志格式规范

#### 4.1 统一格式

```
[COVERAGE] <EVENT>|<FUNC_ID>|<FUNC_NAME>|<EXTRA>
```

| 字段 | 说明 |
|------|------|
| EVENT | 事件类型: `enter`(入口), `exit`(出口) |
| FUNC_ID | 函数唯一标识 |
| FUNC_NAME | 函数名称 |
| EXTRA | 额外信息 (可选) |

#### 4.2 示例

```bash
# GIDS
[COVERAGE] FUNC enter|AUTH-002|CheckIMEI|imei=6258412454025411
[COVERAGE] FUNC exit|AUTH-002|CheckIMEI|success=true|duration=120ms

# BGW
[COVERAGE] FUNC enter|AuthServiceImpl|exportIMEIList
[COVERAGE] FUNC exit|AuthServiceImpl|exportIMEIList|duration=45ms|status=success
```

### 五、日志收集方案

#### 5.1 方案 A: 测试平台拉取 (推荐)

```
测试执行完成
    │
    ▼
GIDS/BGW 日志文件 (stdout/stderr)
    │
    ▼
测试平台 API 获取日志
    │
    ▼
解析 + 生成报告
```

**优点：** 实现简单，无需额外组件
**适用场景：** 本地测试、K8s Job 场景

#### 5.2 方案 B: 日志推送

```
GIDS/BGW (Debug 模式)
    │
    ├── 日志文件 ────▶ Filebeat ────▶ Elasticsearch
    │                                      │
    │                                      ▼
    │                                 Logstash
    │                                      │
    │                                      ▼
    └─────────────────────────────▶ 测试平台解析服务
```

**优点：** 实时性好
**适用场景：** 生产环境长期监控

### 六、数据模型

```go
// 覆盖率目录项
type CoverageItem struct {
    ID          string `json:"id"`           // 函数唯一标识
    ServiceName string `json:"service_name"` // 服务名
    MethodName  string `json:"method_name"`  // 方法名
    Category    string `json:"category"`     // 分类
    Description string `json:"description"`   // 描述
}

// 覆盖率命中记录
type CoverageHit struct {
    FuncID     string    `json:"func_id"`
    HitCount   int       `json:"hit_count"`
    FirstHit   time.Time `json:"first_hit"`
    LastHit    time.Time `json:"last_hit"`
}

// 覆盖率报告
type CoverageReport struct {
    TestID       string            `json:"test_id"`
    TestName     string            `json:"test_name"`
    TotalFuncs   int               `json:"total_funcs"`
    HitFuncs    int               `json:"hit_funcs"`
    CoverageRate float64          `json:"coverage_rate"`
    Hits         []CoverageHit     `json:"hits"`
    Missed       []CoverageItem    `json:"missed"`      // 未覆盖函数
    GeneratedAt  time.Time        `json:"generated_at"`
}
```

### 七、实施计划

| 阶段 | 工作内容 | 优先级 |
|------|---------|--------|
| 1 | GIDS 覆盖率埋点库开发 | P0 |
| 2 | GIDS 关键函数埋点 | P0 |
| 3 | BGW AOP 切面开发 | P0 |
| 4 | 测试平台覆盖率目录管理 | P1 |
| 5 | 测试平台日志解析服务 | P1 |
| 6 | 测试平台覆盖率报告展示 | P1 |
| 7 | 与现有测试执行流程集成 | P2 |
