# 第 16 章 持久化：事务边界决定恢复能力

## 先决定哪些事实必须一起提交

完整助手消息与它的工具意图应在同一事务接纳。工具终结状态与对应结果事件也应一起提交。否则会出现历史里有工具请求、调用表没有任务，或调用表说成功、模型历史没有结果的分裂状态。

参考 schema：

```sql
CREATE TABLE sessions(id TEXT PRIMARY KEY, version INTEGER NOT NULL);
CREATE TABLE events(
  session_id TEXT, seq INTEGER, kind TEXT, payload TEXT,
  PRIMARY KEY(session_id, seq)
);
CREATE TABLE calls(
  session_id TEXT, call_id TEXT, invocation_digest TEXT,
  state TEXT, execution_attempt INTEGER, outcome_ref TEXT,
  PRIMARY KEY(session_id, call_id)
);
```

真实实现还需索引、非空约束、schema 版本和访问控制。本书可运行内核将一个数据库限定为一个会话，省去 session_id 列，但不改变事务配对的原则。

## 提交助手响应的时序

开始事务，检查 session expected version，插入 assistant settled event，为每个调用插入 intended 状态，推进版本，提交。只有提交成功，调度器才派发这些调用。若提交失败，完整响应还可以重试接纳，不能让工具先跑。

重复 `call_id` 携带不同参数必须拒绝。携带相同参数也不能无条件重复插入消息；应由命令幂等键判断这是同一次接纳重试，还是模型错误复用 id。一个“存在就忽略”的实现可能隐藏冲突。

## 派发记录先于外部动作

授权通过并取得执行资源后，提交 dispatched 及 execution attempt，再调用外部执行器。这会留下保守窗口：记录已派发但动作可能还没开始。恢复时可以查询或保守处理；反过来先执行再记 dispatched，会让真正发生的行动完全没有记录。

这个顺序不解决外部动作与本地事务的原子性，但让不确定状态可识别。第 17 章专门讨论恢复策略。

## UI 发布怎样避免数据库双写

数据库提交后发送 WebSocket，如果发送失败，事实已经存在，客户端通过 seq 重放补齐。更复杂系统可以在同一事务写 outbox，再由独立 publisher 发送。发送成功但 outbox 确认失败可能重复发送，因此消费者按 event_id 或 seq 去重。

不要声称事务 outbox 让所有网络消费者恰好收到一次。它提供可重试传递与幂等消费的基础，仍需定义顺序、保留期和游标过期处理。

## JSONL 与 SQLite 的选择

JSONL 易检查、追加与导出，但锁、损坏尾部、索引和多记录原子提交需要额外设计。SQLite 提供本地事务和索引，但连接归属、WAL 文件、备份、锁等待与版本迁移同样要管理。

Codex 的 recorder 明确区分记录、persist、flush；DeepSeek 的 JSONL provider 区分物理格式与逻辑迁移；Pi 会话树说明追加记录后仍需有效历史投影。〔C10〕〔D10〕〔D11〕〔P05〕

## 源码细节：入队、writer 屏障与断电持久性不同

Codex 的 record_canonical_items 把 AddItems 发到 writer 队列，成功返回说明队列接收了请求，不能因此认为文件已经同步。persist 和 flush 发送带 oneshot ack 的命令，等待 writer 完成对应操作；新 rollout 可以延迟物化，文件打开失败时保留待写项，之后再次尝试。writer 的屏障失败会进入恢复模式，重新打开并再试一次，第二次仍失败才返回错误。〔C10〕

write_pending_items_once 在已写项之后推进 ordinal 并移除已完成前缀；write_pending_once 最后调用文件 flush。这些操作不能与数据库多记录事务混为一谈，也不能仅凭 flush 名称推断已经执行 sync_all/fsync、承诺任意断电下不丢记录。跨进程崩溃、系统断电、文件系统故障需要分别核对保证。〔C10〕

因此本书说“提交后通知”，至少要先声明提交层级：宿主逻辑接纳、异步 writer 接收、文件写出、文件与目录同步，是不同完成时刻。控制面需要哪一级确认，应由接口返回值和具体 provider 约定，而不是 UI 看到保存图标就推导全部保证。

## 源码细节：DeepSeek 的整代迁移发布

generation.ts 针对历史 JSONL 代际准备新 artifact，先编码到临时文件并同步，再用当前格式读取验证 bytes 与 digest；发布前核对源文件物理身份，也可以复核关联子会话来源。它处理的是格式迁移，不是工具动作与日志一起原子提交。〔D10〕

POSIX 发布通过 link 将已准备文件排他地放到 currentPath，并同步目录；目标已经存在时不覆盖，而是验证已有胜出者与预期迁移前缀是否一致。Windows 使用对应发布 helper。因此不能简单描述为无条件 rename 覆盖旧日志。旧来源保留，失败阶段有独立清理逻辑。〔D10〕

catalog-migration 还记录子会话源文件的身份，检查 header 中 id、创建时间、父会话、cwd、preset 等字段，并在发布前复核 dev、ino、size 及时间等信息。单个子来源解析失败可以形成 unavailable fact；身份变化则不能静默用另一份材料完成迁移。设计判断：保存来源见证有助于检测准备期间变化，但物理身份核对不是对任意外部恶意写者的全局锁。〔D11〕

## Schema 迁移与恢复不能混为一谈

未来版本格式应由旧程序明确拒绝。支持旧格式时按版本迁移并验证，避免“字段不存在就猜默认”静默改变历史。损坏尾部是提交完整性问题，旧字段是 schema 问题，两个恢复流程分别设计。

保留原始代际并发布新代际，是 DeepSeek 提供的一种思路；数据库则可以事务迁移或导出到新库。保留旧文件不等于承诺降级可写，也不保证所有旧程序还能理解新业务事件。〔D11〕

## 备份与产物一致性

结果里引用的 diff、完整输出与截图可能在独立 artifact store。先持久产物，再在事务中引用；失败产物可以被垃圾回收，已提交引用不能指向尚未完成上传的对象。清理时根据引用与保留策略处理，不仅按文件时间删除。

备份 SQLite 时采用支持一致性的方式，不能只复制主文件而忽略活跃 WAL。恢复测试应检查事件、调用和产物都能对应，而不只是数据库能打开。

## 验收

在事务每个边界注入失败：助手已生成但未提交、意图提交后未派发、结果提交前崩溃、提交后通知失败、重复接纳和存储写满。每种情形都要能从表与事件判断下一步，不能靠日志里的自然语言猜。
