# 附录 B 源码快照与证据索引

研究日期为 2026-10-30。以下链接固定到所读提交，行号是定位入口而非整章唯一依据。所有 SHA-256 来自本地文件原始字节。没有上传上游源码。

## 快照身份

| 项目 | 提交或包版本 | 说明 |
|---|---|---|
| codex | `57d4fac64adbcaed0523ca6bf8d58c4ef6875157` | 仅有未跟踪 docs/epub/；本书不将其作为实现证据 |
| deepseek-harness | `687f282e8625c6b8d11ff58211a90524be2e4317` | 按发布包与 source map 标识 |
| pi | `16f5f0af4d85ca583d045ceb5ed6d646fcaf7761` | 按发布包与 source map 标识 |
| ccsource | `Claude Code 2.1.88；无 Git 提交` | 按发布包与 source map 标识 |

## 材料与验证方法

研究脚本记录 100 个文件。Claude Code 被引用的提取实现逐一与 `cli.js.map` 内对应 `sourcesContent` 对照；这验证本地一致性，不替代发布包来源认证或构建可达性证明。研究材料中有既有书稿和压缩包，本书未将其并入分析正文。

这些快照作为设计方案的参考依据。可运行参考内核和故障实验见第 23 章；完整方案包含明确标注的扩展设计。未构建四个上游项目或执行统一真实模型评测。

## C01 · codex {#evidence-c01}

- 相对路径：`codex/codex-rs/core/src/session/turn.rs`
- 定位：第 173 行，`async fn run_turn`；文件共 3415 行。
- SHA-256：`076bf9522cba976a9b171d3a33403dfb7927330a73fe66afd4e8648f4b1c3629`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/session/turn.rs#L173)

## C02 · codex {#evidence-c02}

- 相对路径：`codex/codex-rs/core/src/session/step_context.rs`
- 定位：第 23 行，`struct StepContext`；文件共 90 行。
- SHA-256：`a91cfea24c0065ac1ef2885141eb3491f9f156f2ccbfad588378ada9ce77b300`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/session/step_context.rs#L23)

## C03 · codex {#evidence-c03}

- 相对路径：`codex/codex-rs/core/src/tools/router.rs`
- 定位：第 85 行，`struct ToolRouter`；文件共 449 行。
- SHA-256：`7345f8d2c467637e3d646d5510770457db89e4259e0515d5175de363e2c9c79e`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/tools/router.rs#L85)

## C04 · codex {#evidence-c04}

- 相对路径：`codex/codex-rs/core/src/tools/registry.rs`
- 定位：第 330 行，`struct ToolRegistry`；文件共 970 行。
- SHA-256：`fc37acd056a78779aeeff497d30bcbba759ea55f469ae2c9e7b8f37f3aeb2dae`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/tools/registry.rs#L330)

## C05 · codex {#evidence-c05}

- 相对路径：`codex/codex-rs/core/src/tools/orchestrator.rs`
- 定位：第 125 行，`pub async fn run`；文件共 645 行。
- SHA-256：`8996f718b818804473c151a8a643747c2b5ab69b05f4630eee143fac7daa0bb5`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/tools/orchestrator.rs#L125)

## C06 · codex {#evidence-c06}

- 相对路径：`codex/codex-rs/core/src/tools/parallel.rs`
- 定位：第 46 行，`struct ToolCallRuntime`；文件共 886 行。
- SHA-256：`f575c018ab1452d99ccf9fa4630e5af5e92bbc9eb3e5457ea17ab5be8ae946d0`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/tools/parallel.rs#L46)

## C07 · codex {#evidence-c07}

- 相对路径：`codex/codex-rs/core/src/unified_exec/process_manager.rs`
- 定位：第 451 行，`impl UnifiedExecProcessManager`；文件共 1929 行。
- SHA-256：`7eba3d82a54ad77cb989991ead28b39fe4aa1df24ddea020a0a36adb2d0fca5a`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/unified_exec/process_manager.rs#L451)

## C08 · codex {#evidence-c08}

- 相对路径：`codex/codex-rs/core/src/compact.rs`
- 定位：第 117 行，`run_inline_auto_compact_task`；文件共 919 行。
- SHA-256：`7501febae5a93a943e22c17ddb4009d6fea587cef40c6d5c6cf1b0754737be0d`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/compact.rs#L117)

## C09 · codex {#evidence-c09}

- 相对路径：`codex/codex-rs/core/src/session/rollout_reconstruction.rs`
- 定位：第 64 行，`fn select_input_compaction`；文件共 655 行。
- SHA-256：`1f4827c0f383641f2b407d7b40bca671d5d80a73412a1ccc9702ba4181d3d501`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/session/rollout_reconstruction.rs#L64)

## C10 · codex {#evidence-c10}

- 相对路径：`codex/codex-rs/rollout/src/recorder.rs`
- 定位：第 86 行，`struct RolloutRecorder`；文件共 2300 行。
- SHA-256：`61641565235a7fd5289db4344a5e2b8f124b269eb461eeb37998d361d0cbea95`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/rollout/src/recorder.rs#L86)

