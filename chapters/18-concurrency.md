# 第 18 章 会话并发：单写者、租约、输入队列与分支

## 一个会话最好只有一个状态推进者

同一会话的模型响应、工具完成、用户纠正、审批和后台通知可以同时到达。推荐把它们送进 Session Actor 的 mailbox，由一个顺序处理者更新有效历史。工具执行可以并行，状态接纳仍有序。这比给每次 `messages.append` 加锁更容易保持跨字段不变量。

事件存储使用 expected version 防止其他进程误写。冲突时重新加载状态并判断命令是否仍适用，不是盲目重试同一个数据库 UPDATE。

## 本地锁与分布式租约的区别

单机单进程可用 actor 注册表，本地跨进程可用进程锁或数据库所有权。分布式部署使用有期限 lease，续租失败后旧 owner 停止派发。但仅有期限不够：旧进程暂停后恢复，可能不知道租约已被接管。

为此每次接管增加 fencing token。执行器或状态存储拒绝小于当前 token 的写入。若外部服务不支持 fencing，则无法仅凭控制面租约完全阻止旧 worker 的副作用，应通过代理、隔离和幂等机制补充。

参考程序用进程文件锁保证一个数据库一个活动 actor，只适用于本地文件系统，不是分布式 lease 实现。

## 输入认领的持久队列

```text
InboxItem {
  input_id, kind: steer | follow_up | context,
  payload_ref, accepted_at, claimed_by_step?, status
}
```

steer 在当前工作下一个安全边界接纳，follow_up 等当前工作自然结束，context 可以不单独唤醒模型。不同语义不要压成一个字符串队列。Pi 低层明确区分 steering 与 follow-up；DeepSeek 有统一 inbox 与下一 step 接纳；Codex 还协调 mailbox 与活动回合。〔P01〕〔D02〕〔C13〕

每次 drain 是一次认领，不应因准备前后都检查而多取输入。批量模式与一次一条模式都可行，但 API 与 UI 必须表达一致。

## 源码细节：Pi Durable 在提交边界接纳输入

prepareBoundary 在事务写入前读取当前 head 与 InboxDoc。applyBoundary 区分 postTools 和 final：选择所有 queued write，按配置选择一个或全部 steer，只有 final 才选择 follow-up；queued reset 会把 postTools 提升为 final。先安置 write，再按顺序安置所选用户项，并在同一次提交中记录 submission 对应的 entry、移除队列项。〔P13〕

旧 head 写入若指向已经离开有效范围的条目，会结算为 stale，而不是偷偷恢复被切掉的上下文。withdrawQueuedInputs 将用户项记为 unanswered 并移出队列，queued write 留待后续安置。这些边界使“输入已收到”“已放入有效历史”“本次请求已看见”成为可以区分的事实。〔P13〕

还要注意配置何时冻结。Codex 保留向模型声明工具时的 StepContext；Pi Durable 则按 task phase 解析 agent、hooks 和工具，环境按使用时构建，运行中的实现保持原有归属。后续阶段可以使用更新配置，因此第 7 章的完整不可变 ToolPlan 是本书建议，不能说所有项目都已经冻结到同一粒度。设计者需要明确请求、阶段、调用各自的版本边界。〔C06〕〔P12〕〔P22〕

## 取消与新输入如何排序

cancel 可以中止当前工作，steer 可以改变后续计划，两者不应自动等价。用户说“这次先停，换个方案”时，先记录停止当前 turn，再把新方案排入新 turn，避免旧工具结束后把结果接到新任务名下。

工具如果声明 interrupt=block，新消息先排队；interrupt=cancel 可尽快停止，但仍要收集效果。界面应显示输入已经收到和什么时候生效，不把“已排队”显示成“当前模型已经知道”。

## 分支历史与真实工作区不同步问题

会话树通过 parent_id 选当前有效分支。回到旧分支只改变模型历史，不自动回滚磁盘。Pi 的会话结构提供分支依据，Codex 的历史重建也关注有效片段和回滚边界。〔P05〕〔C09〕

切换分支后，重新读取当前工作区状态，把差异作为运行事实提供给模型。若产品提供代码回滚功能，单独执行版本控制动作并经过授权，不能把会话游标移动偷偷等同于 reset。

## UI 重连需要版本化快照

客户端携带 last_seq 订阅。若事件仍保留，发送后续；若游标过旧，返回 snapshot + snapshot_seq，再接后续事件。快照与后续读取必须避免间隙：在固定版本形成快照，之后从该序号继续，不按墙钟时间衔接。

临时流 revision 只在特定 attempt 生命周期有效，进程重启后用持久事实重建，不能承诺临时字符游标继续有效。

源码中也存在不同的重连语义。Pi Durable 的 ConversationViews.attach 在 Session 的串行线上取得当前视图并注册 observer，让它看到后续 publication；watch 受 context 取消控制。README 对视图慢消费者描述为最多保留 100 个未投递帧，超出后用最新完整视图替代；新连接从当前视图开始。它不是本章前面建议的永久 seq 事件重放接口。数字和边界属于该视图接口，不能外推到所有日志与事件消费者。〔P24〕〔P12〕

## 验收

两个进程同时打开会话应只有一个取得推进权；相同命令重复提交只认领一次；用户取消与工具完成竞态不能产生两个任务终态；旧审批不得批准新回合；断线重连能恢复 committed 状态；分支切换后不把旧代码当当前文件。
