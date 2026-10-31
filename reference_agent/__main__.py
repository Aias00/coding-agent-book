import argparse
import asyncio
from pathlib import Path
from .core import BROKEN, FixtureModel, InjectedCrash, Kernel, OutcomeUnknown, Policy, Store, Workspace

def main():
    parser = argparse.ArgumentParser(description='Bounded, model-driven Coding Agent reference kernel')
    parser.add_argument('command', choices=['init', 'run', 'events'])
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--allow-edit', action='store_true')
    parser.add_argument('--crash-after-edit', action='store_true')
    args = parser.parse_args()
    if args.command == 'init':
        args.workspace.mkdir(parents=True, exist_ok=False)
        (args.workspace / 'paths.py').write_text(BROKEN)
        (args.workspace / 'task.txt').write_text('Repair lexical path containment and verify the four fixture cases.\n')
        print('Initialized:', args.workspace)
        return 0
    workspace = Workspace(args.workspace)
    store = Store(workspace.root / '.agent/state.sqlite')
    try:
        if args.command == 'events':
            from .core import canonical
            for event in store.events(): print(canonical(event))
            return 0
        def fault(call, outcome):
            if args.crash_after_edit and call.name == 'edit' and outcome.status == 'ok': raise InjectedCrash()
        kernel = Kernel(store, workspace, FixtureModel(), Policy(args.allow_edit), after_effect=fault)
        try:
            result = asyncio.run(kernel.run())
            print(result)
            return 0 if result == 'completed' else 2
        except (InjectedCrash, OutcomeUnknown) as error:
            print(type(error).__name__ + ': edit may already have happened; inspect the workspace and durable calls')
            return 2
    finally:
        store.close()

if __name__ == '__main__': raise SystemExit(main())
