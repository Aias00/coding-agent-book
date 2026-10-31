# 第 15 章 上下文压缩：四份源码的实现、边界与取舍

## 阅读口径：先看实际实现，再作方案判断

本章以固定本地快照为依据：Codex `57d4fac64adb`、DeepSeek Harness `687f282e8625`、Pi `16f5f0af4d85`，以及 Claude Code 2.1.88 发布包。先说明各自触发、切分、摘要与安装路径，再比较设计，最后提出本书的组合方案。源码事实、分析判断与实现建议分别标明。

压缩主要改变下一请求的有效上下文。原始记录如何保留、恢复时如何重建，要看各项目的日志与投影实现；不能统一理解为删除聊天记录，也不能把所有名为 compaction 的分支都理解为一次模型摘要。

## Pi：从有效会话投影切分，追加摘要记录

### 触发与 token 估算

源码调用主线是 `AgentSession._checkCompaction()` → `_runAutoCompaction()` → `prepareCompaction()` → `compact()` → `SessionManager.appendCompaction()`，随后刷新模型上下文。自动检查还区分普通阈值、上下文溢出及可恢复的长度截断；已成功结束的回答与需要继续的失败响应，其重试行为不同。溢出恢复有一次 compact-and-retry 的保护，防止相同恢复不断循环。〔P04〕

`shouldCompact()` 的实际条件为：

```text
contextTokens > contextWindow - reserveTokens

默认 reserveTokens    = 16,384
默认 keepRecentTokens = 20,000
```

使用量优先取有效助手响应中的 usage，再加上其后新增消息的估计。`estimateProjectedContextTokens()` 还会检查 usage 所在位置与后续 context edit、compaction 的关系。如果旧 usage 已不能代表当前投影，就重新估算，避免刚压缩完又被历史大数字触发。〔P06〕

一个容易误读的细节：`reserveTokens` 用于触发余量，不是这里传给摘要请求的输出上限。`generateSummaryWithUsage()` 中保留了 `_reserveTokens` 参数，但注释和实现说明它不再用于这个目的；摘要输出按模型调用配置处理。〔P06〕

### 保留边界与长回合拆分

`prepareCompaction()` 先构造 `buildSessionProjection()`，找到最近有效摘要，再通过 `findProjectedCutPoint()` 从尾部累计 token，选择保留起点。边界依据模型可见消息，而不是简单按磁盘记录数量切一半。〔P06〕

`isCutPointMessage()` 不接受 toolResult。允许在带工具调用的 assistant 消息之前切，这样后面的工具结果也会保留。Pi 同时允许切进一个长回合内部：`isSplitTurn` 为真时，把更早历史与当前回合前缀分开总结，再合并为一份摘要；根据实际历史，可能需要两次摘要调用。〔P06〕

```text
较早历史 → history summary
当前回合已压缩前缀 → turn-prefix summary
当前回合后半段 → 保留原文
```

因此“所有项目都只能按完整用户回合压缩”不符合这份源码。

### 摘要生成与持久化

Pi 把待总结消息转换并序列化为文本，放入 `<conversation>`；已有摘要通过 `<previous-summary>` 交给模型更新。提示要求固定 Markdown 板块：Goal、Constraints & Preferences、Progress、Key Decisions、Next Steps、Critical Context。它不是上一版通用方案中展示的 JSON 对象，也不能仅因提示规定格式就认为输出已经通过严格结构解析。〔P06〕

`compact()` 会补入读取、修改文件列表；长度截断或错误响应不能作为正常摘要提交，试图调用工具的摘要也会被拒绝。`completeSummarization()` 使用可见的重试入口，并设置 `cacheRetention: "none"`；不能据此推导所有缓存行为，但能确认摘要请求采用了明确的独立策略。〔P06〕

