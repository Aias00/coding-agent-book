#!/usr/bin/env python3
"""Record only reviewed source identities; never copy upstream implementations."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'codex': [
        ('C01', 'codex-rs/core/src/session/turn.rs', 'async fn run_turn'),
        ('C02', 'codex-rs/core/src/session/step_context.rs', 'struct StepContext'),
        ('C03', 'codex-rs/core/src/tools/router.rs', 'struct ToolRouter'),
        ('C04', 'codex-rs/core/src/tools/registry.rs', 'struct ToolRegistry'),
        ('C05', 'codex-rs/core/src/tools/orchestrator.rs', 'pub async fn run'),
        ('C06', 'codex-rs/core/src/tools/parallel.rs', 'struct ToolCallRuntime'),
        ('C07', 'codex-rs/core/src/unified_exec/process_manager.rs', 'impl UnifiedExecProcessManager'),
        ('C08', 'codex-rs/core/src/compact.rs', 'run_inline_auto_compact_task'),
        ('C09', 'codex-rs/core/src/session/rollout_reconstruction.rs', 'fn select_input_compaction'),
        ('C10', 'codex-rs/rollout/src/recorder.rs', 'struct RolloutRecorder'),
        ('C11', 'codex-rs/core/src/tools/spec_plan.rs', 'build_tool_router'),
        ('C12', 'codex-rs/core/src/tools/sandboxing.rs', 'trait ToolRuntime'),
        ('C13', 'codex-rs/core/src/session/input_queue.rs', ''),
        ('C14', 'codex-rs/core/src/session/multi_agents.rs', ''),
        ('C15', 'codex-rs/app-server/README.md', ''),
        ('C16', 'LICENSE', 'Apache License'),
        ('C17', 'codex-rs/core/src/compact_remote_v2.rs', 'fn build_v2_compacted_history'),
        ('C18', 'codex-rs/core/src/compact_remote_v2_installation.rs', 'candidate.model_info.slug'),
        ('C19', 'codex-rs/core/src/compact_token_budget.rs', 'sess.start_new_context_window'),
        ('C20', 'codex-rs/core/src/session/async_compaction.rs', 'candidate.prefix.generation'),
        ('C21', 'codex-rs/protocol/src/models.rs', '    Compaction {'),
        ('C22', 'codex-rs/linux-sandbox/src/linux_run_main.rs', 'pub struct LinuxSandboxCommand'),
    ],
    'deepseek-harness': [
        ('D01', 'docs/architecture.md', '## Turn flow'),
        ('D02', 'packages/core/agent-loop/src/agent.ts', 'prepareCall'),
        ('D03', 'packages/core/agent-loop/src/tool-calls.ts', 'async function executeToolCalls'),
        ('D04', 'packages/core/agent-loop/src/assistant-stream.ts', 'class AssistantStreamAttempt'),
        ('D05', 'packages/core/tools/src/index.ts', ''),
        ('D06', 'packages/core/tools/src/types.ts', ''),
        ('D07', 'packages/core/session/src/index.ts', 'deriveMessages'),
        ('D08', 'packages/core/session/src/types.ts', 'SessionEventMap'),
        ('D09', 'packages/core/scope/src/index.ts', ''),
        ('D10', 'packages/session/session-persistence-jsonl/src/generation.ts', ''),
        ('D11', 'packages/session/session-persistence-jsonl/src/catalog-migration.ts', ''),
        ('D12', 'packages/compaction/compaction-basic/README.md', ''),
        ('D13', 'packages/subagent/subagent/README.md', ''),
        ('D14', 'packages/sandbox/sandbox-policy/README.md', ''),
        ('D15', 'docs/capability-seams.md', ''),
        ('D16', 'docs/cordis-primer.md', ''),
        ('D17', 'LICENSE', ''),
        ('D18', 'packages/llm/llm-pi-ai/README.md', ''),
        ('D19', 'packages/compaction/compaction-basic/src/index.ts', 'class BasicCompactionEngine'),
        ('D20', 'packages/compaction/compaction-basic/src/config.ts', 'function resolveCompactSpec'),
        ('D21', 'packages/compaction/compaction-basic/src/region.ts', 'function selectCompactableRange'),
        ('D22', 'packages/compaction/compaction-basic/src/summarizer.ts', 'function summarizeWithLlm'),
        ('D23', 'packages/skill/tool-skill/src/index.ts', ''),
        ('D24', 'packages/skill/skill/src/index.ts', 'class SkillRegistry'),
        ('D25', 'packages/mcp/mcp-client/src/index.ts', 'async function apply'),
        ('D26', 'packages/mcp/mcp-client/README.md', ''),
        ('D27', 'packages/mcp/mcp-client/src/tools.ts', 'async function syncTools'),
        ('D28', 'packages/sandbox/sandbox/src/index.ts', 'export interface SandboxExecutionPolicy'),
        ('D29', 'packages/sandbox/sandbox-policy/src/index.ts', 'resolve(request: SandboxPolicyRequest'),
        ('D30', 'packages/sandbox/sandbox-local/src/index.ts', 'const PLATFORM_CHAINS'),
    ],
    'pi': [
        ('P01', 'packages/agent/src/agent-loop.ts', 'async function runLoop'),
        ('P02', 'packages/agent/src/types.ts', 'type ToolExecutionMode'),
        ('P03', 'packages/agent/src/agent.ts', 'class Agent'),
        ('P04', 'packages/coding-agent/src/core/agent-session.ts', 'class AgentSession'),
        ('P05', 'packages/coding-agent/src/core/session-manager.ts', 'interface SessionEntryBase'),
        ('P06', 'packages/coding-agent/src/core/compaction/compaction.ts', 'DEFAULT_COMPACTION_SETTINGS'),
        ('P07', 'packages/coding-agent/src/core/tools/edit.ts', 'function createEditToolDefinition'),
        ('P08', 'packages/coding-agent/src/core/tools/file-mutation-queue.ts', ''),
        ('P09', 'packages/coding-agent/src/core/project-trust.ts', 'function resolveProjectTrusted'),
        ('P10', 'packages/coding-agent/src/core/extensions/runner.ts', ''),
        ('P11', 'packages/coding-agent/src/core/extensions/types.ts', ''),
        ('P12', 'packages/durable/README.md', ''),
        ('P13', 'packages/durable/src/harness/inbox.ts', 'async function prepareBoundary'),
        ('P14', 'packages/durable/src/tasks.ts', ''),
        ('P15', 'packages/ai/src/types.ts', ''),
        ('P16', 'LICENSE', ''),
        ('P17', 'packages/coding-agent/src/core/tools/bash.ts', ''),
        ('P18', 'packages/coding-agent/src/modes/rpc/rpc-mode.ts', ''),
        ('P19', 'packages/coding-agent/src/core/skills.ts', 'function formatSkillsForPrompt'),
        ('P20', 'packages/coding-agent/src/core/mcp-servers.ts', 'export type McpExposure'),
    ],
    'ccsource': [
        ('A01', 'package/package.json', '"version"'),
        ('A02', 'package/cli.js.map', ''),
        ('A03', 'package/src-extracted/src/query.ts', 'async function* queryLoop'),
        ('A04', 'package/src-extracted/src/Tool.ts', 'export type Tool<'),
        ('A05', 'package/src-extracted/src/services/tools/StreamingToolExecutor.ts', 'class StreamingToolExecutor'),
        ('A06', 'package/src-extracted/src/services/tools/toolExecution.ts', 'async function checkPermissionsAndCallTool'),
        ('A07', 'package/src-extracted/src/services/compact/autoCompact.ts', 'getAutoCompactThreshold'),
        ('A08', 'package/src-extracted/src/services/compact/microCompact.ts', ''),
        ('A09', 'package/src-extracted/src/services/compact/compact.ts', ''),
        ('A10', 'package/src-extracted/src/utils/sessionStorage.ts', 'function isChainParticipant'),
        ('A11', 'package/src-extracted/src/utils/permissions/permissions.ts', ''),
        ('A12', 'package/src-extracted/src/tools/BashTool/bashPermissions.ts', ''),
        ('A13', 'package/src-extracted/src/tools/AgentTool/AgentTool.tsx', ''),
        ('A14', 'package/src-extracted/src/hooks/useCanUseTool.tsx', ''),
        ('A15', 'package/LICENSE.md', ''),
        ('A16', 'package/src-extracted/src/utils/sessionRestore.ts', ''),
        ('A17', 'package/src-extracted/src/services/compact/timeBasedMCConfig.ts', 'const TIME_BASED_MC_CONFIG_DEFAULTS'),
        ('A18', 'package/src-extracted/src/utils/sandbox/sandbox-adapter.ts', 'async function wrapWithSandbox'),
    ],
}

def git(directory, *args):
    result = subprocess.run(['git', '-C', str(directory), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=Path('/Volumes/data'))
    args = parser.parse_args()
    edition = json.loads((ROOT / 'edition.json').read_text())['edition']
    previous = json.loads((ROOT / 'research/sources.json').read_text())
    result = {'edition': edition, 'review_date': '2026-10-30', 'projects': {}, 'files': []}
    for name, files in FILES.items():
        directory = args.source_root / name
        commit = git(directory, 'rev-parse', 'HEAD')
        if commit != previous['projects'].get(name, {}).get('commit'):
            raise ValueError(f'Source snapshot changed for {name}; review before updating book evidence')
        remote = git(directory, 'remote', 'get-url', 'origin')
        result['projects'][name] = {'commit': commit, 'remote': remote,
            'working_tree_status': git(directory, 'status', '--porcelain') if commit else None}
        sourcemap = json.loads((directory / 'package/cli.js.map').read_text()) if name == 'ccsource' else None
        embedded = dict(zip(sourcemap['sources'], sourcemap['sourcesContent'])) if sourcemap else {}
        for key, relative, needle in files:
            path = directory / relative
            raw = path.read_bytes()
            body = raw.decode('utf-8')
            lines = body.splitlines()
            line = next((i + 1 for i, text in enumerate(lines) if needle and needle in text), 1)
            if needle and line == 1 and needle not in lines[0]:
                raise ValueError(f'Missing locator: {key}: {needle}')
            url = f'{remote.removesuffix(".git")}/blob/{commit}/{relative}#L{line}' if commit else None
            row = {'id': key, 'project': name, 'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(),
                'lines': len(lines), 'locator': needle or 'file', 'line': line, 'url': url}
            if name == 'ccsource' and '/src-extracted/' in relative:
                map_name = '../' + relative.split('/src-extracted/', 1)[1]
                row['matches_embedded_source'] = embedded.get(map_name) == body
                if not row['matches_embedded_source']:
                    raise ValueError(f'Extracted file differs from map: {relative}')
            result['files'].append(row)
    target = ROOT / 'research/sources.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'Recorded {len(result["files"])} source files; extracted Claude Code files verified against sourcesContent.')

if __name__ == '__main__':
    main()
