《AI Coding Agent 设计与实现》2.2.0 增订：按源码展开权限、沙箱与工具 runtime。

- 第 7 章：区分权限系统、沙箱和 runtime，比较三套工具调用生命周期。
- 第 8 章：补充 step 上下文归属、并发准入和取消后的正文收敛。
- 第 10 章：区分请求等待、进程期限与后台保留，追踪 Codex 与 Pi 的命令执行路径。
- 第 11 章：补充审批与升级重试、单调 guard、hook 输入变化、规则优先级及项目 trust。
- 第 12 章：区分策略与后端、full 与 partial，说明 Linux 包装顺序和升级时保留禁止读取。
- 证据索引扩展至 90 个文件，15 个 Claude Code 提取实现文件与 source map 嵌入文本对照。
- 延续源码事实、工程判断、建议方案分别标注；更新 EPUB、在线阅读及验证报告。

[在线阅读](https://aias00.github.io/coding-agent-book/) · [源码与书稿](https://github.com/Aias00/coding-agent-book) · [上一增订版](https://github.com/Aias00/coding-agent-book/releases/tag/v2.1.0)

本次为书稿增订；参考内核没有新增操作系统沙箱、任意 shell 或交互审批实现。上游实际隔离效果与跨产品安全性没有进行统一运行评测。