结果通过 `appendCompaction()` 追加到会话树，包含 summary、firstKeptEntryId、tokensBefore、details、usage 和有效 systemMessage。之后 `buildContextEntries()` 选取最新压缩记录、从 firstKeptEntryId 起保留的旧记录，以及压缩后新增记录。原始会话仍可保留，有效模型历史由投影选择。〔P05〕

设计判断：Pi 的路径直观，适合作为第一版实现起点。长回合切分比必须保留整回合更灵活，旧 usage 失效检查也很实用；代价是切分与历史投影仍有复杂边界，双摘要可能增加等待与成本。

## DeepSeek Harness：受约束的 surface 替换

### 两个自动入口与真实阈值

`BasicCompactionEngine` 在 `agent/pre-step` 检查压力，在 `agent/request-error` 处理 provider 确认的上下文溢出。普通压力路径先尝试可选的 toolResultPruner，重新测量，仍然超限才调用摘要；裁剪已经足够时不会继续付出摘要调用成本。〔D19〕

`resolveCompactSpec()` 的公式是：

```text
messageBudget = contextWindow - reservedCompletionTokens
threshold = floor(min(
  contextWindow * thresholdRatio,
  messageBudget - headroomTokens
))
retainTokens = floor(messageBudget * retainRatio)
```

默认 thresholdRatio 为 0.8，retainRatio 为 0.16，headroomTokens 为 65,536；也可直接配置保留 token 数，或按模型覆盖策略。普通压力测量达到阈值后进入处理；provider 溢出恢复绕过普通阈值与保留尾部政策，尝试一次有用的平衡缩减。〔D20〕〔D19〕

设计判断：公式把窗口、输出预留和额外空间一起考虑，比固定百分比更明确。但默认 headroom 不能不加判断地移植。例如窗口 128,000、输出预留 8,000 时，阈值为 54,464，明显早于窗口 80%；较小窗口需要重新校准参数。无效预算会作为配置错误处理，不能把这套默认值说成普遍最优。

### 切分、摘要与缓存前缀

`selectCompactableRange()` 跳过 surface 开头的 system/message，从尾部按价格累计保留内容，并调用配对检查避免把 assistant 工具请求和结果切开。所选的是当前有效 surface，不是随意删除一段原始事件。〔D21〕

`summarizeWithLlm()` 保留原系统消息、工具声明和选定对话前缀，再在最后追加一条 user-role 压缩指令。源码注释说明，这是为了复用已有请求前缀缓存；实际是否命中仍取决于路由与供应商。〔D22〕

它要求 Markdown 检查点，包含用户意图、关键技术、文件代码、错误修复、待办、当前工作、下一步和关键上下文。输出只提取可接受的文本，空摘要与不完整终态不能正常提交。已有检查点会被合并更新，而非要求原封不动复制。〔D22〕

### 成功条件与日志提交

`summarizeCompaction()` 计算带包装 checkpoint 的 token 价格，要求它严格小于被替换片段；否则报错。`compactSurfaceRegion()` 在异步摘要后再次检查稳定性：自动路径要求 whole-surface 一致，手动路径检查 selected-span 仍在、连续、价格一致且边界平衡。〔D21〕

提交按生命周期记录：

```text
compaction/start
→ 生成并检查摘要
→ compaction/summary
→ user/message，携带 surfaceOp: replace
→ compaction/end
```

这是日志记录与有效 surface 替换机制，不应直接称为任意存储事务。失败时尝试记录关闭标记；若关闭失败，未匹配 start 仍可被检测。手动压缩还提供明确 flush 检查点。模型可见消息改变，原始事件依然用于追溯。〔D21〕

溢出恢复还有一个细节：前面的无模型裁剪可能已经产生持久缩减，即使后续摘要失败，只要 replacement generation 确实前进，代码仍可按限制重试。没有缩减证据时，不会仅凭“尝试过压缩”就盲目重试。〔D19〕

设计判断：在本章核对的客户端流程中，它对大小、配对、历史稳定性和失败证据的约束最值得借鉴。但这些机械检查不能证明摘要没有漏掉业务约束，语义保真仍需任务实验。

