# 第 20 章 多 Agent：分工、权限继承与结果整合

## 先判断任务是否值得拆

适合拆分的任务拥有清晰输入、独立产物和可验证结果，例如分别调查两个模块、实现互不相交的组件、独立评审一个 diff。不适合的情况是多人持续修改同一函数、子任务之间高度串行依赖，或父代理无法验证结果。

多 agent 会增加上下文复制、协调、等待和整合成本。要通过同一任务预算比较净收益，不能把同时启动数量当作能力指标。

## 委派接口需要显式任务和产物

```text
Delegation {
  task_id, parent_session_id, objective,
  input_refs[], allowed_files[], authority_ceiling,
  workspace_mode, model_profile, budget, completion_schema
}
ChildResult {
  status, artifact_refs[], changed_files[],
  verification[], unresolved_items[], evidence_refs[]
}
```

子代理输出长篇自然语言不足以支持自动整合。父代理需要知道具体文件、版本、检查和未解决事项，再决定是否接受。

## Spawn、fork 与外部委派不同

spawn 建新上下文，父代理选择必要信息；fork 继承有效历史，需要裁剪权限与无关内容；外部产品可能只支持一次执行，没有后续消息与恢复。DeepSeek 子代理服务明确区分本地可继续与外部一次性 provider。〔D13〕

接口用 capability 表达 continuation、interrupt、resume 和 structured result，不支持时拒绝。把一次新任务伪装成继续，会让用户以为子代理保留了并不存在的上下文。

## 源码细节：DeepSeek 的 fork、驻留与关闭

ForkInProcessProvider 的 completedTurnPrefix 只截取父日志到最后一个 turn/end；当前未配平的工具回合不进入 seed，尚无完整回合时从空 seed 开始。prepareContinuable 在创建时捕获一次，之后恢复子会话重放自己的记录，不重新从父代理更新后的历史再次 fork。因而 fork 不是父会话所有最新内存的实时共享。〔D35〕

SubagentManager.startLocal 在第一次 await 前捕获 descriptor、agent 配置与 delegated policies，避免创建途中父配置变化混入当前子任务。materialize 在启动前从共享根池预留容量，并把正在物化的对象登记到 materializations；失败归还槽位，关闭时也会取消并等待这些尚未驻留的对象。这里的容量针对 activation，不是模型 token 的全局预算。〔D34〕

关闭使用 memoized close Promise，多次 dispose 共享同一次清理。finishDisposal 对本地子代理发取消，等待其空闲、后代关闭与待启动对象回滚，尝试最终 flush，再释放 handle、驻留表、容量和所有权；多个清理失败会被收集，不在第一个异常后遗弃其他分支。外部 provider 则通过对应 run 的 result/dispose 协调，不能假定具有本地 Agent 的同样接口。〔D34〕

生命周期事件还区分持久 child id 与一次驻留 epoch 的 runId。start 只在实际驻留后发布；end 使用同一身份并在清理结果已知后发布。epochStopReason 根据子会话实际消费的工作与 turn 终态推导 max-tokens、aborted、error、refusal 等，不能把 dispose 成功当作任务完成。未运行的已取消队列也会影响 completed 判断；失败与后来取消不能随意互相覆盖。〔D33〕

例如子代理测试失败后父代理要求停止，清理正常结束仍不意味着子任务成功。设计判断：创建、执行结果和资源释放分别记录，可以避免界面上的“已结束”被父代理误写成“已通过验证”。父代理仍需核对实际产物和证据，框架生命周期不替代业务验收。

## 权限只能继承到上限内

子代理 authority 不大于父代理批准范围，任务 profile 可进一步收紧。若子代理需要更宽权限，应向控制面发独立请求，而非因为父代理“很信任它”自动放行。凭据通过执行目标注入，不复制到子代理 prompt。

委派深度与活跃容量是两种限制。maxDepth 防递归扩展，maxActive 限资源；还应共享总 token 与墙钟预算，防止每个子代理各拥有一份完整父预算。

## 工作区隔离与文件归属

方案一分配不重叠文件，低成本但需要中央归属表；方案二使用独立 worktree/副本，最后合并；方案三只让子代理产出 patch，父代理统一应用。根据任务选择，不默认所有子代理都直接写同一目录。

worktree 不隔离端口、网络、外部数据库或凭据。测试服务名、临时路径和缓存也要避免冲突。Claude Code AgentTool 的工作目录与隔离相关可见实现可作为产品参考，具体启用能力受版本和门控影响。〔A13〕

## 容量与等待的死锁问题

如果父代理占着最后一个执行槽又等待子代理，而子代理需要同一槽才能启动，会死锁。明确根任务是否占槽，父等待是否释放，何时预约新 activation，取消时何时归还容量。限额在启动前预留，清理结束后释放，避免启动风暴短暂超额。

满额时可以拒绝并返回可重试状态，或进入有界公平队列。不要让一个无限排队调用长期占据它所需的资源。

## 父代理必须验证与整合

检查子结果的文件范围、patch 前置条件、测试证据版本和权限合规。多个 patch 合并后重新跑集成验证，因为各自通过不证明组合通过。冲突显式呈现，由父代理生成新方案，不能按最后完成者覆盖。

父代理总结也不能把子代理自报成功升级为已验证事实。报告保留原始证据引用，以及父代理额外做过哪些检查。

## 取消与恢复归属

父取消时停止创建后代，传播取消到归属树，等待清理。独立用户允许长期运行的任务需要转移所有者，不能仅因进程仍存在就成为无人管理后台工作。恢复时按持久 task_id 查询已有子任务，不能无条件重新 spawn。

验收覆盖深度、容量、父子竞态、共享文件冲突、工作区合并失败、外部 provider 不支持继续和父取消后资源回收。本章提供设计方案，参考内核尚未实现多 agent 调度。