## C11 · codex {#evidence-c11}

- 相对路径：`codex/codex-rs/core/src/tools/spec_plan.rs`
- 定位：第 121 行，`build_tool_router`；文件共 1680 行。
- SHA-256：`919bf85acf44810892f6d1adc6701253c92a71678cbf74c877d718d0aaf9db9f`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/tools/spec_plan.rs#L121)

## C12 · codex {#evidence-c12}

- 相对路径：`codex/codex-rs/core/src/tools/sandboxing.rs`
- 定位：第 378 行，`trait ToolRuntime`；文件共 578 行。
- SHA-256：`1ab6c27e34a93fe3857281e11e388eb3ae4b786819fbe15883ad7e1fb8b5473f`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/tools/sandboxing.rs#L378)

## C13 · codex {#evidence-c13}

- 相对路径：`codex/codex-rs/core/src/session/input_queue.rs`
- 定位：第 1 行，`file`；文件共 843 行。
- SHA-256：`11212b3d8fa379ecbabcf8392889e157964075617cfb5d55b3ec5c2477ffaa45`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/session/input_queue.rs#L1)

## C14 · codex {#evidence-c14}

- 相对路径：`codex/codex-rs/core/src/session/multi_agents.rs`
- 定位：第 1 行，`file`；文件共 121 行。
- SHA-256：`a820832921665e16ddade8d56edd816c7f551d4eec3d509f75482426693fb7e4`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/session/multi_agents.rs#L1)

## C15 · codex {#evidence-c15}

- 相对路径：`codex/codex-rs/app-server/README.md`
- 定位：第 1 行，`file`；文件共 618 行。
- SHA-256：`d8e489c92adeb9d33bcbbcc5ff78431e839fdb2d6cefccb16812316bc22f5573`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/app-server/README.md#L1)

## C16 · codex {#evidence-c16}

