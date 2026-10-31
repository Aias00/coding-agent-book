import asyncio
import json
import tempfile
import time
import unittest
from pathlib import Path
from .core import (BROKEN, FIXED, Call, Conflict, FixtureModel, Grant, InjectedCrash,
                   Kernel, LeaseBusy, Outcome, OutcomeUnknown, Policy, Response,
                   Store, Tool, Workspace, fingerprint, sha)


class SequenceModel:
    def __init__(self, *responses): self.responses = iter(responses)
    async def generate(self, request): return next(self.responses)


class KernelTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'paths.py').write_text(BROKEN)
        (self.root / 'task.txt').write_text('repair fixture')
        self.workspace = Workspace(self.root)
        self.store = Store(self.root / '.agent/state.sqlite')
        self.addCleanup(lambda: self.store.close())

    def kernel(self, model=None, **kwargs):
        return Kernel(self.store, self.workspace, model or FixtureModel(), Policy(True), **kwargs)

    async def test_full_model_driven_repair(self):
        self.assertEqual(await self.kernel().run(), 'completed')
        self.assertEqual((self.root / 'paths.py').read_text(), FIXED)
        self.assertEqual(sum(e['kind'] == 'request/prepared' for e in self.store.events()), 4)

    async def test_completed_resume_does_not_repeat_tools_or_model(self):
        await self.kernel().run()
        events = self.store.events()
        self.assertEqual(await self.kernel(SequenceModel()).run(), 'completed')
        self.assertEqual(self.store.events(), events)

    async def test_policy_denial_is_partial_and_does_not_write(self):
        kernel = Kernel(self.store, self.workspace, FixtureModel(), Policy(False))
        self.assertEqual(await kernel.run(), 'partial')
        self.assertEqual((self.root / 'paths.py').read_text(), BROKEN)
        self.assertFalse(any(e['kind'] == 'tool/dispatched' and e['payload']['call_id'] == 'edit-1' for e in self.store.events()))

    async def test_truncated_tool_arguments_never_dispatch(self):
        model = SequenceModel(Response(calls=(Call.make('cut', 'edit', {}),), finish_reason='length'), Response('stop'))
        self.assertEqual(await self.kernel(model).run(), 'partial')
        self.assertFalse(any(e['kind'] == 'tool/dispatched' for e in self.store.events()))

    async def test_crash_after_effect_blocks_unsafe_replay_after_reopen(self):
        def crash(call, result):
            if call.name == 'edit': raise InjectedCrash()
        with self.assertRaises(InjectedCrash): await self.kernel(after_effect=crash).run()
        self.assertEqual((self.root / 'paths.py').read_text(), FIXED)
        self.store.close()
        self.store = Store(self.root / '.agent/state.sqlite')
        with self.assertRaises(OutcomeUnknown): await self.kernel().run()
        self.assertEqual(sum(e['kind'] == 'tool/dispatched' and e['payload']['call_id'] == 'edit-1' for e in self.store.events()), 1)

    async def test_file_version_conflict_does_not_overwrite(self):
        call = Call.make('edit', 'edit', dict(path='paths.py', expected_sha256=sha('old'), old=BROKEN, new=FIXED))
        kernel = self.kernel()
        self.store.accept(Response(calls=(call,)), kernel.tools, self.root)
        await kernel.batch((call,))
        self.assertEqual((self.root / 'paths.py').read_text(), BROKEN)
        self.assertIn('File changed', json.loads(self.store.call('edit')['outcome'])['content'])

    async def test_duplicate_call_response_rolls_back_as_one_transaction(self):
        call = Call.make('same', 'read', {'path': 'paths.py'})
        with self.assertRaises(Conflict): self.store.accept(Response(calls=(call, call)), self.kernel().tools, self.root)
        self.assertEqual(self.store.events(), [])
        self.assertIsNone(self.store.call('same'))

    async def test_call_id_cannot_change_parameters(self):
        kernel = self.kernel()
        self.store.accept(Response(calls=(Call.make('a', 'read', {'path': 'paths.py'}),)), kernel.tools, self.root)
        before = self.store.events()
        with self.assertRaises(Conflict):
            self.store.accept(Response(calls=(Call.make('a', 'read', {'path': 'task.txt'}),)), kernel.tools, self.root)
        self.assertEqual(self.store.events(), before)

    async def test_authorization_is_bound_to_actual_parameters(self):
        policy = Policy(True)
        tool = self.kernel().tools['read']
        call = Call.make('a', 'read', {'path': 'paths.py'})
        grant = policy.authorize(call, tool, self.root)
        with self.assertRaises(PermissionError): policy.verify(grant, Call.make('a', 'read', {'path': 'task.txt'}), tool, self.root)

    async def test_expired_authorization_rejected(self):
        tool = self.kernel().tools['read']
        call = Call.make('a', 'read', {'path': 'paths.py'})
        with self.assertRaises(PermissionError): Policy(True).verify(Grant(fingerprint(call, tool, self.root), '1', time.time()-1), call, tool, self.root)

    async def test_workspace_rejects_escape_symlink_and_control_store(self):
        (self.root / 'alias').symlink_to(self.root / 'paths.py')
        for path in ['../outside', '/etc/passwd', 'alias', '.agent/state.sqlite']:
            with self.assertRaises(PermissionError): self.workspace.path(path)

    async def test_single_actor_lease(self):
        with self.assertRaises(LeaseBusy): Store(self.root / '.agent/state.sqlite')

    async def test_unknown_tool_becomes_error_result(self):
        kernel = self.kernel()
        call = Call.make('missing', 'missing', {})
        self.store.accept(Response(calls=(call,)), kernel.tools, self.root)
        await kernel.batch((call,))
        self.assertEqual(json.loads(self.store.call('missing')['outcome'])['status'], 'error')

    async def test_parallelism_is_bounded_and_results_ordered(self):
        active = 0
        maximum = 0
        completions = []
        started = asyncio.Event()
        async def read(call, args):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            if call.id == '0': await started.wait()
            if call.id == '1': started.set()
            await asyncio.sleep(0)
            completions.append(call.id)
            active -= 1
            return Outcome(call.id, 'ok', call.id)
        kernel = self.kernel(max_parallel=2)
        kernel.tools = {'read': Tool('read', (), True, True, read)}
        calls = tuple(Call.make(str(i), 'read', {}) for i in range(4))
        self.store.accept(Response(calls=calls), kernel.tools, self.root)
        await kernel.batch(calls)
        self.assertEqual(maximum, 2)
        self.assertEqual([e['payload']['call_id'] for e in self.store.events() if e['kind'] == 'tool/result'], ['0','1','2','3'])

    async def test_exclusive_tool_forms_a_barrier(self):
        trace = []
        async def body(call, args):
            trace.append('start-'+call.id)
            await asyncio.sleep(0)
            trace.append('end-'+call.id)
            return Outcome(call.id,'ok','done')
        kernel = self.kernel()
        kernel.tools = {'read': Tool('read', (), True, True, body), 'exclusive': Tool('exclusive', (), False, True, body)}
        calls = (Call.make('a','read',{}),Call.make('b','exclusive',{}),Call.make('c','read',{}))
        self.store.accept(Response(calls=calls),kernel.tools,self.root)
        await kernel.batch(calls)
        self.assertLess(trace.index('end-a'),trace.index('start-b'))
        self.assertLess(trace.index('end-b'),trace.index('start-c'))

    async def test_budget_is_not_reset_by_reopen(self):
        model = SequenceModel(Response('unfinished',finish_reason='length'))
        self.assertEqual(await self.kernel(model,max_steps=1).run(),'budget_exhausted')
        self.assertEqual(await self.kernel(SequenceModel(),max_steps=1).run(),'budget_exhausted')

    async def test_cancel_before_dispatch_has_no_write(self):
        kernel = self.kernel()
        kernel.cancelled.set()
        self.assertEqual(await kernel.run(),'cancelled')
        self.assertEqual((self.root/'paths.py').read_text(),BROKEN)

    async def test_read_result_cannot_spoof_verification_identity(self):
        model = SequenceModel(Response(calls=(Call.make('verify-1','read',{'path':'paths.py'}),)), Response('done'))
        self.assertEqual(await self.kernel(model).run(),'partial')


if __name__ == '__main__': unittest.main()
