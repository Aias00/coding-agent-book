# 第 7 章 工具协议：声明、校验、授权与结果终结

## 模型看见声明，运行时保留实现

源码事实：Codex 的 `ToolRouter` 同时持有注册表、模型可见 specs、tool mode 和 code mode 名称映射。Pi 的 agent-core 则在请求边界通过 `declareToolChanges()` 对比可执行工具与 transcript 已声明集合，记录新增和移除。两种方式都在处理同一个关系：模型收到的使用说明，应与运行时实际能解释的工具一致。〔C03〕〔C11〕〔P01〕

模型侧通常接收名称、描述与参数 schema；handler、连接、凭据与执行上下文由宿主保存。下面是本书的概念示例，字段不是某一家模型 API 的完整请求格式：

```json
{
  "name": "read_file",
  "description": "读取工作区中的文本文件",
  "inputSchema": {
    "type": "object",
    "properties": { "path": { "type": "string" } },
    "required": ["path"],
    "additionalProperties": false
  }
}
```

模型据此提出 `read_file({path: "src/main.ts"})`。真正读取文件的是宿主根据名称查到的 handler。调用必须携带可关联身份，结果用相同身份回到模型历史，供下一次生成使用。模型输出一段看起来像调用的普通文本，不应被当作已经执行；实际入口由 adapter 的结构化响应解析与工具路由确定。

## 已安装、会话可用与本轮暴露分开管理

本书建议区分三份集合：已安装能力、当前会话允许的能力、本次请求实际声明的能力。筛选涉及身份、scope、执行环境、模型支持和任务策略。集合的变化应形成新的工具计划，不能仅修改一段提示词就假定执行限制也改变。

源码事实：Pi 的 `McpExposure` 定义四种暴露模式，含义如下。配置层在这里保存定义，连接与实际接入由相应扩展负责；不能把这个配置文件当作完整 MCP 执行实现。〔P20〕

| 模式 | 模型与运行时的关系 |
|---|---|
| direct | 工具作为普通工具声明，code mode 也可使用 |
| deferred | 先通过 tool_search 加载，再允许模型直接调用 |
| codemode | 通过程序入口调用，脚本可用 searchTools 查找；不直接声明每个工具 |
| hidden | 已登记但不可达 |

Codex 的 `spec_plan` 也区分 direct、deferred、code-mode-only 与 hidden 等 exposure，并结合模型搜索能力和配置决定最终暴露。具体枚举和组合与 Pi 不完全相同，不能认为这些名称构成通用标准。〔C11〕

延迟发现的收益是减少每次请求携带的 schema；代价是额外搜索往返，以及“已发现”“已声明”“当前可执行”三个状态必须保持一致。隐藏工具还需要执行入口实际拒绝，不能只期望模型忘记工具名称。

## Runtime 不只是一个 execute 函数

本书讨论的工具 runtime 是宿主对调用生命周期的管理层，不等同于 Node.js、Python 或容器运行时。它接纳模型提议，联系具体实现与执行环境，管理取消和结果；权限系统与沙箱分别承担决策和真实资源约束。

| 层次 | 回答的问题 | 不能单独保证什么 |
|---|---|---|
| 权限系统 | 这个身份能否执行这项行动 | 获准程序运行时不会越界 |
| 沙箱 | 程序实际可以触及哪些资源 | 该行动符合用户业务意图 |
| 工具 runtime | 调用怎样准备、执行、结束和清理 | 任意后端都具备相同隔离能力 |

源码事实：Codex 的 `ToolRuntime<Req, Out>` 组合 `Approvable` 与 `Sandboxable`，除 `run()` 外还提供 turn_environment、执行器是否自行管理进程沙箱、网络审批和 sandbox_cwd 等入口。`run()` 接收 `SandboxAttempt`，其中携带本次权限、沙箱选择、工作区根、网络代理及取消相关信息。因此同一工具的不同尝试可以采用不同执行权限，而不是把全部上下文塞进一个全局变量。〔C12〕

DeepSeek 的 `ToolRegistry.execute()` 统一调用准备、派发、后处理和最终结果路径，调度器通过内部 staged 接口控制阶段衔接。普通工具与监听器失败会形成错误结果；最终返回的是与观察者收到的一致的冻结结果快照。该快照约束并不自动保证外部服务副作用事务化。〔D05〕

Pi 的 `prepareToolCall()` 依次查找工具、准备并验证参数、运行 beforeToolCall；被 block 或已取消时返回即时错误结果。`runToolCall()` 复用准备、执行与 afterToolCall，适合作为直接调用和程序化调用的共同入口，但函数本身不追加消息或发送循环事件，调用方仍需负责历史接纳。不能把这里的 hook 接口直接说成内置的完整审批系统。〔P01〕

