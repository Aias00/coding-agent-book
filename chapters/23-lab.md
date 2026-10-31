# 第 23 章 动手实验：构建一个会承认未知的运行框架

## 实验目标与范围

本仓库的 `labs/harness_lab.py` 是独立编写的教学程序。它不用真实模型，不调用上游产品，不需要密钥。确定性驱动固定提出两个读取、一项编辑和一次测试，用来隔离运行框架机制，避免把模型随机性混入日志与恢复实验。

程序只在新建的可丢弃目录中创建 `paths.py`、`test_paths.py` 和 `events.jsonl`。工具读操作并行执行，结果按计划顺序提交；编辑检查完整旧内容；测试使用 Python 子进程运行四个词法路径用例。它不是生产级智能体，也不提供操作系统沙箱、多写者协调或通用工作流引擎。

## 第一步：观察正常执行

在仓库根目录运行，选择尚不存在的目录：

```sh
python3 labs/harness_lab.py init /tmp/coding-agent-demo-normal
python3 labs/harness_lab.py run /tmp/coding-agent-demo-normal
```

打开该目录中的 `events.jsonl`，可以看到工具意图、派发与结果。正常结果最后有 `run/completed`。测试结果包含子进程退出码和真实 unittest 输出，而不是驱动自称测试通过。

两个读取通过 `ThreadPoolExecutor` 执行，结果循环仍沿计划顺序读取 future 并提交。这里刻意分开执行完成与日志提交。再次运行相同命令会复用已提交结果，不再执行编辑或测试。

这项复用假定实验工作区和任务定义没有被外部改变。生产系统还应把输入版本、代码哈希或环境身份绑定到结果有效性，不能永远相信旧的成功测试。

## 第二步：观察授权拒绝

```sh
python3 labs/harness_lab.py init /tmp/coding-agent-demo-denied
python3 labs/harness_lab.py run /tmp/coding-agent-demo-denied --deny-edit
```

程序以状态码 2 退出，并保留策略拒绝结果。编辑没有派发，文件仍是有意存在缺陷的原始版本。测试验证的是副作用没有发生，而不是输出里有没有“遵守权限”几个字。

同一日志中的拒绝不会因为下次省略参数就自动改为允许。实验把失败结果视为当前调用终态；要研究不同政策，应使用新的实验目录。这避免用隐式重试悄悄覆盖过去授权事实。

## 第三步：在派发前停止

```sh
python3 labs/harness_lab.py init /tmp/coding-agent-demo-stop
python3 labs/harness_lab.py run /tmp/coding-agent-demo-stop --stop-before edit
python3 labs/harness_lab.py run /tmp/coding-agent-demo-stop
```

第一次 run 保存意图与停止记录，没有编辑派发；第二次可以正常继续。这个场景相对简单，因为我们知道副作用尚未开始。它与已经派发但没有结果的中断不能使用同一策略。

## 第四步：制造写入后的未知窗口

```sh
python3 labs/harness_lab.py init /tmp/coding-agent-demo-crash
python3 labs/harness_lab.py run /tmp/coding-agent-demo-crash --crash after-edit
python3 labs/harness_lab.py run /tmp/coding-agent-demo-crash
```

第一项 run 在实际替换文件后、记录成功结果前注入异常。第二项 run 看到编辑已经派发却没有已提交结果，返回 `OutcomeUnknown`，不会盲目重写文件。注入异常模拟的是状态窗口，并不声称模拟了真实机器断电、磁盘缓存损坏或所有文件系统持久性情况。

这时你能看到现实文件已经修复，日志却没有编辑成功。它具体展示了为什么“恢复聊天”不足以证明工具未执行。

## 第五步：显式核对后置条件

```sh
python3 labs/harness_lab.py run /tmp/coding-agent-demo-crash --reconcile
```

reconcile 检查当前文件是否精确等于预定的新内容。匹配时补记已核对结果，再运行测试；不匹配时仍报告未知。它没有重新派发编辑。这个策略只适用于本实验固定的精确替换，不应扩展到任意写操作。

如果有人在中断后修改了文件，即使改动看起来合理，精确比较也会失败。保守失败使冲突可见，后续应由明确的新任务决定如何处理，而不是用运行框架的恢复逻辑覆盖用户改动。

## 验证完整实验

```sh
python3 -m unittest discover -s labs -v
```

本版包含 10 项测试，覆盖正常修复、四个真实边界用例的执行、重复恢复不重复派发、授权拒绝、停止后继续、写后中断、显式核对、前置条件变化、有序读取结果和损坏日志拒绝等行为。其中部分测试覆盖多个断言，数量不等于场景穷尽。

日志追加调用 flush 与 fsync，文件替换使用临时文件加 `os.replace`；目录项同步、跨进程锁、日志修复和存储介质故障不在本实验保证内。程序故意拒绝损坏日志尾部，避免静默忽略一条可能记录了派发的事实。

## 将实验映射回四个项目

意图与结果对应工具调用生命周期；并行读取与有序提交对应调度器语义；派发前停止对应取消边界；后置条件核对对应保守副作用恢复。四套真实系统更复杂，但理解这些最小机制后，再读其源码时就能追踪“它在这里承诺了什么”，而不只停留在功能名称。
