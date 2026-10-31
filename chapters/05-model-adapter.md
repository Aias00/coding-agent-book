# 第 5 章 模型适配层：统一语义，显式保留差异

## Adapter 应该拥有哪部分职责

模型层负责消息序列化、供应商请求、流事件解码、用量归一化和错误分类；主循环负责决定重试、接纳历史和继续执行。adapter 不应悄悄重跑工具，也不应把权限拒绝包装成一条“模型回答”。Pi 的独立模型层与 DeepSeek 的 prepared call 为划分责任提供了参考。〔P15〕〔D02〕

设计接口可以采用：

```text
prepare(route, capabilities, request) -> BoundRequest
stream(BoundRequest, attempt_id, cancellation) -> AsyncIterator<ModelEvent>

ModelEvent = TextDelta | ToolArgumentsDelta | ToolCallComplete
           | UsageUpdate | ResponseComplete | ResponseFailed
```

`BoundRequest` 保存实际 provider、模型、端点类别、序列化参数与能力决定。prepare 后若路由变化，必须重新准备并记录，不能只改 HTTP URL。

## 能力矩阵不能压成一个 supports_tools

至少记录：工具调用协议、是否支持并行调用、是否允许中途系统提示更新、图片放在哪些角色、结构化输出形式、上下文窗口、输出上限、缓存字段和取消方式。某些能力可由 provider 配置声明，某些只能由模型目录确认；未知时使用保守路径。

例如模型 A 支持在历史尾部更新工具声明，模型 B 要求每次请求携带完整当前工具表。内部历史可以相同，wire format 需要不同。adapter 应用规则并记录有损转换，不能让循环去判断十几种供应商字段。

## Provider 消息转换必须保持调用配对

内部历史中 assistant 的工具调用与后续 tool result 通过 `call_id` 关联。转换时不可因为裁剪、角色合并或错误过滤而留下孤立结果。供应商可能要求每个调用都有结果，或对结果顺序有额外约束。归一化层应先检查内部协议，再根据供应商约束分组。

对于不支持的内容，应明确选择拒绝、转换成可识别的文本引用或换路由。不要静默删除图片后继续宣称模型“看过截图”。转换记录应说明内容被怎样表达，但不复制敏感二进制到普通审计日志。

## 错误分类决定后续动作

| 错误 | adapter 输出 | 循环一般怎样处理 |
|---|---|---|
| 网络瞬断、服务暂忙 | transient，是否已收到有效流 | 按预算退避重试 |
| 参数或协议错误 | invalid_request | 修正序列化或停止 |
| 上下文超限 | context_overflow | 压缩后新建请求版本 |
| 凭据失效 | authentication | 更新凭据或阻塞 |
| 速率限制 | rate_limit + 可用等待信息 | 等待或换路线，计入总期限 |
| 用户取消 | cancelled | 收敛，不按普通故障重试 |

不要根据错误文本里是否包含某个英文单词决定全部行为。优先使用结构化状态；无法确定错误类别时保留 unknown，不把所有 4xx 都当作不可重试，也不把所有异常都当作网络问题。

## 隐藏重试会破坏可观察性

HTTP 库重试两次，SDK 重试两次，循环再重试两次，可能将一次逻辑请求放大。推荐选定一个重试所有者，记录 attempt 与总预算；其他层只做明确允许的传输重连。DeepSeek 的 pi-ai 适配文档明确区分框架可见重试与 SDK 重试。〔D18〕

退避可以采用 full jitter：第 n 次取 `[0, min(cap, base×2^n)]` 内随机等待，同时受总截止时间限制。等待期间可取消，不要用不可中断的长 sleep。若服务返回 Retry-After，先验证数值与上限，再纳入调度。

## 源码细节：重试配置与执行者分开

DeepSeek 的 resolveRetryPolicy 在 provider 路由注册时生成不可变策略，执行重试的是可选 llm-retry 插件，不是仅声明配置就一定自动重试。normal 默认最多重试 5 次，初始延迟 500 ms、最大 10,000 ms、jitterRatio 0.1；默认错误集合包含空响应、RATE_LIMIT、SERVER、TIMEOUT、TRANSPORT。always 则表示持续处理模型请求失败，直到成功、取消或插件结束，不能把 normal 的次数上限套到 always。〔D32〕〔D36〕

实际 localDelay 是有上限的指数退避乘对称随机系数，再限制最大值。它并不是本章前面作为建议展示的 full jitter。第一次本地计算以 500 ms 为基准，默认约在其上下 10% 范围浮动；后续随指数增长，但不会超过上限。可用 providerRetryAfterMs 优先参与决策，normal 遇到超过最大允许等待的值会交还后续恢复链，不是随意无限等待。〔D36〕

```text
准备路由及其策略
→ 模型请求失败并记录 attempt
→ agent/request-error 恢复链
→ 记录 llm/retry
→ 可取消的等待
→ 记录 llm/retry-started
→ 返回 retry 决定
```

always 路径还先等待下游恢复：若压缩等恢复器已经决定 retry，就沿用该决定；取消优先于后续调度。代码记录重试事件后才等待，但 session append 的逻辑提交不能直接扩大为操作系统断电持久性，后者仍由存储 provider 决定。这里重试的是模型请求，不是授权对已发生工具动作重新执行。〔D36〕〔D04〕

设计判断：策略归 provider、执行归显式恢复插件，便于解释每次额外请求的来源。自建系统还需把模型、工具和整个任务的重试预算分开；always 适合什么业务应由宿主约束，不能因为单次延迟有上限就声称总费用或总等待已经有界。

## 凭据解析要晚，凭据内容不要进快照

请求配置记录 credential reference，而不是明文 key。真正发送前解析短期凭据，防止准备很久后令牌已过期。重试时可以刷新凭据，但不要把业务内容与权限范围一起无记录地修改。Pi 的循环在调用前解析 API key，体现了这一时机差异。〔P01〕

参考内核只定义 `Model.generate(Request)`，通过脚本模型验证循环。连接真实模型时实现这个接口；需要流式 UI 时再实现本章更丰富的事件协议。不要为了证明架构运行而默认调用付费服务。

## 验收细节

用记录流 fixture 验证 Unicode、工具参数、多调用、usage 缺失、错误终态和取消。断言最终 Request 的角色、工具表和调用配对，而不只比较生成文本。再验证一次上下文超限只触发有限次压缩，错误凭据不会进入无限重试。