设计判断：Pi 的小内核容易理解；DeepSeek 的分阶段接口适合扩展与调度组合；Codex 的尝试对象适合把审批、隔离和多种执行环境联系起来。选择取决于宿主需要管理的执行复杂度，不是接口越多，任务效果就越好。

## ToolDefinition 应该包含哪些字段

```text
ToolDefinition {
  name, version, description, input_schema, output_schema?,
  effect_class, concurrency_class, replay_policy,
  timeout_policy, interrupt_policy, output_limits,
  prepare?, execute, reconcile?, present?
}
```

`effect_class` 描述读写与外部效果，`concurrency_class` 描述能否重叠，两者不同。`replay_policy` 说明中断后能否重跑，`reconcile` 说明怎样查询已发生效果。产品呈现使用 `present` 或独立 renderer；无 UI 执行仍能理解结构化结果。

Claude Code 的 Tool 同时表达并发、只读、中断和结果大小；Pi 的调用钩子提供统一执行路径；Codex 的工具计划将声明与运行时一起确定。〔A04〕〔P02〕〔C11〕

## 注册表必须生成不可变工具计划

每次请求形成 `ToolPlan(revision, declarations, runtimes)`。模型看到哪个 schema，这批调用就按哪个版本解释。扩展加载后新工具只影响下一份计划。卸载若发生在调用途中，需要等待持有运行时的调用结束，或明确取消，不能把同名新实现直接套到旧参数上。

重复名称应拒绝或显式命名空间化，不使用“最后注册覆盖前者”的隐式规则。工具发现可以延迟，但调用时必须检查该工具是否在当前可授权集合，不能从所有已安装工具里随意兜底。

## 校验分成三层

第一层检查 JSON 结构与类型，拒绝未知字段或按明确兼容规则规范化。第二层检查语义：路径存在、旧文本唯一、命令参数组合有效。第三层检查权限：身份和范围是否允许。三层的失败需要不同错误码，模型才能选择修正参数、重新读取或请求授权。

不要在校验器中执行真实副作用。例如“验证连接”若顺便创建远程资源，尚未授权就已经行动。准备步骤若必须联网，应把这项查询视为独立受控能力。

## 规范化必须发生在审批之前

模型可能用相对路径、旧字段或字符串化数组表达参数。允许兼容时，先规范化到执行器实际使用的形式，再生成摘要和审批指纹。审批后 hook 若改参数，需要重新校验与重新授权。不能让用户看到旧参数、执行器运行新参数。

建议保存原始参数和规范化参数的受控引用，并记录转换版本。日志中的敏感内容要脱敏，但审批绑定使用完整规范化摘要，避免脱敏后多个不同动作碰撞成相同展示。

## 工具调用管线的精确顺序

```text
resolve(plan, name)
→ parse and normalize
→ schema + semantic validation
→ extensible pre-policy
→ mandatory guard
→ approve actual invocation
→ acquire execution resources
→ recheck expiring conditions
→ persist dispatch
→ execute
→ post-policy / content finalization
→ commit result
→ publish committed event
```

准备、权限询问可能等待很久；取得执行资源后重新检查授权有效期和文件前置条件。mandatory guard 只能收紧，不应被普通插件的 allow 覆盖。DeepSeek 的管线拆分与 guard 机制可参考。〔D05〕〔D06〕

## 后处理不能抹掉真实效果

post-policy 可以阻止敏感内容进入模型，但不能因为输出被隐藏就把已发生写入标成未执行。结果至少分开 `effect` 与 `content visibility`。如果工具成功，呈现器失败，仍然需要提交成功效果和呈现错误，不能让模型以为应该重跑。

结构化输出与文本需要一致。钩子修改文本并脱敏时，同步处理 structured payload 与产物；否则敏感值可能仍在另一个字段。Pi 的结果覆盖说明强调了这类字段关系。〔P02〕

## 错误结果的推荐形式

```json
{
  "status": "error",
  "code": "PRECONDITION_CHANGED",
  "effect": "none",
  "message": "文件在读取后发生变化",
  "next_action": "重新读取，再生成修改"
}
```

错误不应包含隐式指令让模型自动绕过限制。权限拒绝建议请求缺少的范围或停止；未知结果建议核对；参数错误建议修正。工具执行异常要分类，不能把所有异常都转成可安全重试。

## 验收要求

准备一个嵌套工具，内部调用另一个受限工具，确认仍走同一授权管线。测试未知名称、版本变化、审批后参数修改、钩子重写、输出后处理失败和重复结果提交。协议越统一，越容易保证新增能力没有绕过核心约束。
