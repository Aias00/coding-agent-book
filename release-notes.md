《AI Coding Agent 设计与实现》2.3.0 增订：补齐此前偏概括的六条执行链路。

- 第 5、6 章：provider 重试策略与执行插件、退避默认值、截断与中断内容、流式 fallback、历史与 UI 结算。
- 第 9 章：Pi 编辑工具的参数兼容、唯一匹配、模糊回退、进程内队列与写入边界。
- 第 16、17 章：Codex writer 队列和屏障、DeepSeek 整代迁移发布、Pi Durable 执行意图、replay 双重检查与重启熔断。
- 第 18、20 章：输入安置与 reset、视图重连、配置冻结粒度、fork seed、子代理容量、所有权与关闭流程。
- 第 22 章与附录 A：列明已有解释、建议方案、未实现功能和仍需运行验证的结论。
- 证据索引扩展至 100 个文件；15 个 Claude Code 提取实现文件继续与 source map 对照。
- 在线阅读与 EPUB 同源更新；保留现有 24 章主体和 28 项参考程序测试。

[在线阅读](https://aias00.github.io/coding-agent-book/) · [源码与书稿](https://github.com/Aias00/coding-agent-book) · [上一增订版](https://github.com/Aias00/coding-agent-book/releases/tag/v2.2.0)

本次新增静态源码分析，没有把参考程序测试扩大解释为上游运行测试。真实模型质量、费用、跨平台隔离及跨产品成功率仍需独立实验。
