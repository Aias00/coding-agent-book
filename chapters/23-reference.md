# 第 23 章 参考实现：一个真正由模型响应驱动的内核

## 程序结构与实际范围

`reference_agent/core.py` 定义 Call、Response、Request、Model、Tool、Policy、Store、Workspace 和 Kernel。`__main__.py` 提供初始化、运行和事件查看；`test_core.py` 验证关键行为。只使用 Python 标准库，默认脚本模型，无 API 密钥和外部服务。运行目标为 macOS/Linux，文件锁使用 fcntl，未提供 Windows 锁实现。

与固定顺序执行四个函数的演示不同，Kernel 每一步把已提交历史交给 Model，按返回的 calls 决定执行，再将结果送回下一次请求。FixtureModel 读取历史选择读取、编辑、验证或停止；替换 Model 实现即可改变行动提议，工具与存储无需跟着改。

这仍是有意收窄的可信单机内核：一个数据库一个会话，进程锁防止多个 actor 同时使用；无通用 shell、无操作系统沙箱、无完整 SDK、无多 agent。文件读取可并行，文件写入保持同步短操作。固定 fixture 验证器不执行任意仓库代码。

每个数据库只演示一个任务生命周期。已完成后再次运行表示读取原任务完成状态，不代表对外部新改动重新验证；新的目标或工作区版本应创建新任务与调用身份。本例通过新目录开始新任务，生产版本应实现多 turn 及证据有效性管理。

## 运行一次完整任务

使用尚不存在的目录：

```sh
python3 -m reference_agent init /tmp/agent-design-normal
python3 -m reference_agent run /tmp/agent-design-normal --allow-edit
python3 -m reference_agent events /tmp/agent-design-normal
```

第一条创建有意带错误的 `paths.py` 和任务文件。第二条模型先请求两次读取，再依据读取哈希提出精确修改，再调用固定验证器，最后返回完成。四次模型请求对应四个决策阶段，工具动作来自实际 Response，而不是 Kernel 的硬编码 if edit。

`--allow-edit` 是本示例明确的执行许可。省略时编辑返回错误，脚本模型报告受阻，任务为 partial，文件不变。它不是生产交互式审批系统；完整审批队列方案见第 11 章。

## 不可变调用怎样实现

Call 保存 `arguments_json` 而不是可变字典。创建时 canonical 序列化，读取参数时重新解析，防止调用者持有字典引用后悄悄修改。Request 同样保存已分离的历史和工具声明 JSON，并记录摘要 revision。

这并非任意对象的通用冻结器，但对于示例的 JSON 调用边界足够明确。真实模型 adapter 先完成参数块，再构造 Call；未完成 finish reason 的响应只记录 attempt/incomplete，不执行工具。

## SQLite 事务对应哪条约束

`Store.accept` 同一事务插入调用意图与 assistant/settled。`Store.dispatched` 检查指纹并记录派发。`Store.settle` 同一事务更新结果与 tool/result。重复结果必须相同，不同结果冲突。事件序号由数据库分配。

工具执行不发生在长数据库事务里，否则慢调用会占用写锁。派发与结果是两个短事务，中间存在真实未知窗口，程序通过恢复政策处理而非假装消除。

## 并发与独占的代码位置

`Kernel.batch` 将连续 parallel 调用放入有界 semaphore 组，`gather` 收集结果，按原始顺序提交；exclusive 调用单独形成屏障。普通工具异常转换成结果，进程丢失类异常保留未结算派发，供恢复判断。

参考实现没有滚动结果即时提交，也没有动态工具热卸载。要升级时先保留测试中的顺序与屏障不变量，再替换调度算法。

## 修改与验证的证据

读取工具返回正文哈希；编辑工具检查哈希、旧文本唯一和结果大小，临时文件替换后返回新哈希。验证器只接受预定的 fixture 修复文本，再执行四个词法路径用例，记录对应实现哈希。

Kernel 完成前检查验证来源确实是 verify_paths，并对应当前实现版本。仅把一个 read 调用命名为 verify-1 不能伪造完成证据。这个测试说明“看 id 像验证”与“真实经过验证工具”有重要区别。

## 制造写入后崩溃

```sh
python3 -m reference_agent init /tmp/agent-design-crash
python3 -m reference_agent run /tmp/agent-design-crash --allow-edit --crash-after-edit
python3 -m reference_agent run /tmp/agent-design-crash --allow-edit
```

第二条在文件变化后、结果提交前模拟进程丢失。第三条恢复已接纳的 pending response，发现 edit dispatched 且非 replay-safe，返回 OutcomeUnknown。程序不会先让模型生成一个新编辑 id，也不会再次修改文件。

需要体验显式后置核对，可用较小实验：

```sh
python3 labs/harness_lab.py init /tmp/agent-window-demo
python3 labs/harness_lab.py run /tmp/agent-window-demo --crash after-edit
python3 labs/harness_lab.py run /tmp/agent-window-demo --reconcile
```

两个演示使用独立目录和存储，不能混用。它们模拟提交窗口，不模拟所有断电、文件系统和介质故障。

## 运行机制测试

```sh
python3 -m unittest reference_agent.test_core -v
python3 -m unittest discover -s labs -v
```

18 项内核测试覆盖完整循环、无重复恢复、权限拒绝、截断不执行、写后中断、文件冲突、调用身份、授权绑定、路径拒绝、单 actor、有界并发、独占屏障、持久预算、取消和验证身份。10 项小实验测试聚焦日志与后置核对。

接真实模型时只实现 Model 接口并遵守完整响应与错误约定；加入任意 shell 前先落实第 10、12 章的执行环境。把每次扩展接到已有管线，保持测试能证明同样约束。
