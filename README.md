# AI Coding Agent 设计与实现

架构、核心机制与关键工程细节。以 Codex、DeepSeek Harness、Pi 和 Claude Code 为参考，从零设计一套能够读代码、改文件、运行验证和处理中断的 Coding Agent。

[在线阅读](https://aias00.github.io/coding-agent-book/) · [增订版 EPUB](https://github.com/Aias00/coding-agent-book/releases/download/v2.1.0/coding-agent-engineering.epub) · [完整书稿](book.md) · [第一版归档](https://github.com/Aias00/coding-agent-book/releases/tag/v1.0.0)

**第二版按设计问题全面重写**：24 章主体、序言与 3 篇附录，包含接口、状态机、数据结构、算法、调用时序、失败恢复和方案取舍。四个项目的 85 项源码证据作为机制依据穿插正文。

**2.1.0 增订**补充任务业务流程、模型实际看到的工具声明、Skill 渐进加载、MCP 发现与调用，以及四套上下文压缩实现的详细比较。新增内容先标注源码事实，再给分析判断和设计建议；不把客户端无法确认的服务端机制写成事实。

- [第 4 章：任务业务流程与执行循环](chapters/04-loop.md)
- [第 7 章：注册、暴露与调用](chapters/07-tool-contract.md)
- [第 15 章：四份压缩源码与方案取舍](chapters/15-compaction.md)
- [第 19 章：Skill 与 MCP 的实际接入](chapters/19-extension.md)

## 关键细节

- 输入何时认领、请求何时冻结、模型 attempt 与工具重试怎样区分。
- 流式字节怎样组装完整工具调用，输出截断为何不能执行。
- 声明与 runtime 如何绑定版本，有界并发、独占屏障与有序结果怎样实现。
- 文件哈希、唯一替换、锁、临时文件和原子替换分别解决什么。
- 审批怎样绑定实际参数、执行目标、权限和有效期，升级后怎样失效。
- 进程树、输出游标、stdin、超时与取消怎样管理。
- 上下文预算、代码证据版本、压缩边界与结构化摘要怎样设计。
- 意图、派发和结果事务如何划分，写后崩溃为什么必须承认结果未知。
- 单写者、输入队列、租约、fencing、插件卸载和子代理归属怎样落实。

## 目录

| 部分 | 章节 |
|---|---|
| 架构与内核 | 需求、总体架构、领域模型、执行循环 |
| 模型与工具 | 模型适配、流式协议、工具协议、调度 |
| 执行与权限 | 文件修改、终端进程、授权、沙箱 |
| 代码与上下文 | 预算、检索与 LSP、压缩 |
| 状态与恢复 | 持久化、未知结果、会话并发 |
| 扩展与产品 | 插件、多 Agent、产品协议、评测 |
| 动手与交付 | 可运行参考内核、实施路线与验收 |

## 运行参考内核

在 macOS/Linux 上使用 Python 3.9+，无需 API 密钥；本地进程锁使用 fcntl。默认脚本模型用于测试机制，不宣称具有真实模型的推理能力。

```sh
python3 -m reference_agent init /tmp/agent-design-demo
python3 -m reference_agent run /tmp/agent-design-demo --allow-edit
python3 -m reference_agent events /tmp/agent-design-demo
```

Kernel 依据 Model 返回的调用推进：读取 → 编辑 → 验证 → 完成。实现不可变调用、工具校验、授权指纹、SQLite 事务、有界并发、文件前置条件与保守恢复。每个数据库演示一个任务生命周期，新任务使用新目录。

模拟写入后、结果提交前崩溃：

```sh
python3 -m reference_agent init /tmp/agent-design-crash
python3 -m reference_agent run /tmp/agent-design-crash --allow-edit --crash-after-edit
python3 -m reference_agent run /tmp/agent-design-crash --allow-edit
```

最后一条应报告 `OutcomeUnknown`，不会盲目重放编辑。显式后置条件核对可在独立 [labs 实验](labs/harness_lab.py) 中体验，完整说明见[第 23 章](chapters/23-reference.md)。

## 验证与构建

```sh
python3 -m unittest reference_agent.test_core -v
python3 -m unittest discover -s labs -v
python3 scripts/build.py
python3 scripts/check.py
node --check web/reader.js
```

18 项内核测试与 10 项故障实验测试覆盖循环、授权、冲突、截断、屏障、预算和恢复。构建需要 Pandoc 3.12.1，产物位于 `dist/` 和 `site/`；EPUBCheck 5.4.0 独立检查出版格式。GitHub Actions 通过后自动发布在线版。

可用 `python3 -m http.server 8765 --directory site` 本地阅读。网站支持搜索、主题、字号、位置恢复和手机目录；正文无需 JavaScript。旧版章节地址提供第二版对应入口。

## 源码依据

| 材料 | 固定身份 |
|---|---|
| Codex | `57d4fac64adbcaed0523ca6bf8d58c4ef6875157` |
| DeepSeek Harness | `687f282e8625c6b8d11ff58211a90524be2e4317` |
| Pi | `16f5f0af4d85ca583d045ceb5ed6d646fcaf7761` |
| Claude Code | 本地 2.1.88 发布包；引用的 14 个提取实现文件与 source map 嵌入文本对照 |

研究日期 2026-10-30。完整路径、哈希和固定提交链接见[附录 B](chapters/26-sources.md)。不上传 Claude Code 原始发布包、source map 或提取源码。

正文分别标明设计方案、上游事实和实际代码范围。真实模型流式 adapter、操作系统沙箱、分布式执行、持久审批、LSP、MCP、任意 shell 和多 agent 平台提供设计与验收要求，并未冒充完整生产实现。没有执行四个产品的统一真实模型 benchmark。

原创文字与图示 CC BY 4.0；原创代码 MIT。Aias00 发布，AI 辅助研究与编写。出处见 [NOTICE.md](NOTICE.md)，验证见 [reports/](reports/)。
