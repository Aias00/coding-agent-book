"""Model-driven loop, immutable calls, durable outcomes, and conservative replay.

The executor is a trusted single-process demonstration. Path checks and process
allowlists are application policy; they are not an operating-system sandbox.
"""
import asyncio
import hashlib
import json
import os
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, Tuple


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def sha(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class OutcomeUnknown(RuntimeError):
    pass


class Conflict(RuntimeError):
    pass


class LeaseBusy(RuntimeError):
    pass


class InjectedCrash(BaseException):
    """Bypasses ordinary tool-error conversion to model process loss."""


@dataclass(frozen=True)
class Call:
    id: str
    name: str
    arguments_json: str

    @classmethod
    def make(cls, identity: str, name: str, arguments: dict):
        return cls(identity, name, canonical(arguments))

    @property
    def arguments(self):
        return json.loads(self.arguments_json)


@dataclass(frozen=True)
class Outcome:
    call_id: str
    status: str
    content: str
    effect: str = 'none'


@dataclass(frozen=True)
class Response:
    text: str = ''
    calls: Tuple[Call, ...] = ()
    finish_reason: str = 'stop'


@dataclass(frozen=True)
class Request:
    messages_json: str
    tools_json: str
    revision: str


class Model(Protocol):
    async def generate(self, request: Request) -> Response:
        ...


@dataclass(frozen=True)
class Tool:
    name: str
    parameters: Tuple[Tuple[str, type], ...]
    parallel: bool
    replay_safe: bool
    handler: Callable
    revision: str = '1'

    def validate(self, call: Call):
        args = call.arguments
        if not isinstance(args, dict) or set(args) != {k for k, _ in self.parameters}:
            raise ValueError('Arguments must exactly match the declared fields')
        for key, expected in self.parameters:
            if type(args[key]) is not expected:
                raise ValueError('Invalid argument type for ' + key)
        return args


@dataclass(frozen=True)
class Grant:
    fingerprint: str
    policy_revision: str
    expires_at: float


@dataclass(frozen=True)
class Policy:
    allow_edit: bool = False
    revision: str = '1'

    def authorize(self, call: Call, tool: Tool, workspace: Path) -> Grant:
        if tool.name == 'edit' and not self.allow_edit:
            raise PermissionError('Editing is not authorized')
        return Grant(fingerprint(call, tool, workspace), self.revision, time.time() + 60)

    def verify(self, grant: Grant, call: Call, tool: Tool, workspace: Path):
        if grant.policy_revision != self.revision or time.time() >= grant.expires_at:
            raise PermissionError('Authorization expired or policy changed')
        if grant.fingerprint != fingerprint(call, tool, workspace):
            raise PermissionError('Authorization does not match the actual action')


def fingerprint(call: Call, tool: Tool, workspace: Path) -> str:
    return sha(canonical([call.name, call.arguments_json, tool.revision, str(workspace.resolve())]))


class Store:
    def __init__(self, database: Path):
        import fcntl
        database = Path(database)
        database.parent.mkdir(parents=True, exist_ok=True)
        self.lock = open(str(database) + '.lock', 'a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise LeaseBusy('Another actor owns this database')
        self.db = sqlite3.connect(database, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS calls(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, state TEXT NOT NULL, outcome TEXT);
        ''')

    def close(self):
        self.db.close()
        self.lock.close()

    def transaction(self, action):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            value = action()
            self.db.execute('COMMIT')
            return value
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def _append(self, kind, payload):
        self.db.execute('INSERT INTO events(kind,payload) VALUES (?,?)', (kind, canonical(payload)))

    def append(self, kind, payload):
        self.transaction(lambda: self._append(kind, payload))

    def events(self):
        return [dict(seq=r['seq'], kind=r['kind'], payload=json.loads(r['payload'])) for r in self.db.execute('SELECT * FROM events ORDER BY seq')]

    def call(self, identity):
        return self.db.execute('SELECT * FROM calls WHERE id=?', (identity,)).fetchone()

    def accept(self, response: Response, tools, workspace):
        identities = [c.id for c in response.calls]
        if len(set(identities)) != len(identities):
            raise Conflict('Duplicate call id within one assistant response')
        def commit():
            for call in response.calls:
                if not call.id or len(call.id) > 200:
                    raise ValueError('Invalid call identity')
                tool = tools.get(call.name)
                identity = fingerprint(call, tool, workspace) if tool else sha(call.name + call.arguments_json)
                old = self.call(call.id)
                if old and old['fingerprint'] != identity:
                    raise Conflict('Call id reused with different parameters or tool revision')
                if old:
                    raise Conflict('Model response reused an already accepted call id')
                self.db.execute('INSERT INTO calls(id,fingerprint,state) VALUES (?,?,?)', (call.id, identity, 'intended'))
            self._append('assistant/settled', dict(text=response.text, calls=[dict(id=c.id, name=c.name, arguments_json=c.arguments_json) for c in response.calls]))
        self.transaction(commit)

    def dispatched(self, call: Call, identity):
        def commit():
            row = self.call(call.id)
            if row['state'] == 'settled':
                raise Conflict('Cannot dispatch an already settled call')
            if row['fingerprint'] != identity:
                raise Conflict('Tool changed after the call was accepted')
            self.db.execute('UPDATE calls SET state=? WHERE id=?', ('dispatched', call.id))
            self._append('tool/dispatched', dict(call_id=call.id, fingerprint=identity))
        self.transaction(commit)

    def settle(self, outcome: Outcome):
        payload = vars(outcome)
        def commit():
            row = self.call(outcome.call_id)
            if row['state'] == 'settled':
                if row['outcome'] != canonical(payload): raise Conflict('Conflicting result')
                return
            self.db.execute('UPDATE calls SET state=?,outcome=? WHERE id=?', ('settled', canonical(payload), outcome.call_id))
            self._append('tool/result', payload)
        self.transaction(commit)

    def history(self):
        return [e for e in self.events() if e['kind'] in ('input/received', 'assistant/settled', 'tool/result')]

    def pending_response(self):
        for e in reversed(self.events()):
            if e['kind'] == 'assistant/settled':
                calls = tuple(Call(**c) for c in e['payload']['calls'])
                if any(self.call(c.id)['state'] != 'settled' for c in calls):
                    return calls
                return ()
        return ()


class Workspace:
    def __init__(self, root: Path):
        self.root = Path(root).resolve(strict=True)

    def path(self, relative: str):
        value = Path(relative)
        if value.is_absolute() or '..' in value.parts or not value.parts or value.parts[0] == '.agent':
            raise PermissionError('Path is outside the allowed workspace')
        target = self.root
        for part in value.parts:
            target = target / part
            if target.is_symlink(): raise PermissionError('Symlinks are not allowed in this reference executor')
        target = target.resolve(strict=True)
        if self.root not in target.parents: raise PermissionError('Path is outside workspace')
        if not target.is_file(): raise ValueError('Expected a regular file')
        return target

    async def read(self, call, args):
        def load():
            path = self.path(args['path'])
            with path.open('rb') as handle:
                return handle.read(65537)
        raw = await asyncio.to_thread(load)
        if len(raw) > 65536: raise ValueError('Read exceeds 64 KiB')
        text = raw.decode('utf-8')
        return Outcome(call.id, 'ok', canonical(dict(path=args['path'], text=text, sha256=sha(text))))

    async def edit(self, call, args):
        path = self.path(args['path'])
        with path.open('rb') as handle:
            raw = handle.read(65537)
        if len(raw) > 65536: raise Conflict('File now exceeds the edit size limit')
        text = raw.decode('utf-8')
        if sha(text) != args['expected_sha256']: raise Conflict('File changed since it was read')
        if not args['old'] or text.count(args['old']) != 1: raise Conflict('Old text must match exactly once')
        updated = text.replace(args['old'], args['new'], 1)
        if len(updated.encode('utf-8')) > 65536: raise ValueError('Edit exceeds 64 KiB')
        mode = path.stat().st_mode
        temporary = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(updated)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        finally:
            if temporary and temporary.exists(): temporary.unlink()
        return Outcome(call.id, 'ok', canonical(dict(path=args['path'], sha256=sha(updated))), 'applied')

    async def verify_paths(self, call, args):
        # Fixed fixture verifier; no arbitrary code execution or shell exposure.
        text = self.path('paths.py').read_text()
        import ast
        ast.parse(text)
        if text != FIXED:
            return Outcome(call.id, 'error', 'Implementation differs from the approved fixture repair')
        scope = {}
        exec(compile(FIXED, '<fixed-verifier-fixture>', 'exec'), scope)
        cases = [('/work/demo/a', True), ('/work/demo', True), ('/work/demo-backup/a', False), ('/work/demo/../secret', False)]
        passed = all(scope['is_within']('/work/demo', candidate) is expected for candidate, expected in cases)
        return Outcome(call.id, 'ok' if passed else 'error', canonical(dict(passed=passed, cases=len(cases), implementation_sha256=sha(text))))

    def tools(self):
        return {
            'read': Tool('read', (('path', str),), True, True, self.read),
            'edit': Tool('edit', (('path', str), ('expected_sha256', str), ('old', str), ('new', str)), False, False, self.edit),
            'verify_paths': Tool('verify_paths', (), False, True, self.verify_paths),
        }


class Kernel:
    def __init__(self, store: Store, workspace: Workspace, model: Model, policy: Policy,
                 max_steps=8, max_parallel=2, after_effect=None):
        if max_steps < 1 or max_parallel < 1: raise ValueError('Budgets must be positive')
        self.store, self.workspace, self.model, self.policy = store, workspace, model, policy
        self.tools = workspace.tools()
        self.max_steps, self.max_parallel = max_steps, max_parallel
        self.after_effect = after_effect
        self.cancelled = asyncio.Event()

    async def execute(self, call):
        row = self.store.call(call.id)
        if row['state'] == 'settled': return Outcome(**json.loads(row['outcome']))
        tool = self.tools.get(call.name)
        if row['state'] == 'dispatched' and tool and not tool.replay_safe:
            raise OutcomeUnknown(call.id + ': dispatched without a committed result')
        if self.cancelled.is_set(): return Outcome(call.id, 'cancelled', 'Cancelled before dispatch')
        try:
            if tool is None: raise ValueError('Unknown tool')
            args = tool.validate(call)
            grant = self.policy.authorize(call, tool, self.workspace.root)
            self.policy.verify(grant, call, tool, self.workspace.root)
            self.store.dispatched(call, fingerprint(call, tool, self.workspace.root))
            result = await tool.handler(call, args)
            if self.after_effect: self.after_effect(call, result)
            return result
        except asyncio.CancelledError:
            # An interrupted dispatched tool may have effects: preserve the open dispatch.
            raise
        except Exception as error:
            row = self.store.call(call.id)
            if tool and not tool.replay_safe and row['state'] == 'dispatched' and not isinstance(error, Conflict):
                self.store.append('tool/unknown', dict(call_id=call.id, reason=type(error).__name__))
                raise OutcomeUnknown(call.id + ': interrupted side effect needs reconciliation') from error
            return Outcome(call.id, 'error', type(error).__name__ + ': ' + str(error))

    async def batch(self, calls):
        position = 0
        while position < len(calls):
            call = calls[position]
            tool = self.tools.get(call.name)
            if tool and tool.parallel:
                end = position
                while end < len(calls) and self.tools.get(calls[end].name) and self.tools[calls[end].name].parallel:
                    end += 1
                pool = asyncio.Semaphore(self.max_parallel)
                async def bounded(item):
                    async with pool: return await self.execute(item)
                outcomes = await asyncio.gather(*(bounded(c) for c in calls[position:end]))
            else:
                end = position + 1
                outcomes = [await self.execute(call)]
            # Completion order never changes the durable transcript order.
            for outcome in outcomes: self.store.settle(outcome)
            position = end

    async def run(self, prompt='Repair the lexical path containment fixture and verify it'):
        events = self.store.events()
        if any(e['kind'] == 'turn/completed' for e in events): return 'completed'
        if not events: self.store.append('input/received', dict(text=prompt))
        pending = self.store.pending_response()
        if pending: await self.batch(pending)
        used_steps = sum(e['kind'] == 'request/prepared' for e in self.store.events())
        for _ in range(max(0, self.max_steps - used_steps)):
            if self.cancelled.is_set():
                self.store.append('turn/cancelled', {})
                return 'cancelled'
            schemas = canonical([dict(name=t.name, fields=[(k, v.__name__) for k, v in t.parameters], revision=t.revision) for t in self.tools.values()])
            history = canonical(self.store.history())
            request = Request(history, schemas, sha(history + schemas))
            self.store.append('request/prepared', dict(revision=request.revision))
            response = await self.model.generate(request)
            if response.finish_reason not in ('stop', 'tool_calls'):
                self.store.append('attempt/incomplete', dict(reason=response.finish_reason))
                continue
            self.store.accept(response, self.tools, self.workspace.root)
            if response.calls:
                await self.batch(response.calls)
                continue
            results = [e['payload'] for e in self.store.events() if e['kind'] == 'tool/result']
            accepted = {c['id']: c['name'] for e in self.store.events() if e['kind'] == 'assistant/settled' for c in e['payload']['calls']}
            current_hash = sha(self.workspace.path('paths.py').read_text())
            verified = any(accepted.get(r['call_id']) == 'verify_paths' and r['status'] == 'ok'
                           and json.loads(r['content']).get('implementation_sha256') == current_hash for r in results)
            status = 'completed' if verified else 'partial'
            self.store.append('turn/' + status, dict(text=response.text))
            return status
        self.store.append('turn/budget_exhausted', dict(max_steps=self.max_steps))
        return 'budget_exhausted'


BROKEN = '''import os
def is_within(base, candidate):
    return os.path.abspath(candidate).startswith(os.path.abspath(base))
'''
FIXED = '''import os
def is_within(base, candidate):
    base = os.path.abspath(base)
    candidate = os.path.abspath(candidate)
    try:
        return os.path.commonpath([base, candidate]) == base
    except ValueError:
        return False
'''


class FixtureModel:
    """A deterministic model substitute, driven by committed history, not a fixed loop."""
    async def generate(self, request):
        history = json.loads(request.messages_json)
        results = {e['payload']['call_id']: e['payload'] for e in history if e['kind'] == 'tool/result'}
        if 'read-1' not in results:
            return Response(calls=(Call.make('read-1', 'read', {'path': 'paths.py'}), Call.make('read-2', 'read', {'path': 'task.txt'})))
        if 'edit-1' not in results:
            original = json.loads(results['read-1']['content'])
            return Response(calls=(Call.make('edit-1', 'edit', dict(path='paths.py', expected_sha256=original['sha256'], old=BROKEN, new=FIXED)),))
        if results['edit-1']['status'] != 'ok': return Response('Editing was blocked; no successful repair is claimed')
        if 'verify-1' not in results: return Response(calls=(Call.make('verify-1', 'verify_paths', {}),))
        return Response('Fixture repair and four lexical path cases checked')
