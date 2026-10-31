# Coding Agent 工程剖析

从 Codex、DeepSeek Harness、Pi 与 Claude Code 读懂智能体运行时。

[在线阅读](https://aias00.github.io/coding-agent-book/) · [下载 EPUB](https://github.com/Aias00/coding-agent-book/releases/download/v1.0.0/coding-agent-engineering.epub) · [完整书稿](book.md) · [证据索引](chapters/26-sources.md)

本书包含 **24 章主体、序言与 3 篇附录，约 3.1 万中文汉字**（不含源码索引），分析执行循环、工具调度、权限与沙箱、上下文压缩、持久化、取消和故障恢复。附 68 个源码文件的固定快照证据、原创架构图和无 API 密钥实验。

## 阅读内容

| 篇章 | 重点 |
|---|---|
| 第 1—2 章 | 运行框架职责、研究方法与贯穿修复案例 |
| 第 3—6 章 | Codex：回合/步骤、工具计划、审批编排、终端与历史重建 |
| 第 7—10 章 | DeepSeek Harness：Cordis、能力接口、日志投影、有序并发与代际迁移 |
| 第 11—14 章 | Pi：低层循环、工具钩子、会话树与实验性 Durable |
| 第 15—18 章 | Claude Code：发布包证据、工具协议、权限、压缩与记录链 |
| 第 19—24 章 | 横向比较、安全、可靠性、评测、动手实验与架构选择 |
| 附录 | 术语、自检答案、源码快照与构建方法 |

在线版支持全文搜索、明暗主题、字号调整、阅读位置记忆、章节翻页和手机目录；正文无需 JavaScript 也能阅读。

## 研究快照

| 材料 | 身份 |
|---|---|
| openai/codex | `57d4fac64adbcaed0523ca6bf8d58c4ef6875157` |
| deepseek-ai/deepseek-harness | `687f282e8625c6b8d11ff58211a90524be2e4317` |
| earendil-works/pi | `16f5f0af4d85ca583d045ceb5ed6d646fcaf7761` |
| ccsource/package | Claude Code `2.1.88`；引用的 13 个提取实现文件与本地 source map 嵌入文本一致 |

研究日期：2026-10-30。本书区分源码事实、工程解释与设计建议。Claude Code 材料是发布包中的可见实现，并非官方开源仓库；本仓库不上传原始发布包、source map 或提取源码。未执行四个产品的统一真实模型性能评测。

## 本地构建

需要 Python 3.9+、Pandoc 3.12.1；网站脚本语法检查需要 Node。EPUBCheck 5.4.0 是独立验证工具，需要 Java。

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m unittest discover -s labs -v
node --check web/reader.js
python3 -m http.server 8765 --directory site
```

浏览器打开 `http://localhost:8765`。电子书输出到 `dist/coding-agent-engineering.epub`；完整静态网站输出到 `site/`。构建不需要四个上游目录。只有重新采集源码身份时才运行：

```sh
python3 scripts/snapshot.py --source-root /Volumes/data
```

可选浏览器检查：安装 Playwright 和 Chromium 后运行 `node scripts/browser-check.cjs`，或者通过 `PLAYWRIGHT_MODULE_PATH` 指定已有 Playwright 模块。检查涵盖桌面、390px 手机、导航、搜索、主题、字号、书签、源码锚点和无脚本阅读。

## 可运行实验

```sh
python3 labs/harness_lab.py init /tmp/my-agent-book-demo
python3 labs/harness_lab.py run /tmp/my-agent-book-demo --crash after-edit
python3 labs/harness_lab.py run /tmp/my-agent-book-demo
python3 labs/harness_lab.py run /tmp/my-agent-book-demo --reconcile
```

第二条命令模拟写入后、结果提交前的崩溃，第三条应报告结果未知，最后一条核对文件后置条件再继续。完整讲解见[第 23 章](chapters/23-lab.md)。教学程序不是生产沙箱，也不提供任意副作用恰好一次保证。

## 自动发布

推送 `main` 后，GitHub Actions 使用固定版本及校验和的 Pandoc/EPUBCheck 生成两种版本，运行结构检查、10 项实验测试与 EPUBCheck，通过后发布 GitHub Pages。版本 EPUB 同时放在 GitHub Release。

本地验证结果见 [reports/](reports/)。结构检查覆盖网页与 EPUB 的内部资源和锚点；浏览器检查和教学实验单独记录，不代表已构建或运行四个上游项目。

## 署名与许可

Aias00 发布，AI 辅助研究与编写。原创文字与图示 CC BY 4.0；原创代码 MIT。上游权利与材料边界见 [NOTICE.md](NOTICE.md)。
