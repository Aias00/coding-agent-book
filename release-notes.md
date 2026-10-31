《AI Coding Agent 设计与实现》2.1.0 增订：补齐任务流程、Tool/Skill/MCP 机制与四套上下文压缩实现的源码分析。

- 第 4 章补充从任务接纳、项目调查、实施、验证到交付的业务流程及异常分支。
- 第 7、19 章补充模型侧工具声明、暴露模式、Skill 目录与正文加载、MCP 原始名称映射和同步失败边界。
- 第 15 章按 Pi、DeepSeek Harness、Codex、Claude Code 分别追踪压缩触发、切分、摘要、替换与能力恢复，并分析收益和代价。
- 区分源码事实、分析判断和设计建议，不对未公开的服务端压缩机制或未实测性能作确定结论。
- 源码证据从 68 扩展到 85 个文件，Claude Code 引用的 14 个提取实现文件与本地 source map 对照。
- 保留 24 章主体、3 篇附录、可运行参考内核及 28 项机制测试，更新同源 EPUB 与在线阅读。

[在线阅读](https://aias00.github.io/coding-agent-book/) · [参考实现与书稿](https://github.com/Aias00/coding-agent-book) · [第一版归档](https://github.com/Aias00/coding-agent-book/releases/tag/v1.0.0)

默认脚本模型用于机制验证，无需 API 密钥。真实模型流式接入、操作系统隔离与分布式执行等给出方案和验收要求，尚非完整生产实现。
