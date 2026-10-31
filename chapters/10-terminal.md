# 第 10 章 命令执行：进程树、输出游标与后台任务

## 源码路径：进程寿命与请求等待不是一回事

源码事实：Codex 的 `UnifiedExecProcessManager` 将进程保存、输出收集和后续交互分开。`exec_command_inner()` 使用经过限制的 yield_time_ms 决定普通调用的本次等待；仍在运行且符合保留条件的进程可以返回 process_id，后续通过 write_stdin 或空输入继续交互、查询。部分 completion 配置另有等待行为，不能把所有分支都简化成固定毫秒数。〔C07〕

yield_time_ms 到期并不等于进程真实运行期限到期。观察调用返回后，测试、构建或服务器仍可能继续；进程管理器需要保留执行环境、输出、退出状态及资源归属，而非只把一次命令输出存进聊天文本。执行器侧的进程标识还加入 UUID，降低本地标识被重新使用时与执行器保留进程混淆的风险。〔C07〕

Pi 内置 Bash 的本地路径由 `createLocalShellOperations()` 启动 child_process，流式读取 stdout/stderr；POSIX 平台以 detached 方式建立进程归属，取消或明确超时时调用 killProcessTree。工具 schema 中 timeout 可选且无默认超时，resolveTimeoutMs 拒绝非正数、非有限数和超出范围的值。等待后还把信号终止映射到非成功退出值，避免 null exit code 被误解为成功。〔P17〕

这里应区分三种期限：请求等待窗口、真实进程运行期限、后台资源保留期限。Pi 的这条 Bash 路径主要演示完整命令等待与取消；Codex unified exec 展示可持续交互的进程管理。不能因为两者都能执行 shell，就认为后台会话语义完全相同。

Pi 的 `BashOperations` 可以替换为远程执行实现，spawnHook 也可以改变 command、cwd 和 env。设计判断：这种 seam 便于扩展，但自建宿主应让最终执行对象与审批对象一致，并确保远程文件、编辑和命令工具指向同一执行世界。可替换接口本身不等于已经具备远程隔离。〔P17〕

## 启动进程与等待进程分成两个接口

```text
start(argv, cwd, env_profile, authority) -> ProcessHandle
poll(process_id, after_cursor, max_bytes) -> OutputChunk + ProcessState
write_stdin(process_id, bytes, authority) -> InteractionResult
terminate(process_id, reason) -> TerminationReport
```

ProcessState 至少区分 starting、running、exited、terminating、lost。一次 poll 等待窗口结束，只表示这次没有拿到终态，不应直接杀进程。Codex unified exec 的进程管理体现了命令调用与长期进程的分离。〔C07〕

## argv 优先，shell 必须显式

固定测试命令使用 argv 数组，避免 shell 额外解释变量、重定向和命令替换。需要 shell 时明确 shell binary、登录模式和脚本字符串，把这些全部纳入授权指纹。安全策略不能一边检查 argv，另一边实际执行重新拼接的 shell 文本。

工作目录应是执行世界里的路径，不由控制面先解析成另一个主机的路径。环境采用 allowlist 或命名 profile，默认不继承所有凭据、代理和开发者私有配置。PATH、语言与分页设置影响输出复现，要有明确定义。

## 三种时间限制

调用等待窗口控制这次 API 最多阻塞多久；进程运行期限控制真实命令最长多久；无活动回收期限控制遗留后台资源。三者分别配置与记录。长测试超过调用等待窗口可以继续运行，但超过真实期限需要进入 termination 流程。

总任务取消后是否保留开发服务器，也需要产品规则。默认不留下无人管理的进程；用户明确要求保持服务时，将它注册为可发现、可停止的后台产物，而非让它意外成为孤儿。

## 终止要面对整个进程树

POSIX 方案可在新 session/process group 中启动命令，取消先向组发温和信号，等待短暂 grace period，再升级强制终止并 reap。Windows 需要使用对应的进程归属与终止机制。仅杀 shell 父进程可能留下测试 worker 或服务器。

系统必须记录信号和实际退出状态。发送 SIGTERM 成功不代表进程已退出；强杀后 stdout reader 也要收敛。无法确认时返回 lost 或 unknown，避免界面显示“已停止”而进程仍在消耗资源。

## 输出必须边读边限制

不能等待进程结束后才读 stdout/stderr，否则管道填满会使进程阻塞。使用独立读取任务，保存总字节数、保留头尾、完整输出产物和截断标志。把退出码与输出展示独立：尾部包含 PASS 不代表最终退出成功。

游标应表示已持久输出中的位置，poll 返回 next_cursor。客户端重复请求同一游标，可以得到同一段数据；不能因为网络重试就永久跳过输出。多个 UI 各自维护游标，不共享一个 destructive read。

## stdin 需要自己的权限语义

启动命令时用户可能只同意查看帮助，随后发送 y 却会确认删除。stdin 交互不能因已经拥有 process_id 就自动无限允许。绑定进程身份、启动权限、当前状态与输入类别；对敏感交互要求新的批准。

口令输入不应回显或进入普通模型历史。交互工具需要区分 PTY 与普通管道，Ctrl-C、EOF、换行和字符输入是不同操作。没有 PTY 的环境不能假装支持所有交互程序。

## 进程身份不能只用 PID

PID 可能复用。句柄应包含系统生成的随机 identity、创建时间或执行器 generation，执行器内部再映射到 PID。重启后发现进程是否仍属于本会话，需要受信归属信息，不能看到同一 PID 就继续写 stdin。

远程 worker 丢失连接时，控制面应查询任务状态或按取消 token 终止；无法确认不自动重启同一写命令。测试和构建也可能有副作用，因此 replay policy 必须由具体执行约束确定。

## 本书实现范围与验收

参考内核提供固定 fixture 验证工具，不暴露任意 shell；较小 labs 实验运行固定 Python unittest 子进程。生产进程管理按本章接口扩展。测试应覆盖大输出、无输出长运行、子进程派生、stdin 阻塞、超时、取消、worker 重启和输出读取失败，而不是只检查 `echo hello`。
