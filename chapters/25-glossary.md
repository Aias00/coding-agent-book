# 附录 A 接口速查、参数起点与设计自检

## 一次模型步需要固定的对象

| 对象 | 必要字段 | 主要用途 |
|---|---|---|
| TaskSpec | 目标、范围、验收、预算 | 定义完成标准 |
| PreparedRequest | 消息、工具、模型配置、revision | 确定实际请求 |
| ToolPlan | schema、runtime、版本 | 绑定声明与执行 |
| Invocation | call、参数、执行目标、权限 | 表达真实行动 |
| Grant | 行动摘要、策略版本、期限 | 执行准入 |
| ToolOutcome | 状态、效果、内容、证据 | 结果接纳与恢复 |
| Checkpoint | 有效历史边界、机器状态 | 恢复执行 |
| ContextReceipt | 选入项、裁剪项、预算 | 解释模型可见内容 |

这些字段是设计速查，不是已经稳定发布的跨项目标准。实现时需要对 JSON、进程、文件与网络边界进行验证，同进程受信类型边界则避免无意义重复检查。

## 建议参数起点

| 参数 | 教学或首版起点 | 调整依据 |
|---|---|---|
| 模型步上限 | 8，跨同一任务恢复累计 | 任务复杂度与无效循环 |
| 工具并发 | 2，独占调用单独运行 | 资源、延迟、冲突 |
| 文本读取上限 | 单次 64 KiB | 模型预算与文件分布 |
| 授权短票据 | 60 秒，执行前复核 | 排队时长与风险 |
| 日志写入 | 短事务，先提交再发布终态 | 故障与吞吐 |
| 大输出保留 | 头尾预览与完整产物 | 诊断需求与存储 |
| 取消收敛 | 分工具配置，不承诺回滚 | 工具可取消性 |

前四项可在本书参考程序中看到，其余是方案要求。数字不是四个项目的共同默认值，也不是生产推荐值；部署前应以任务与故障集校准。

## 十四个细节自检

1. 同一逻辑 step 重试时是否重复认领用户输入？正确设计复用认领事实，只有新请求版本按规则接纳新输入。
2. 工具参数解析成功但响应 length 截断，是否执行？保守实现拒绝，因为行动可能不完整。
3. 审批之后 hook 改参数怎么办？重新校验并重新授权，不能沿用旧摘要。
4. 等待锁期间 grant 过期怎么办？取得资源后复核，拒绝过期授权。
5. 两个读取完成乱序，下一请求历史如何排列？按定义的稳定顺序，UI 进度可另行展示。
6. 文件哈希匹配是否等于原子 compare-and-swap？不是，仍需并发控制并说明外部写者竞态。
7. shell 已启动，是否能无限发送 stdin？不能，后续输入也可能产生新效果。
8. 工具输出被脱敏，能否把行动标为未执行？不能，真实效果与内容可见性分开。
9. 压缩摘要能否说“测试通过”但没有验证事件？不能将模型摘要作为唯一机器证据。
10. result committed 但 WebSocket 失败怎么办？按持久序号重放，不重跑工具。
11. dispatched 无 result 是否直接重试？按 replay policy；不安全动作先核对或阻塞。
12. 子代理 worktree 是否隔离全部资源？不是，端口、网络、凭据仍需管理。
13. 租约过期能否保证旧 worker 不再写？仅靠期限不够，需要 fencing 或其他执行限制。
14. 会话分支回退能否自动撤销文件修改？不能，代码回滚是独立授权动作。

## 术语简表

Harness 是模型周围的运行框架。Actor 是一个有序状态推进者。Projection 是从事实记录推导消费者状态。Attempt 是实际请求尝试。Replay 是重建或重跑，使用时说明含义。Idempotency 是业务重复请求不重复产生效果。Fencing 是以单调令牌拒绝旧执行者。Artifact 是完整输出、diff、截图等可引用产物。Scope 是注册范围。Disposer 是资源撤销操作。

不要把“有日志”“有沙箱配置”“有重试”“有多个 agent”当作最终保证。每个保证都需要条件、执行位置和失败行为。

## 源码按问题阅读

循环与步骤：〔C01〕〔C02〕〔D02〕〔P01〕〔A03〕。工具与调度：〔C03〕〔C05〕〔C06〕〔D03〕〔D05〕〔P02〕〔A04〕〔A05〕。上下文与恢复：〔C08〕〔C09〕〔D04〕〔D07〕〔D11〕〔P05〕〔P06〕〔P12〕〔A07〕〔A10〕。插件与权限：〔D09〕〔D14〕〔D15〕〔P09〕〔P10〕〔A06〕〔A11〕。

先明确要实现的约束，再看对应文件的接口、调用点、失败分支和测试。这样能够学到可迁移的设计，而不仅是记住当前目录布局。

## 增订专题的函数地图

| 问题 | 源码入口 | 证据 |
|---|---|---|
| Skill 目录怎样暴露给模型 | Pi formatSkillsForPrompt；DeepSeek tool-skill pre-step | 〔P19〕〔D23〕 |
| Skill 来源和范围怎样合并 | DeepSeek SkillRegistry | 〔D24〕 |
| MCP 工具怎样转成普通工具 | DeepSeek syncTools、createMcpToolDefinition | 〔D27〕 |
| MCP 连接和初始发现谁管理 | DeepSeek mcp-client.apply | 〔D25〕 |
| 直接、延迟和程序入口怎样选择 | Pi McpExposure；Codex spec_plan | 〔P20〕〔C11〕 |
| 压缩什么时候发生 | Pi shouldCompact；DeepSeek compactIfNeeded；Claude shouldAutoCompact | 〔P06〕〔D19〕〔A07〕 |
| 摘要是否更小、历史是否仍兼容 | DeepSeek summarizeCompaction、稳定性检查 | 〔D21〕 |
| 服务端压缩与窗口重置怎样区分 | Codex run_auto_compact 的分支 | 〔C01〕〔C17〕〔C19〕 |
| 压缩后怎样恢复 Skill 与 MCP 指令 | Claude compactConversation | 〔A09〕 |
| 审批与升级重试如何衔接 | Codex ToolOrchestrator.run | 〔C05〕 |
| 哪些限制不能被普通扩展放开 | DeepSeek prepareExecution、guardReason | 〔D05〕 |
| hook 与权限流程如何改变输入 | Claude checkPermissionsAndCallTool | 〔A06〕 |
| bypass 模式仍检查哪些规则 | Claude checkRuleBasedPermissions | 〔A11〕 |
| 文件策略与真实执行后端怎样分离 | DeepSeek SandboxPolicyService、sandbox-local | 〔D28〕〔D29〕〔D30〕 |
| 升级权限时如何保留禁止读取 | Codex unsandboxed_execution_allowed | 〔C12〕 |
| Linux 沙箱如何启动 | Codex LinuxSandboxCommand | 〔C22〕 |
| 工具 runtime 持有哪些本次执行信息 | Codex ToolRuntime、SandboxAttempt | 〔C12〕 |
| 取消发生前正文是否已经执行 | DeepSeek dispatchToolBody、cancellationResult | 〔D05〕 |
| 请求等待与进程寿命如何分开 | Codex exec_command_inner；Pi createLocalShellOperations | 〔C07〕〔P17〕 |
| 项目 trust 管什么 | Pi resolveProjectTrusted | 〔P09〕 |
| 沙箱 adapter 与外部依赖怎样衔接 | Claude wrapWithSandbox | 〔A18〕 |

第 15 章比较的是这些可检查的客户端设计。摘要准确率、实际费用和真实任务成功率没有统一实验依据，不提供数值排名。
