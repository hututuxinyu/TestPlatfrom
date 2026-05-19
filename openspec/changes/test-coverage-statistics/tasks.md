## 1. GIDS 覆盖率埋点开发

- [ ] 1.1 创建 `src/common/coverage/coverage.go` 覆盖率埋点核心库
- [ ] 1.2 在 `AuthService` 方法中添加埋点 (ExportIMEIList, CheckIMEI, ImportIMEIList, IsEscape)
- [ ] 1.3 在 `BrowserService` 方法中添加埋点 (CreateBrowser, DeleteBrowser, GetBrowserStatus)
- [ ] 1.4 在 `LoginController` 方法中添加埋点
- [ ] 1.5 添加 Debug 模式开关配置
- [ ] 1.6 更新 GIDS `main.go` 初始化覆盖率模块

## 2. BGW 覆盖率 AOP 开发

- [ ] 2.1 添加 Spring Boot AOP 依赖 (spring-boot-starter-aop)
- [ ] 2.2 创建 `CoverageAspect.java` AOP 切面类
- [ ] 2.3 配置切面拦截 service 和 adapter 包
- [ ] 2.4 添加 Debug 模式开关配置
- [ ] 2.5 创建 `coverage_catalog.yaml` 初始目录

## 3. 测试平台 - 覆盖率目录管理

- [ ] 3.1 创建覆盖率目录管理页面
- [ ] 3.2 添加目录项增删改查 API
- [ ] 3.3 支持 YAML 批量导入导出
- [ ] 3.4 添加 GIDS/BGW 服务选择器

## 4. 测试平台 - 日志收集与解析

- [ ] 4.1 添加测试执行时日志收集配置
- [ ] 4.2 创建覆盖率日志解析服务
- [ ] 4.3 实现 [COVERAGE] 日志行提取和解析
- [ ] 4.4 匹配覆盖率目录生成命中记录

## 5. 测试平台 - 覆盖率报告展示

- [ ] 5.1 创建覆盖率报告展示页面
- [ ] 5.2 显示覆盖率百分比 (总覆盖率)
- [ ] 5.3 显示已覆盖/未覆盖函数列表
- [ ] 5.4 添加覆盖率阈值告警功能
- [ ] 5.5 支持导出覆盖率报告 (PDF/HTML)

## 6. 集成与测试

- [ ] 6.1 与现有测试执行流程集成
- [ ] 6.2 测试 GIDS Debug 模式日志输出
- [ ] 6.3 测试 BGW Debug 模式日志输出
- [ ] 6.4 端到端覆盖率报告生成测试
