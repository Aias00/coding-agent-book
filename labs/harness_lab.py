#!/usr/bin/env python3
"""Deterministic harness mechanics lab. No model API, credentials, or shell required."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OLD = '''import os

def is_within(base, candidate):
    return os.path.abspath(candidate).startswith(os.path.abspath(base))
'''
NEW = '''import os

def is_within(base, candidate):
    base = os.path.abspath(base)
    candidate = os.path.abspath(candidate)
    try:
        return os.path.commonpath([base, candidate]) == base
    except ValueError:
        return False
'''
TEST = '''import unittest
from paths import is_within

class PathTests(unittest.TestCase):
    def test_child(self):
        self.assertTrue(is_within('/work/demo', '/work/demo/a.txt'))
    def test_same(self):
        self.assertTrue(is_within('/work/demo', '/work/demo'))
    def test_sibling(self):
        self.assertFalse(is_within('/work/demo', '/work/demo-backup/a.txt'))
    def test_parent_escape(self):
        self.assertFalse(is_within('/work/demo', '/work/demo/../secret.txt'))
'''

class OutcomeUnknown(RuntimeError):
    pass

class InjectedCrash(RuntimeError):
    pass

class Stopped(RuntimeError):
    pass

class Blocked(RuntimeError):
    pass

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.events = []
        if self.path.exists():
            # Deliberately refuse damaged tails: silent truncation could hide a dispatch.
            for line in self.path.read_text().splitlines():
                event = json.loads(line)
                if event['seq'] != len(self.events) + 1:
                    raise ValueError('Journal sequence is invalid')
                self.events.append(event)

    def append(self, kind, **fields):
        event = dict(seq=len(self.events) + 1, kind=kind, **fields)
        with self.path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + '\n')
            handle.flush()
            os.fsync(handle.fileno())
        self.events.append(event)
        return event

    def find(self, call, kind):
        return next((e for e in reversed(self.events) if e.get('call') == call and e['kind'] == kind), None)

def initialize(workspace):
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=False)
    (workspace / 'paths.py').write_text(OLD)
    (workspace / 'test_paths.py').write_text(TEST)
    return workspace

class Runner:
    def __init__(self, workspace, deny_edit=False, crash=None, stop_before=None, reconcile=False):
        self.workspace = Path(workspace).resolve()
        self.journal = Journal(self.workspace / 'events.jsonl')
        self.deny_edit = deny_edit
        self.crash = crash
        self.stop_before = stop_before
        self.reconcile = reconcile

    def prepare(self, call, safe):
        result = self.journal.find(call, 'tool/result')
        if result:
            if not result['ok']:
                raise Blocked(result['output'])
            return result
        dispatched = self.journal.find(call, 'tool/dispatched')
        if dispatched and not safe:
            if self.reconcile and call == 'edit' and (self.workspace / 'paths.py').read_text() == NEW:
                return self.journal.append('tool/result', call=call, ok=True,
                    output='Reconciled: target content equals the intended postcondition', reconciled=True)
            raise OutcomeUnknown(f'{call}: dispatched without committed result; inspect external state')
        if not self.journal.find(call, 'tool/intent'):
            self.journal.append('tool/intent', call=call, replay_safe=safe)
        if self.stop_before == call:
            self.journal.append('run/stopped', call=call)
            raise Stopped(f'Stopped before dispatch: {call}')
        if call == 'edit' and self.deny_edit:
            self.journal.append('tool/result', call=call, ok=False, output='Policy denied file edit')
            raise Blocked('Policy denied file edit')
        self.journal.append('tool/dispatched', call=call)
        return None

    def reads(self):
        calls = [('read-implementation', 'paths.py'), ('read-tests', 'test_paths.py')]
        pending = []
        for call, path in calls:
            if self.prepare(call, safe=True) is None:
                pending.append((call, path))
        # Dispatch bodies overlap. Journal results remain in model-plan order.
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [(call, pool.submit((self.workspace / path).read_text)) for call, path in pending]
            for call, future in futures:
                body = future.result()
                self.journal.append('tool/result', call=call, ok=True, output=body, sha256=digest(body))

    def edit(self):
        if self.prepare('edit', safe=False) is not None:
            return
        path = self.workspace / 'paths.py'
        # This lab coordinates one writer only. It is not a filesystem sandbox or transaction.
        if path.read_text() != OLD:
            self.journal.append('tool/result', call='edit', ok=False, output='Edit precondition changed')
            raise Blocked('Edit precondition changed')
        with tempfile.NamedTemporaryFile(mode='w', dir=self.workspace, delete=False, encoding='utf-8') as handle:
            temporary = Path(handle.name)
            handle.write(NEW)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        if self.crash == 'after-edit':
            raise InjectedCrash('Simulated process loss after effect, before result commit')
        self.journal.append('tool/result', call='edit', ok=True, output='Applied exact replacement', sha256=digest(NEW))

    def test(self):
        # This particular fixture test is side-effect-free and can be replayed.
        if self.prepare('test', safe=True) is not None:
            return
        result = subprocess.run([sys.executable, '-B', '-m', 'unittest', '-v', 'test_paths'],
            cwd=self.workspace, capture_output=True, text=True, timeout=30)
        self.journal.append('tool/result', call='test', ok=result.returncode == 0,
            output=result.stdout + result.stderr, exit_code=result.returncode)
        if result.returncode:
            raise Blocked('Fixture tests failed')

    def run(self):
        self.reads()
        self.edit()
        self.test()
        if not any(e['kind'] == 'run/completed' for e in self.journal.events):
            self.journal.append('run/completed', output='Four lexical path tests passed')
        return self.journal.events

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'run'])
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--deny-edit', action='store_true')
    parser.add_argument('--crash', choices=['after-edit'])
    parser.add_argument('--stop-before', choices=['edit', 'test'])
    parser.add_argument('--reconcile', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            initialize(args.workspace)
            print('Created intentionally buggy, disposable fixture:', args.workspace)
        else:
            events = Runner(args.workspace, args.deny_edit, args.crash, args.stop_before, args.reconcile).run()
            print('Completed; journal events:', len(events))
    except (OutcomeUnknown, InjectedCrash, Stopped, Blocked, ValueError) as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
