# 第 7 章 工具协议：声明、校验、授权与结果终结

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
