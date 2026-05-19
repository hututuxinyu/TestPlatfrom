## 新增需求

### 需求：覆盖率埋点追踪

系统 SHALL 在 Debug 模式下对 GIDS 和 BGW 业务关键函数进行入口/出口埋点，输出统一格式的覆盖率日志。

#### 场景：GIDS 函数埋点

**场景：GIDS AuthService.CheckIMEI 函数执行**
- **WHEN** GIDS 以 Debug 模式启动
- **AND** 测试脚本调用 CheckIMEI 函数
- **THEN** 系统输出日志 `[COVERAGE] FUNC enter|AUTH-002|CheckIMEI|imei=xxx`
- **AND** 函数返回后输出日志 `[COVERAGE] FUNC exit|AUTH-002|CheckIMEI|success=true`

**场景：GIDS 函数执行异常**
- **WHEN** GIDS 函数执行抛出异常
- **THEN** 系统输出日志 `[COVERAGE] FUNC exit|FUNC_ID|success=false|error=xxx`

#### 场景：BGW AOP 拦截

**场景：BGW Service 层方法拦截**
- **WHEN** BGW 以 Debug 模式启动
- **AND** 任何 Service/Adapter 层方法被调用
- **THEN** Aspect 拦截器自动记录方法进入和退出
- **AND** 输出统一覆盖率日志格式

#### 场景：覆盖率收集器

**场景：批量收集覆盖率数据**
- **WHEN** 测试执行完成
- **THEN** 收集器 SHALL 汇总所有 CoverageHit 记录
- **AND** 支持导出为 JSON 格式供测试平台解析
