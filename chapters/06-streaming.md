# 第 6 章 流式协议：字节、内容块与可执行行动

## 四个完成时刻必须区分

网络 chunk 完成、SSE event 完成、工具参数块完成、整个模型响应完成是四个不同事件。网络可能把一段 UTF-8 字符拆成两次读取，也可能一次返回多条 SSE。不能对每个网络 chunk 直接 `json.loads`，更不能把当前已解析出的参数立即交给执行器。

建议管线：增量字节解码器 → 协议事件解析器 → 内容块 assembler → 完整调用校验 → 调度器。每层维护自己的缓冲与限制，并用明确结束条件把数据交给下一层。

## SSE 解析器需要处理什么

教学伪代码：

```text
decoder.feed(bytes, final=False) -> decoded_text
append text to line_buffer
while a complete line exists:
  process CRLF / LF
  if empty line: dispatch accumulated event
  else if line begins with ':': ignore heartbeat
  else collect data/event/id fields
```

多条 data 行应按协议拼接；空行才终结一个 event。连接结束时必须检查不完整行和不完整响应，不能默认为成功。设置 event 最大长度、参数累计长度及总响应大小，避免恶意或异常服务让缓冲无限增长。

## 工具参数如何累计

assembler 以稳定的内容块身份或 provider index 保存 name、id、argument fragments 和结束标志。文本片段可立即展示，参数片段只供预览。遇到明确的工具块完成事件，才对完整 JSON 做一次最终解析与 schema 校验。

若每来一个字符就重解析完整累计 JSON，参数长度 n 的总开销可能接近平方级。DeepSeek 的 pi-ai adapter 文档专门记录了增量参数处理与相关补丁背景，说明大参数会把协议细节变成事件循环性能问题。〔D18〕

增量 JSON 解析可以用于早期提示，但不能把“目前能修复成一个对象”当作最终参数。Pi 在输出长度截断时拒绝执行该响应中的工具调用，正是因为语法可恢复不保证行动完整。〔P01〕

## 是否在整个响应结束前执行工具

保守方案等 ResponseComplete 后才接受调用，状态简单。低延迟方案在完整工具块就绪后提前执行，但必须面对后续流失败：同一响应回退或重试时，之前的工具可能已经产生效果。Claude Code 的 StreamingToolExecutor 有丢弃、取消与合成结果机制，可作为复杂度参考。〔A05〕

建议先只对被严格分类的读取启用早执行；写入仍等完整响应。即便读取早执行，也要记录它属于哪个 attempt，后续回退后其结果能否进入有效历史。不能因为“只读”就忽略信息泄露、资源消耗或远程查询计费。

## UI 增量与持久事实怎样协调

使用临时 `attempt_id` 发布 start/chunk/end，提交后再附上稳定消息身份。UI 看见 committed end 才把临时节点升级为确定消息；abandoned end 应清楚表示中断或回退。DeepSeek 的实时流与 assistant/message、assistant/attempt 结算可提供参考。〔D04〕

不要把每个字符都作为一次独立数据库事务。可以保留最后结算的完整流、批量写 chunk，或仅在产品确实要求断电恢复到字符级时采用更强存储。不同策略的恢复精度不同，必须写进承诺。

## 背压与慢消费者

模型流消费者如果等待每次 WebSocket 发送，慢客户端会拖慢执行；如果无限缓冲，又可能耗尽内存。推荐把执行事实与 UI 扇出分开，UI 增量队列有界，溢出时合并文本或要求客户端通过快照恢复。工具终结与授权请求不能像普通字符那样随意丢弃。

每个订阅端用事件序号恢复，不依赖“我已经收到第几个字符”作为全局游标。持久序号与临时 revision 可以并存，但必须标明各自有效期。

## 必做的协议测试

对同一条合法响应按所有字节位置切分，assembler 最终结果应相同；把多条事件合并到一个 chunk 也应相同。再测试半截多字节字符、重复块结束、工具缺少 id、响应 length 截断、连接无终态关闭和取消。任何不完整状态都不能静默变成可执行写操作。