## Codex：先识别三条分支

### 压缩入口并不只有一种行为

`run_auto_compact()` 首先检查 Feature::TokenBudget，然后根据 provider 的 remote_compaction 能力选择远程 V2 或本地路径。触发可以发生在回合前、回合中或回合后，具体条件结合 token status、配置和已准备好的后台候选。〔C01〕

| 分支 | 本地代码能确认的行为 |
|---|---|
| TokenBudget | 跳过模型/服务端总结，调用 start_new_context_window |
| RemoteCompactionSupport::V2 | 接收服务端压缩项，筛选保留项并安装历史 |
| Unsupported | 通过本地摘要调用构造替代历史 |

因此不能给 Codex 统一套上“生成一段自然语言摘要，再保留最近对话”的描述。〔C19〕〔C17〕〔C08〕

### 本地摘要的保留规则

`run_compact_task_inner_impl()` 克隆历史，追加压缩提示，消费摘要响应。若压缩请求本身仍超限，会从最旧历史项开始移除再尝试；某些取消、预算或不完整响应错误直接结束对应路径。〔C08〕

生成摘要后，`build_compacted_history()` 从最近用户消息向前，在 20,000 token 的预算中挑选保留，再加入摘要，并重建初始上下文、world state 和窗口元数据，最后 `replace_compacted_history()`。这条保留规则侧重用户消息，不等于 Pi 那种保留最近完整消息尾部。〔C08〕〔C09〕

设计判断：保留用户需求原文有利于维持任务方向，但较早的具体工具轨迹更依赖摘要。对排错任务是否更好，需要检查压缩后是否还能使用必要错误和代码证据。

### 远程 V2 与后台候选

远程路径接收 `ResponseItem::Compaction`，其可见类型含 encrypted_content。`build_v2_compacted_history()` 按消息类型和 feature 筛选保留项，以 64,000 token 预算裁剪，再追加服务端压缩项。服务端内部摘要如何编码、是否比文本摘要保真，仅靠本地客户端源码无法确认。〔C17〕〔C21〕

后台候选也不能直接安装：`take_ready()` 检查历史 generation；安装路径检查模型 slug 与 comp_hash，兼容性不符返回不安装。这是合理的异步优化约束：预先计算的结果必须仍然对应当前历史和模型。〔C20〕〔C18〕

设计判断：这些版本与候选检查值得迁移到自建系统；远程摘要质量不纳入本章排名。TokenBudget 的窗口轮换又是另一类目标，不能与有损摘要质量直接比较。

## Claude Code：分层缩减与压缩后的工作状态恢复

### 请求前的处理次序

本节依据本地 2.1.88 发布包提取实现，受构建和 feature gate 控制的路径不视为所有用户默认启用。`queryLoop()` 中可见：工具结果预算处理 → 可选 snip → microcompact → 可选 context collapse → autocompact。每层可能缩减上下文，完整摘要不是唯一策略。〔A03〕

`microcompactMessages()` 先尝试时间触发路径。符合条件时保留近期可压缩工具结果，把较早结果正文替换成清理标记，调用身份仍然存在。cached 路径则通过 API 层 cache edits 管理服务端缓存中的结果，不直接改写本地消息正文。条件不满足时，这个入口可以直接返回原消息。〔A08〕

时间触发配置默认 enabled=false、间隔 60 分钟、保留 5 项，可由运行配置控制。不能因为源码有一段缓存优化，就断言当前产品一定使用它。〔A17〕

### 完整自动压缩与失败限制

不计环境覆盖时，默认阈值计算为：

```text
effectiveWindow = contextWindow - min(modelMaxOutputTokens, 20,000)
autoCompactThreshold = effectiveWindow - 13,000
```

`autoCompactIfNeeded()` 先判断开关、调用来源与阈值，尝试 session memory compaction，没有可用结果时进入 compactConversation。完整自动压缩连续失败达到 3 次后跳过后续尝试，避免每轮重新执行无效请求。不同 feature 路径还有各自控制，不能把某一分支当作全部实现。〔A07〕

