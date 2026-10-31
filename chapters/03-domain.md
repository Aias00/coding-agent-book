# 第 3 章 领域模型：身份、版本与必须成立的不变量

## 给不同生命周期不同身份

建议至少定义 `session_id`、`turn_id`、`step_id`、`attempt_id`、`call_id`、`artifact_id`。一次用户任务 turn 可以包含多个模型 step；一次逻辑 step 可以有多个网络 attempt；一次助手响应可以提出多个 call。身份不应从文本内容或数组下标临时猜测。

```text
Session(version, active_turn, workspace_id)
Turn(id, status, input_claims, budget, stop_reason)
Step(id, request_revision, tool_plan_revision, attempts[])
Attempt(id, stream_status, finish_reason, usage)
ToolCall(id, step_id, ordinal, name, arguments, status)
```

恢复时保留逻辑 `call_id`；真实重新派发用新的 execution attempt 身份。否则一个调用经历两次尝试，会在日志里伪装成两个互不相关的动作。服务端 request id 是补充关联，不应替代本地身份。

## 消息与事件不是同一种对象

事件记录发生过的事实，例如输入已认领、请求已冻结、工具已派发。消息是从这些事实投影出的模型对话。UI 进度也是投影，可以有短暂状态；不能反过来把 React 节点或终端输出当作会话格式。

设计事件 envelope：

```text
Event {
  session_id, seq, event_id, schema_version,
  kind, turn_id?, step_id?, call_id?,
  payload, timestamp, causation_id?
}
```

`seq` 在会话内严格递增，负责重放顺序；时间戳供展示和分析，不用来修复乱序。跨机器时钟会漂移，同一毫秒也可能有多个事件。`causation_id` 指向触发原因，不应与去重键混为一谈。

## 七条核心不变量

1. 一份有效助手工具请求，每个 call 最终必须有可解释的结果或未知状态。
2. 未完成的工具参数不能进入派发阶段。
3. 执行使用的参数与权限必须对应批准的内容。
4. 同一会话的有效历史由一个有序写入者推进。
5. 提供给模型的历史必须能够由已记录事实和明确投影规则重建。
6. 已提交调用结果不能因普通重试被重复执行或悄悄覆盖。
7. 任务完成必须符合定义好的验证条件，不能只依据助手自述。

不变量比类名更重要。不同代码语言可以采用不同类型结构，但必须能指出每条约束在哪里检查。

## 工具结果如何表达部分成功

不要只返回 `success: bool`。建议：

```text
ToolOutcome {
  call_id, status: ok | error | cancelled | unknown,
  content[], structured?, artifacts[],
  effect: none | applied | possibly_applied,
  error_code?, retry_hint?, evidence[]
}
```

编辑成功但 diff 生成失败，可以有 `effect=applied` 与错误信息；远程响应丢失可以是 `status=unknown`。框架需要保留这类事实，模型也应收到具体恢复建议。一个字符串异常无法表达这些区别。

## 版本需要绑定到决策

工具 schema、工作区策略、模型能力和上下文都可能变化。准备请求时固定它们的 revision，审批时记录相关版本，提交时检查会话 expected version。版本不一定全用递增整数：文件可以用内容哈希，schema 可用规范化表示的摘要，策略可以用持久配置版本。

文件哈希表示你读到的内容，不代表工作区全部文件都没变化。若验证依赖多个文件，需要记录相应 read set 或工作树版本。精确说明版本覆盖范围，才能避免把局部一致误当作全局快照。

## 参考实践与验收

Codex 将工具运行绑定到步骤上下文；DeepSeek Harness 把 turn/step 与事件关联；Pi 用 parentId 表示有效分支；Claude Code 区分短暂 progress 与记录链。它们都说明身份与投影属于核心执行模型。〔C06〕〔D08〕〔P05〕〔A10〕

验收时构造重复 call id、不同参数的相同 id、失配的审批版本和重复事件提交。系统必须明确拒绝或幂等处理，不能依赖“模型一般不会这样输出”。