- 相对路径：`codex/LICENSE`
- 定位：第 1 行，`Apache License`；文件共 201 行。
- SHA-256：`d17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/LICENSE#L1)

## C17 · codex {#evidence-c17}

- 相对路径：`codex/codex-rs/core/src/compact_remote_v2.rs`
- 定位：第 480 行，`fn build_v2_compacted_history`；文件共 1353 行。
- SHA-256：`cb81ae523a2d3674ffe0acd12a492431d773e1148a420bbd99850b9081277673`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/compact_remote_v2.rs#L480)

## C18 · codex {#evidence-c18}

- 相对路径：`codex/codex-rs/core/src/compact_remote_v2_installation.rs`
- 定位：第 86 行，`candidate.model_info.slug`；文件共 299 行。
- SHA-256：`51bc95908de2153856836f931b25deed831c5e2c3ab13a3dc35231da3a0ae0be`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/compact_remote_v2_installation.rs#L86)

## C19 · codex {#evidence-c19}

- 相对路径：`codex/codex-rs/core/src/compact_token_budget.rs`
- 定位：第 58 行，`sess.start_new_context_window`；文件共 69 行。
- SHA-256：`49682d338de201896ee122e36b16dc62072ce791c4acea52c7c0a6b615e6e20f`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/compact_token_budget.rs#L58)

## C20 · codex {#evidence-c20}

- 相对路径：`codex/codex-rs/core/src/session/async_compaction.rs`
- 定位：第 162 行，`candidate.prefix.generation`；文件共 222 行。
- SHA-256：`275a1ea41773da9644e9f03d41548fed92cf4ad8891a0b4fcd61675ff64ef909`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/core/src/session/async_compaction.rs#L162)

## C21 · codex {#evidence-c21}

- 相对路径：`codex/codex-rs/protocol/src/models.rs`
- 定位：第 1296 行，`    Compaction {`；文件共 4757 行。
- SHA-256：`753498bc730ba21ded710d9aa2b2f9163e6bbe4eaa18f1c25d998c36138a54f7`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/protocol/src/models.rs#L1296)

## C22 · codex {#evidence-c22}

- 相对路径：`codex/codex-rs/linux-sandbox/src/linux_run_main.rs`
- 定位：第 59 行，`pub struct LinuxSandboxCommand`；文件共 1198 行。
- SHA-256：`2c8cdf628b8b8467cccf38227cada5295f5cb6a04888b860ea1b882fe2d19d53`
- [固定提交源码](https://github.com/openai/codex/blob/57d4fac64adbcaed0523ca6bf8d58c4ef6875157/codex-rs/linux-sandbox/src/linux_run_main.rs#L59)

## D01 · deepseek-harness {#evidence-d01}

- 相对路径：`deepseek-harness/docs/architecture.md`
- 定位：第 79 行，`## Turn flow`；文件共 165 行。
- SHA-256：`95a7722c7096d665d8adedeb733b8f5ad7740e67cb5c6e9dc91ec05f430cb760`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/docs/architecture.md#L79)

## D02 · deepseek-harness {#evidence-d02}

- 相对路径：`deepseek-harness/packages/core/agent-loop/src/agent.ts`
- 定位：第 604 行，`prepareCall`；文件共 705 行。
- SHA-256：`4add12f5c22bb1b8cf1dbc239c9b09fa3351feff2c936cb2b8900036468bd01b`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/agent-loop/src/agent.ts#L604)

## D03 · deepseek-harness {#evidence-d03}

- 相对路径：`deepseek-harness/packages/core/agent-loop/src/tool-calls.ts`
- 定位：第 60 行，`async function executeToolCalls`；文件共 290 行。
- SHA-256：`5c7e8d8ff0028b436efdd13e5dffa4801d2311c211c3af039e7dab705f87b303`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/agent-loop/src/tool-calls.ts#L60)

## D04 · deepseek-harness {#evidence-d04}

- 相对路径：`deepseek-harness/packages/core/agent-loop/src/assistant-stream.ts`
- 定位：第 18 行，`class AssistantStreamAttempt`；文件共 140 行。
- SHA-256：`120d2bec5efeec2aa54bf0e4261a45282936272d610dbbab21eee36b902629de`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/agent-loop/src/assistant-stream.ts#L18)

## D05 · deepseek-harness {#evidence-d05}

- 相对路径：`deepseek-harness/packages/core/tools/src/index.ts`
- 定位：第 1 行，`file`；文件共 1993 行。
- SHA-256：`398bcdeb221e450d088510830b77d99a513e65ab31e40ade71688a19cdf5e6aa`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/tools/src/index.ts#L1)

## D06 · deepseek-harness {#evidence-d06}

- 相对路径：`deepseek-harness/packages/core/tools/src/types.ts`
- 定位：第 1 行，`file`；文件共 63 行。
- SHA-256：`26c2c9ac831526d9bcefe5ee3b9b1a6a8ca313d43efffe579670366790539bb6`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/tools/src/types.ts#L1)

## D07 · deepseek-harness {#evidence-d07}

- 相对路径：`deepseek-harness/packages/core/session/src/index.ts`
- 定位：第 984 行，`deriveMessages`；文件共 1453 行。
- SHA-256：`c1f08f7dcf4075eeebb13e6ea06b3f348bfeb85b8a5d4e4bfd1c3b93c1959332`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/session/src/index.ts#L984)

## D08 · deepseek-harness {#evidence-d08}

- 相对路径：`deepseek-harness/packages/core/session/src/types.ts`
- 定位：第 282 行，`SessionEventMap`；文件共 562 行。
- SHA-256：`515cba50f366b06dc3caaab45e8ce98c48c80fc07684437aba014df13ce04f2f`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/session/src/types.ts#L282)

## D09 · deepseek-harness {#evidence-d09}

- 相对路径：`deepseek-harness/packages/core/scope/src/index.ts`
- 定位：第 1 行，`file`；文件共 204 行。
- SHA-256：`074b8f0c3fa2e240effd0a7e65c54be7c14debc1e53bb712334ce20d15affe4a`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/core/scope/src/index.ts#L1)

## D10 · deepseek-harness {#evidence-d10}

- 相对路径：`deepseek-harness/packages/session/session-persistence-jsonl/src/generation.ts`
- 定位：第 1 行，`file`；文件共 1059 行。
- SHA-256：`43a400aaa47be789173ef4d5dd3226bce374cbfac300c2bff199b5a7d108efd6`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/session/session-persistence-jsonl/src/generation.ts#L1)

## D11 · deepseek-harness {#evidence-d11}

- 相对路径：`deepseek-harness/packages/session/session-persistence-jsonl/src/catalog-migration.ts`
- 定位：第 1 行，`file`；文件共 92 行。
- SHA-256：`414ffd8d3ed6b80bb239f54916ec64e6b5f3d06ebc5a0d950922391271d612fa`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/session/session-persistence-jsonl/src/catalog-migration.ts#L1)

## D12 · deepseek-harness {#evidence-d12}

- 相对路径：`deepseek-harness/packages/compaction/compaction-basic/README.md`
- 定位：第 1 行，`file`；文件共 260 行。
- SHA-256：`dd5409de780a6463f83fbee08bc0d07fc11de210463d1927f1b11cae840629eb`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/compaction/compaction-basic/README.md#L1)

## D13 · deepseek-harness {#evidence-d13}

- 相对路径：`deepseek-harness/packages/subagent/subagent/README.md`
- 定位：第 1 行，`file`；文件共 227 行。
- SHA-256：`ac080c1b7b9224a5b86f43fceee9384f0e86daea73bfe62811891b62608e6d2f`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/subagent/subagent/README.md#L1)

## D14 · deepseek-harness {#evidence-d14}

- 相对路径：`deepseek-harness/packages/sandbox/sandbox-policy/README.md`
- 定位：第 1 行，`file`；文件共 160 行。
- SHA-256：`d16b0648c8d17beb25fff96277e17ff24371497c09a5e2e1c28e34c94f60f80a`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/sandbox/sandbox-policy/README.md#L1)

## D15 · deepseek-harness {#evidence-d15}

- 相对路径：`deepseek-harness/docs/capability-seams.md`
- 定位：第 1 行，`file`；文件共 714 行。
- SHA-256：`ea9484aec30cc85fcb80d3205c9970fcef17ab83d6105f3a1c2c19b4cb2deaf0`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/docs/capability-seams.md#L1)

## D16 · deepseek-harness {#evidence-d16}

- 相对路径：`deepseek-harness/docs/cordis-primer.md`
- 定位：第 1 行，`file`；文件共 45 行。
- SHA-256：`f0cc573cc10b60d1bd76039fb0bd666edfb32c9b18027d4dc301c042a9e65d58`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/docs/cordis-primer.md#L1)

## D17 · deepseek-harness {#evidence-d17}

- 相对路径：`deepseek-harness/LICENSE`
- 定位：第 1 行，`file`；文件共 21 行。
- SHA-256：`ebb4f09972aee8608be255debaf78451a68e95c290f55c240dec2ecfa16ea6be`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/LICENSE#L1)

## D18 · deepseek-harness {#evidence-d18}

- 相对路径：`deepseek-harness/packages/llm/llm-pi-ai/README.md`
- 定位：第 1 行，`file`；文件共 273 行。
- SHA-256：`da63b3f79622bcb69ebafc345b04c4b930a5bd871c2cb13d1adcacf7afe3aa5e`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/llm/llm-pi-ai/README.md#L1)

## D19 · deepseek-harness {#evidence-d19}

- 相对路径：`deepseek-harness/packages/compaction/compaction-basic/src/index.ts`
- 定位：第 113 行，`class BasicCompactionEngine`；文件共 452 行。
- SHA-256：`c298756c1d06a24593dc573e08f337f7f012675bcfaa675edb7d5368b19649f6`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/compaction/compaction-basic/src/index.ts#L113)

## D20 · deepseek-harness {#evidence-d20}

- 相对路径：`deepseek-harness/packages/compaction/compaction-basic/src/config.ts`
- 定位：第 153 行，`function resolveCompactSpec`；文件共 362 行。
- SHA-256：`4972edc6447dcff87eab54c3a9c5984171238aa06aa0eb34ffde4bfac4ce1275`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/compaction/compaction-basic/src/config.ts#L153)

## D21 · deepseek-harness {#evidence-d21}

- 相对路径：`deepseek-harness/packages/compaction/compaction-basic/src/region.ts`
- 定位：第 117 行，`function selectCompactableRange`；文件共 600 行。
- SHA-256：`295b53cc9e924f7cb2e843e0d0d296e89ead73da2aab9790282db30736e2e063`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/compaction/compaction-basic/src/region.ts#L117)

## D22 · deepseek-harness {#evidence-d22}

- 相对路径：`deepseek-harness/packages/compaction/compaction-basic/src/summarizer.ts`
- 定位：第 120 行，`function summarizeWithLlm`；文件共 221 行。
- SHA-256：`03ef6eb0b6a011530829820e30ff709c2c1b34cfa37a98c19c0037432b9d2f55`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/compaction/compaction-basic/src/summarizer.ts#L120)

## D23 · deepseek-harness {#evidence-d23}

- 相对路径：`deepseek-harness/packages/skill/tool-skill/src/index.ts`
- 定位：第 1 行，`file`；文件共 433 行。
- SHA-256：`29f6cf10c7247379298d9a96a53aef9cb2b21dcf7266f57ab147860b27d7cc44`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/skill/tool-skill/src/index.ts#L1)

## D24 · deepseek-harness {#evidence-d24}

- 相对路径：`deepseek-harness/packages/skill/skill/src/index.ts`
- 定位：第 356 行，`class SkillRegistry`；文件共 868 行。
- SHA-256：`af4fad67fb086c3f5c93aed4604830718b4535e7e59a60d680404b07ea08477c`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/skill/skill/src/index.ts#L356)

## D25 · deepseek-harness {#evidence-d25}

- 相对路径：`deepseek-harness/packages/mcp/mcp-client/src/index.ts`
- 定位：第 154 行，`async function apply`；文件共 203 行。
- SHA-256：`f279bd88743ca73b0d9834915d1bb31e455e21c87f4990808cfd55b273db4d1c`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/mcp/mcp-client/src/index.ts#L154)

## D26 · deepseek-harness {#evidence-d26}

- 相对路径：`deepseek-harness/packages/mcp/mcp-client/README.md`
- 定位：第 1 行，`file`；文件共 229 行。
- SHA-256：`346ad21f0c7f8bd7248a021513228769fcde1dec7065a3ea77e809f999805806`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/mcp/mcp-client/README.md#L1)

## D27 · deepseek-harness {#evidence-d27}

- 相对路径：`deepseek-harness/packages/mcp/mcp-client/src/tools.ts`
- 定位：第 113 行，`async function syncTools`；文件共 511 行。
- SHA-256：`59203150bda479a990afcdaf60483a35a836887926892e1074e02d0294c01af9`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/mcp/mcp-client/src/tools.ts#L113)

## D28 · deepseek-harness {#evidence-d28}

- 相对路径：`deepseek-harness/packages/sandbox/sandbox/src/index.ts`
- 定位：第 40 行，`export interface SandboxExecutionPolicy`；文件共 182 行。
- SHA-256：`46592025ce36d04ff8d1bfa9d6594dd8d1527883649ccf40ff7a169e94e68dc6`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/sandbox/sandbox/src/index.ts#L40)

## D29 · deepseek-harness {#evidence-d29}

- 相对路径：`deepseek-harness/packages/sandbox/sandbox-policy/src/index.ts`
- 定位：第 164 行，`resolve(request: SandboxPolicyRequest`；文件共 183 行。
- SHA-256：`6fce58e5bf63475f761871389bbf01043fba859f22e44c805522c39afbff32d6`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/sandbox/sandbox-policy/src/index.ts#L164)

## D30 · deepseek-harness {#evidence-d30}

- 相对路径：`deepseek-harness/packages/sandbox/sandbox-local/src/index.ts`
- 定位：第 160 行，`const PLATFORM_CHAINS`；文件共 583 行。
- SHA-256：`282709d0bf789ad3ab9ec6a706f3aeaeac1632d80a08ded507a7b7caff860ac2`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/sandbox/sandbox-local/src/index.ts#L160)

## D31 · deepseek-harness {#evidence-d31}

- 相对路径：`deepseek-harness/packages/llm/llm/src/assembler.ts`
- 定位：第 38 行，`export class BlockAssembler`；文件共 208 行。
- SHA-256：`a2d065645058a70195a504b101e9eed23df3eaced3def868d602f3a863b03887`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/llm/llm/src/assembler.ts#L38)

## D32 · deepseek-harness {#evidence-d32}

- 相对路径：`deepseek-harness/packages/llm/llm/src/retry-policy.ts`
- 定位：第 149 行，`export function resolveRetryPolicy`；文件共 195 行。
- SHA-256：`eee2423a0152096026446dd651f29678e0c504f0349a91758720f01f74efa871`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/llm/llm/src/retry-policy.ts#L149)

## D33 · deepseek-harness {#evidence-d33}

- 相对路径：`deepseek-harness/packages/subagent/subagent/src/lifecycle.ts`
- 定位：第 134 行，`export function epochStopReason`；文件共 169 行。
- SHA-256：`3f892ad12033aaf30a8c81b404eefaadb0974bd54d993631970a3c6509a13b92`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/subagent/subagent/src/lifecycle.ts#L134)

## D34 · deepseek-harness {#evidence-d34}

- 相对路径：`deepseek-harness/packages/subagent/subagent/src/manager.ts`
- 定位：第 130 行，`export class SubagentManager`；文件共 1493 行。
- SHA-256：`87298342da27dd567897bd23145fdec7d841e1f26a4e6b5dfa9a48b0b477d03e`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/subagent/subagent/src/manager.ts#L130)

## D35 · deepseek-harness {#evidence-d35}

- 相对路径：`deepseek-harness/packages/subagent/subagent-fork-in-process/src/index.ts`
- 定位：第 46 行，`function completedTurnPrefix`；文件共 83 行。
- SHA-256：`1bc4ff5ff22c20937b6224ffe208a3c37b18c2b741ed77330c27432ce23cf30e`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/subagent/subagent-fork-in-process/src/index.ts#L46)

## D36 · deepseek-harness {#evidence-d36}

- 相对路径：`deepseek-harness/packages/llm/llm-retry/src/index.ts`
- 定位：第 194 行，`async function recover`；文件共 259 行。
- SHA-256：`d33553781ed2118aab3b249c159fae550d359627565e4714c9ea599e474b8093`
- [固定提交源码](https://github.com/deepseek-ai/deepseek-harness/blob/687f282e8625c6b8d11ff58211a90524be2e4317/packages/llm/llm-retry/src/index.ts#L194)

## P01 · pi {#evidence-p01}

- 相对路径：`pi/packages/agent/src/agent-loop.ts`
- 定位：第 163 行，`async function runLoop`；文件共 949 行。
- SHA-256：`28a2b03e34a7e32f004aa851e54d3b5be9dad71c392205614cbc9abdf3a9020a`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/agent/src/agent-loop.ts#L163)

## P02 · pi {#evidence-p02}

- 相对路径：`pi/packages/agent/src/types.ts`
- 定位：第 47 行，`type ToolExecutionMode`；文件共 539 行。
- SHA-256：`2e116ef60fdaca4e26be5a1ace8d8b47f545d648d365de60b8c9f9d1ba629ee4`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/agent/src/types.ts#L47)

## P03 · pi {#evidence-p03}

- 相对路径：`pi/packages/agent/src/agent.ts`
- 定位：第 188 行，`class Agent`；文件共 613 行。
- SHA-256：`7024a3145a6ebc951a0f030164adb1dfb12d33d6e0dbbac15ef0efda49c87457`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/agent/src/agent.ts#L188)

## P04 · pi {#evidence-p04}

- 相对路径：`pi/packages/coding-agent/src/core/agent-session.ts`
- 定位：第 379 行，`class AgentSession`；文件共 4428 行。
- SHA-256：`e0fa206e8c49a98c024708068df39c0e4944f4251633425fc083b2fbb5ec0ac6`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/agent-session.ts#L379)

## P05 · pi {#evidence-p05}

- 相对路径：`pi/packages/coding-agent/src/core/session-manager.ts`
- 定位：第 57 行，`interface SessionEntryBase`；文件共 2013 行。
- SHA-256：`450d82c529933214e088b8422f00061815e617f352f6c834689787a314064bff`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/session-manager.ts#L57)

## P06 · pi {#evidence-p06}

- 相对路径：`pi/packages/coding-agent/src/core/compaction/compaction.ts`
- 定位：第 126 行，`DEFAULT_COMPACTION_SETTINGS`；文件共 1099 行。
- SHA-256：`f5bbc427e337be708bd15297806c0acaf7cb0ee65cc4af77e6e48c3e3937894f`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/compaction/compaction.ts#L126)

## P07 · pi {#evidence-p07}

- 相对路径：`pi/packages/coding-agent/src/core/tools/edit.ts`
- 定位：第 143 行，`function createEditToolDefinition`；文件共 220 行。
- SHA-256：`31a368c14cf5437ecac157765660001b16063302d9bd746303d6d1b1dcb5625d`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/tools/edit.ts#L143)

## P08 · pi {#evidence-p08}

- 相对路径：`pi/packages/coding-agent/src/core/tools/file-mutation-queue.ts`
- 定位：第 1 行，`file`；文件共 61 行。
- SHA-256：`33cb06ac9bcdf32c8b84d9d12e33be44c503a7670f668e003a3262cd34294d11`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/tools/file-mutation-queue.ts#L1)

## P09 · pi {#evidence-p09}

- 相对路径：`pi/packages/coding-agent/src/core/project-trust.ts`
- 定位：第 47 行，`function resolveProjectTrusted`；文件共 97 行。
- SHA-256：`7e5875d8786c7a6b28e8263d879f1454e6273c6cd432a8da76d75ee5ff51088f`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/project-trust.ts#L47)

## P10 · pi {#evidence-p10}

- 相对路径：`pi/packages/coding-agent/src/core/extensions/runner.ts`
- 定位：第 1 行，`file`；文件共 1565 行。
- SHA-256：`3cd6d1ad18e8e4c7adf722aed9291bc64f06e3a7d461755c21e3cba4819f4e5e`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/extensions/runner.ts#L1)

## P11 · pi {#evidence-p11}

- 相对路径：`pi/packages/coding-agent/src/core/extensions/types.ts`
- 定位：第 1 行，`file`；文件共 2304 行。
- SHA-256：`cb54c7a4fedb3473bb995694bbc1f2988c144fb0b802bfd1b656816bc25d0f25`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/extensions/types.ts#L1)

## P12 · pi {#evidence-p12}

- 相对路径：`pi/packages/durable/README.md`
- 定位：第 1 行，`file`；文件共 874 行。
- SHA-256：`4ffad270954f23a8c35514de5494b1953623ef1147fea0f7089f28382710393a`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/durable/README.md#L1)

## P13 · pi {#evidence-p13}

- 相对路径：`pi/packages/durable/src/harness/inbox.ts`
- 定位：第 51 行，`async function prepareBoundary`；文件共 168 行。
- SHA-256：`ead422265ffff2ffd5bc2e6047b62d8b932732e7addd3e0cc964f9fcb9e45437`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/durable/src/harness/inbox.ts#L51)

## P14 · pi {#evidence-p14}

- 相对路径：`pi/packages/durable/src/tasks.ts`
- 定位：第 1 行，`file`；文件共 8 行。
- SHA-256：`08ed979b5ae25122aca620952deeb0cde4956c41869ae5a51d47fc7aaf2627d9`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/durable/src/tasks.ts#L1)

## P15 · pi {#evidence-p15}

- 相对路径：`pi/packages/ai/src/types.ts`
- 定位：第 1 行，`file`；文件共 898 行。
- SHA-256：`2a48985ce8f4c1710f1e107433e8cc23ba32cf03a1bd5e53565137c887a6f7c3`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/ai/src/types.ts#L1)

## P16 · pi {#evidence-p16}

- 相对路径：`pi/LICENSE`
- 定位：第 1 行，`file`；文件共 21 行。
- SHA-256：`0457f5bcec3b3b211605dfb5d1a49042fd638f3686a410fe099c24a25af13c48`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/LICENSE#L1)

## P17 · pi {#evidence-p17}

- 相对路径：`pi/packages/coding-agent/src/core/tools/bash.ts`
- 定位：第 1 行，`file`；文件共 442 行。
- SHA-256：`de2b54d4f4bfbb844ce6d8077f63d715f7d8e80079dd9689b561e45b6679c81b`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/tools/bash.ts#L1)

## P18 · pi {#evidence-p18}

- 相对路径：`pi/packages/coding-agent/src/modes/rpc/rpc-mode.ts`
- 定位：第 1 行，`file`；文件共 819 行。
- SHA-256：`d534e0fa1484844a097963d5f4fb4df9397c5a1b5e29e42aed7575ab6f67989b`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/modes/rpc/rpc-mode.ts#L1)

## P19 · pi {#evidence-p19}

- 相对路径：`pi/packages/coding-agent/src/core/skills.ts`
- 定位：第 358 行，`function formatSkillsForPrompt`；文件共 514 行。
- SHA-256：`8dcc644dbabbb34238f609ecf191c0da370d74873ccaccaf3c3cd0e7703d9431`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/skills.ts#L358)

## P20 · pi {#evidence-p20}

- 相对路径：`pi/packages/coding-agent/src/core/mcp-servers.ts`
- 定位：第 52 行，`export type McpExposure`；文件共 346 行。
- SHA-256：`0aaad23b26f31f743bdd117754f4c871ea821279bf68f8ba5d71eccbb1602c6a`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/mcp-servers.ts#L52)

## P21 · pi {#evidence-p21}

- 相对路径：`pi/packages/coding-agent/src/core/tools/edit-diff.ts`
- 定位：第 300 行，`export function applyEditsToNormalizedContent`；文件共 556 行。
- SHA-256：`f85a9809eb44b9828236050cf38a8e45933e5cfd583a186e9a0e55a664dd3e8d`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/coding-agent/src/core/tools/edit-diff.ts#L300)

## P22 · pi {#evidence-p22}

- 相对路径：`pi/packages/durable/src/harness/tool.ts`
- 定位：第 125 行，`export const ToolTask`；文件共 964 行。
- SHA-256：`e1417cf44bcf8c75e0978e2ed31e1e87f7c36871113eec535db16d0fc621c9a9`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/durable/src/harness/tool.ts#L125)

## P23 · pi {#evidence-p23}

- 相对路径：`pi/packages/durable/src/harness/scheduler.ts`
- 定位：第 1366 行，`#parked(record:`；文件共 2507 行。
- SHA-256：`77e4f0f71c099308cf7ead442c9a1335b5156a1a1194315cd41f2aa06ef4a1ab`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/durable/src/harness/scheduler.ts#L1366)

## P24 · pi {#evidence-p24}

- 相对路径：`pi/packages/durable/src/harness/view.ts`
- 定位：第 78 行，`class ConversationViews`；文件共 267 行。
- SHA-256：`e9d8e017089060a6deab7465630471b0405f563861094971cc10ea351d3a6823`
- [固定提交源码](https://github.com/earendil-works/pi/blob/16f5f0af4d85ca583d045ceb5ed6d646fcaf7761/packages/durable/src/harness/view.ts#L78)

## A01 · ccsource {#evidence-a01}

- 相对路径：`ccsource/package/package.json`
- 定位：第 3 行，`"version"`；文件共 35 行。
- SHA-256：`0fb4bb78f60c07760788a10f53a444d5c3b22228edd124772abe03d55f34ebe9`

## A02 · ccsource {#evidence-a02}

- 相对路径：`ccsource/package/cli.js.map`
- 定位：第 1 行，`file`；文件共 4764 行。
- SHA-256：`7965012b7a5fc9e09d8d747a04c5c32b94696924536e217f686bb1e7ee70a657`

## A03 · ccsource {#evidence-a03}

- 相对路径：`ccsource/package/src-extracted/src/query.ts`
- 定位：第 241 行，`async function* queryLoop`；文件共 1729 行。
- SHA-256：`74e0ce0d86cfd453add8dc1d15ccb6311b02964b8321e3721b8e71fbd87252ce`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A04 · ccsource {#evidence-a04}

- 相对路径：`ccsource/package/src-extracted/src/Tool.ts`
- 定位：第 362 行，`export type Tool<`；文件共 792 行。
- SHA-256：`29d555ab8e50de9fb005264b5334aba870f1da472198e14d0b3ab0bf86d7c49c`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A05 · ccsource {#evidence-a05}

- 相对路径：`ccsource/package/src-extracted/src/services/tools/StreamingToolExecutor.ts`
- 定位：第 40 行，`class StreamingToolExecutor`；文件共 530 行。
- SHA-256：`ee17dce704af73787c9ed76dbbc638167521e5c1f68c9436149378bb3358601c`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A06 · ccsource {#evidence-a06}

- 相对路径：`ccsource/package/src-extracted/src/services/tools/toolExecution.ts`
- 定位：第 599 行，`async function checkPermissionsAndCallTool`；文件共 1745 行。
- SHA-256：`77aae23a5b8b68aa1ee32b99eb25c6360071d7a4c4c46e6d2c95d584fb6e25e0`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A07 · ccsource {#evidence-a07}

- 相对路径：`ccsource/package/src-extracted/src/services/compact/autoCompact.ts`
- 定位：第 72 行，`getAutoCompactThreshold`；文件共 351 行。
- SHA-256：`1946b5ea23fa2eda91955378641258fb8f19e7742f06ce17d6caae7f2d3c921a`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A08 · ccsource {#evidence-a08}

- 相对路径：`ccsource/package/src-extracted/src/services/compact/microCompact.ts`
- 定位：第 1 行，`file`；文件共 530 行。
- SHA-256：`4509572de2be2f8024820df3e1e1f79e32074c708e56b3f5de0b37764f0d7bf2`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A09 · ccsource {#evidence-a09}

- 相对路径：`ccsource/package/src-extracted/src/services/compact/compact.ts`
- 定位：第 1 行，`file`；文件共 1705 行。
- SHA-256：`80af045d9247de7dda0cbe7aab653329d0b7c8b62a2cdadfd86238305df71f53`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A10 · ccsource {#evidence-a10}

- 相对路径：`ccsource/package/src-extracted/src/utils/sessionStorage.ts`
- 定位：第 154 行，`function isChainParticipant`；文件共 5105 行。
- SHA-256：`8a123ebce1ee72b9081d34b8f3697e5fcc9c7576df5b98e4206bb28414134412`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A11 · ccsource {#evidence-a11}

- 相对路径：`ccsource/package/src-extracted/src/utils/permissions/permissions.ts`
- 定位：第 1 行，`file`；文件共 1486 行。
- SHA-256：`3a28acc854014fe49751aeaf7ca2648239cb309811fd948db3bcc91b46baed05`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A12 · ccsource {#evidence-a12}

- 相对路径：`ccsource/package/src-extracted/src/tools/BashTool/bashPermissions.ts`
- 定位：第 1 行，`file`；文件共 2621 行。
- SHA-256：`8656e6b59b6923cd730451f29dccac140e9622dd64c0a5ae6c1d52a5ca1b987b`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A13 · ccsource {#evidence-a13}

- 相对路径：`ccsource/package/src-extracted/src/tools/AgentTool/AgentTool.tsx`
- 定位：第 1 行，`file`；文件共 1398 行。
- SHA-256：`322e8d097352d61d42bc2aa30b7e2509c3a9782d8d77434f960f7f650143401a`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A14 · ccsource {#evidence-a14}

- 相对路径：`ccsource/package/src-extracted/src/hooks/useCanUseTool.tsx`
- 定位：第 1 行，`file`；文件共 204 行。
- SHA-256：`3689b30326118e94bb53a8cc1fa1761d1c0b1bff6489162f1dd0771ec8b8b953`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A15 · ccsource {#evidence-a15}

- 相对路径：`ccsource/package/LICENSE.md`
- 定位：第 1 行，`file`；文件共 1 行。
- SHA-256：`8ce94b9478bb9868f9641f818e06cd722fbe55d4c22e2d2ed11971b20146173a`

## A16 · ccsource {#evidence-a16}

- 相对路径：`ccsource/package/src-extracted/src/utils/sessionRestore.ts`
- 定位：第 1 行，`file`；文件共 551 行。
- SHA-256：`9dfe9c2203aac5c3cc6d49e45bf2f8fd381582781b5cec3abbc4ceb6d219e177`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A17 · ccsource {#evidence-a17}

- 相对路径：`ccsource/package/src-extracted/src/services/compact/timeBasedMCConfig.ts`
- 定位：第 30 行，`const TIME_BASED_MC_CONFIG_DEFAULTS`；文件共 43 行。
- SHA-256：`aede0336973766a4ae25d2625156d3f9300736896ed4691b566e1c98472fd6f9`
- 本地提取文本与发布包 source map 嵌入文本一致。

## A18 · ccsource {#evidence-a18}

- 相对路径：`ccsource/package/src-extracted/src/utils/sandbox/sandbox-adapter.ts`
- 定位：第 704 行，`async function wrapWithSandbox`；文件共 985 行。
- SHA-256：`7a69378764884ce8bd042e6286ee24468a77c18bb2582aa007bc4b3fd799bfcb`
- 本地提取文本与发布包 source map 嵌入文本一致。

## 官方补充资料

- [OpenAI：Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform)，访问日期 2026-10-30，仅用于 harness 术语与职责说明。
- 开源项目的许可证与署名见仓库 `NOTICE.md` 和 `LICENSES/`。
