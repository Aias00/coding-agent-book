import json
import tempfile
import unittest
from pathlib import Path

from harness_lab import Blocked, InjectedCrash, NEW, OLD, OutcomeUnknown, Runner, Stopped, initialize

class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = initialize(Path(self.temp.name) / 'fixture')

    def test_repair_and_validation(self):
        events = Runner(self.workspace).run()
        self.assertEqual((self.workspace / 'paths.py').read_text(), NEW)
        result = next(e for e in events if e.get('call') == 'test' and e['kind'] == 'tool/result')
        self.assertEqual(result['exit_code'], 0)
        self.assertIn('Ran 4 tests', result['output'])

    def test_resume_reuses_committed_results(self):
        first = Runner(self.workspace).run()
        second = Runner(self.workspace).run()
        self.assertEqual(first, second)

    def test_policy_denial_has_no_write_effect(self):
        runner = Runner(self.workspace, deny_edit=True)
        with self.assertRaises(Blocked):
            runner.run()
        self.assertEqual((self.workspace / 'paths.py').read_text(), OLD)
        self.assertFalse(any(e.get('call') == 'edit' and e['kind'] == 'tool/dispatched' for e in runner.journal.events))

    def test_stop_before_dispatch_can_resume(self):
        with self.assertRaises(Stopped):
            Runner(self.workspace, stop_before='edit').run()
        self.assertEqual((self.workspace / 'paths.py').read_text(), OLD)
        Runner(self.workspace).run()
        self.assertEqual((self.workspace / 'paths.py').read_text(), NEW)

    def test_crash_after_effect_does_not_blindly_replay(self):
        with self.assertRaises(InjectedCrash):
            Runner(self.workspace, crash='after-edit').run()
        self.assertEqual((self.workspace / 'paths.py').read_text(), NEW)
        with self.assertRaises(OutcomeUnknown):
            Runner(self.workspace).run()

    def test_explicit_reconciliation_checks_postcondition(self):
        with self.assertRaises(InjectedCrash):
            Runner(self.workspace, crash='after-edit').run()
        events = Runner(self.workspace, reconcile=True).run()
        self.assertTrue(any(e.get('reconciled') for e in events))
        self.assertEqual(sum(e['kind'] == 'tool/dispatched' and e.get('call') == 'edit' for e in events), 1)

    def test_changed_precondition_blocks_write(self):
        (self.workspace / 'paths.py').write_text('# changed by a different writer\n')
        with self.assertRaises(Blocked):
            Runner(self.workspace).run()
        self.assertEqual((self.workspace / 'paths.py').read_text(), '# changed by a different writer\n')

    def test_read_results_commit_in_plan_order(self):
        runner = Runner(self.workspace)
        runner.reads()
        results = [e['call'] for e in runner.journal.events if e['kind'] == 'tool/result']
        self.assertEqual(results, ['read-implementation', 'read-tests'])

    def test_corrupt_journal_is_not_silently_ignored(self):
        (self.workspace / 'events.jsonl').write_text('{"seq":1')
        with self.assertRaises(json.JSONDecodeError):
            Runner(self.workspace)

    def test_reconciliation_rejects_unexpected_content(self):
        with self.assertRaises(InjectedCrash):
            Runner(self.workspace, crash='after-edit').run()
        (self.workspace / 'paths.py').write_text('# unexpected\n')
        with self.assertRaises(OutcomeUnknown):
            Runner(self.workspace, reconcile=True).run()

if __name__ == '__main__':
    unittest.main()