### 摘要以后为什么还要恢复附件

`compactConversation()` 运行 PreCompact hooks，生成摘要并处理过长请求重试；成功后准备部分文件附件、异步 agent 状态、计划及计划模式、已调用 Skill 内容，重新提供延迟工具、Agent 和 MCP instructions 等信息。已发现的延迟工具名还记录到 boundary metadata，供后续 schema 筛选继续使用。〔A09〕

最终 `buildPostCompactMessages()` 以确定次序组合：

```text
boundaryMarker
+ summaryMessages
+ 可选 messagesToKeep
+ attachments
+ hookResults
```

这解释了压缩与能力管理的关系：摘要能表达“正在发布”，但当前有效 Skill 的操作要求、已加载的工具和 MCP 指令仍需要恢复位置。完整 Skill 目录也不会无条件重新注入，源码专门区分目录与已使用 Skill 内容。〔A09〕

设计判断：工作状态恢复是这里最值得借鉴的产品设计。但恢复内容也占窗口，源码因此单独估算 truePostCompactTokenCount，并记录可能再次触发压缩。不能只看摘要正文很短，就认为下一请求已经足够小。〔A09〕

## 依据代码比较：哪个环节更合理

下面是基于已检查客户端代码的工程判断，不是实际成功率或价格排名。

| 目标 | 更值得参考的部分 | 同时付出的代价 |
|---|---|---|
| 第一版容易实现和排错 | Pi 的准备、切分、摘要、追加与投影 | 仍需处理长回合、usage 失效与摘要调用成本 |
| 压缩替换可检查、失败可解释 | DeepSeek 的配对、变小、稳定性及日志标记 | token 定价与 surface 一致性实现更复杂，默认预算需校准 |
| 压缩后继续原有工作方式 | Claude Code 的 Skill、工具、文件与 MCP 恢复 | 附件增加输入，门控与缓存状态复杂 |
| 异步预压缩与服务端集成 | Codex 的候选版本、模型兼容与安装 | 依赖 provider，服务端内部保真无法本地验证 |

缓存方面，Pi 的独立文本摘要与 DeepSeek 的原请求前缀复用采用不同策略。前缀复用有减少重复计算的设计动机，但实际 token、缓存命中、路由差异及摘要次数需要实测；不能只凭接口断言哪一家更便宜。

固定 Markdown 格式也不等于事实验证。源码中能看到长度、终态、配对和稳定性检查，但这些不能证明“计划跑测试”没有被摘要错误写成“测试已通过”。需要用压缩后继续任务的结果评估语义损失。

## 本书建议：按清晰内核逐项补强

本节是设计建议。可以从 Pi 式的清晰流程起步，加入 DeepSeek 的实际缩小与历史稳定性检查，按 Claude Code 的思路恢复当前任务必要的能力信息，需要后台优化时再加入 Codex 式候选兼容检查。它不是四个项目之一已经提供的一份统一实现。

建议将强事实与摘要分开：已修改文件、验证结果和未知调用由执行记录提供；模型摘要说明目标、思路与背景。下面字段是一种可选设计，不是前述项目共有的真实 schema：

```text
Checkpoint {
  source_history_version, summarized_range, kept_from,
  summary, effective_prompt_state, tool_plan_revision,
  verification_refs[], unresolved_calls[], evidence_refs[]
}
```

权限与执行范围由运行时保持，摘要中的“已经允许”不直接产生授权。摘要提交失败保留旧输入；候选失效拒绝安装；恢复旧测试证据时检查对应代码版本。

验收时至少注入：用户最新限制、已修改版本、失败测试、未知调用、长工具输出和已加载 Skill。压缩后确认没有越界修改、重复动作、丢失待办、误判验证或失去必要能力。语义验证与格式检查分别报告，才能知道改进发生在哪个层面。
