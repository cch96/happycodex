from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from scripts import review_runner


ROOT = Path(__file__).resolve().parents[1]


class ReviewRunnerTests(unittest.TestCase):
    def make_temp(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name)

    def git(self, repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True, text=True
        )
        return completed.stdout.strip()

    def make_repo(self, root: Path) -> tuple[Path, str, str]:
        repo = root / "repo"
        repo.mkdir()
        self.git(repo, "init", "-q", "-b", "main")
        self.git(repo, "config", "user.name", "Review Test")
        self.git(repo, "config", "user.email", "review@example.invalid")
        (repo / "feature.txt").write_text("base\n", encoding="utf-8")
        self.git(repo, "add", "feature.txt")
        self.git(repo, "commit", "-q", "-m", "base")
        base = self.git(repo, "rev-parse", "HEAD")
        (repo / "feature.txt").write_text("base\nhead\n", encoding="utf-8")
        self.git(repo, "add", "feature.txt")
        self.git(repo, "commit", "-q", "-m", "head")
        head = self.git(repo, "rev-parse", "HEAD")
        return repo, base, head

    def make_source_home(self, root: Path) -> Path:
        source = root / "source-codex"
        source.mkdir()
        (source / "auth.json").write_text(
            '{"auth":"AUTH_FIXTURE_SECRET_12345"}\n', encoding="utf-8"
        )
        (source / "models_cache.json").write_text('{"models":[]}\n', encoding="utf-8")
        return source

    def make_packet(self, root: Path, base: str, head: str) -> Path:
        packet = root / "packet.md"
        packet.write_text(
            "# Review packet\n\n"
            "- Objective: review the feature change.\n"
            f"- Base commit: `{base}`\n"
            f"- Head commit: `{head}`\n"
            "- Acceptance: feature.txt gains one line without changing the first.\n"
            "- Verification receipt: focused test exit 0.\n",
            encoding="utf-8",
        )
        return packet

    def make_fake_codex(self, root: Path) -> Path:
        fake = root / "fake-codex"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, re, shlex, subprocess, sys, time\n"
            "if '--version' in sys.argv:\n"
            " print('codex-cli 0.144.1-fixture')\n"
            " raise SystemExit(0)\n"
            "if len(sys.argv) > 1 and sys.argv[1] == 'sandbox':\n"
            " raise SystemExit(19 if os.environ.get('NCL_FAKE_PREFLIGHT_FAIL') else 0)\n"
            "if os.environ.get('NCL_FAKE_SLEEP'):\n"
            " time.sleep(float(os.environ['NCL_FAKE_SLEEP']))\n"
            "if os.environ.get('NCL_FAKE_WRITE'):\n"
            " pathlib.Path('ignored-review-write.tmp').write_text('write\\n', encoding='utf-8')\n"
            "if os.environ.get('NCL_FORBIDDEN_OBJECT'):\n"
            " seen = subprocess.run(['git','cat-file','-e',os.environ['NCL_FORBIDDEN_OBJECT']], capture_output=True).returncode == 0\n"
            " if seen: raise SystemExit(23)\n"
            "home = pathlib.Path(os.environ['CODEX_HOME'])\n"
            "session_dir = home / 'sessions/2026/07/12'\n"
            "session_dir.mkdir(parents=True, exist_ok=True)\n"
            "config = (home / 'config.toml').read_text(encoding='utf-8')\n"
            "prompt = json.loads(config.splitlines()[0].split('=', 1)[1].strip())\n"
            "cwd = str(pathlib.Path.cwd())\n"
            "context_cwd = '/wrong' if os.environ.get('NCL_FAKE_WRONG_CWD') else cwd\n"
            "canary_command = re.search(r'run exactly `([^`]+)`', prompt).group(1)\n"
            "base = sys.argv[sys.argv.index('--base') + 1]\n"
            "head = subprocess.run(['git','rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()\n"
            "effort = os.environ.get('NCL_FAKE_EFFORT', 'max')\n"
            "outer = [\n"
            " {'type':'session_meta','payload':{'session_id':'outer','id':'outer','cwd':cwd,'thread_source':'user','source':'exec'}},\n"
            "]\n"
            "reviewer = [\n"
            " {'type':'session_meta','payload':{'session_id':'outer','id':'outer' if os.environ.get('NCL_FAKE_SAME_SESSION') else 'review','parent_thread_id':'outer','cwd':cwd,'thread_source':'subagent','source':{'subagent':'review'}}},\n"
            " {'type':'response_item','payload':{'type':'message','role':'developer','content':[{'type':'input_text','text':prompt}]}},\n"
            " {'type':'turn_context','payload':{'cwd':context_cwd,'workspace_roots':[context_cwd],'model':'gpt-5.6-sol','effort':effort,'approval_policy':'never','sandbox_policy':{'type':'read-only'},'permission_profile':{'type':'managed','file_system':{'type':'restricted','entries':[{'path':{'type':'special','value':{'kind':'minimal'}},'access':'read'},{'path':{'type':'path','path':cwd},'access':'read'}] + ([{'path':{'type':'path','path':'/'},'access':'read'}] if os.environ.get('NCL_FAKE_BROAD_PROFILE') else [])},'network':'restricted'},'multi_agent_version':'disabled'}},\n"
            "]\n"
            "if os.environ.get('NCL_FAKE_FORBIDDEN'):\n"
            " reviewer.append({'type':'response_item','payload':{'type':'custom_tool_call','name':'exec','input':'await tools.web__run({})'}})\n"
            "(session_dir / 'outer.jsonl').write_text(''.join(json.dumps(x)+'\\n' for x in outer), encoding='utf-8')\n"
            "(session_dir / 'review.jsonl').write_text(''.join(json.dumps(x)+'\\n' for x in reviewer), encoding='utf-8')\n"
            "result = {'findings':[],'overall_correctness':'patch is correct','overall_explanation':'No actionable findings.','review_root':str(pathlib.Path.cwd())}\n"
            "if os.environ.get('NCL_FAKE_LEAK_AUTH'):\n"
            " result['leak'] = (home / 'auth.json').read_text(encoding='utf-8')\n"
            "print(json.dumps({'type':'thread.started','thread_id':os.environ.get('NCL_FAKE_THREAD_ID','outer')}))\n"
            "canary_event = '/bin/bash -c ' + shlex.quote(canary_command + (' || true' if os.environ.get('NCL_FAKE_DECEPTIVE_CANARY') else ''))\n"
            "proof_event = f'git diff --check {base}..{head}' if os.environ.get('NCL_FAKE_DIFF_CHECK_ONLY') else f'git diff {base}..{head}'\n"
            "print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':canary_event,'aggregated_output':'','exit_code':0}}))\n"
            "print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':proof_event,'aggregated_output':'' if os.environ.get('NCL_FAKE_DIFF_CHECK_ONLY') else 'diff --git evidence','exit_code':0}}))\n"
            "print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':json.dumps(result)}}))\n"
            "if not os.environ.get('NCL_FAKE_NO_COMPLETED'):\n"
            " print(json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':5}}))\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        return fake

    def invoke(self, root: Path, repo: Path, base: str, head: str, **overrides):
        arguments = {
            "repo": repo,
            "base": base,
            "head": head,
            "packet": self.make_packet(root, base, head),
            "output": root / "output",
            "source_codex_home": self.make_source_home(root),
            "codex_binary": self.make_fake_codex(root),
        }
        arguments.update(overrides)
        return review_runner.run_review(**arguments)

    def test_run_review_is_fresh_max_read_only_and_writes_receipt(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        output = root / "review-output"

        receipt = self.invoke(root, repo, base, head, output=output)

        self.assertTrue(receipt["ok"], receipt)
        review = json.loads((output / "review.md").read_text(encoding="utf-8"))
        self.assertEqual(review["findings"], [])
        self.assertEqual(review["review_root"], str(repo))
        persisted = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["base"], base)
        self.assertEqual(persisted["head"], head)
        self.assertEqual(persisted["model"], "gpt-5.6-sol")
        self.assertEqual(persisted["effort"], "max")
        self.assertEqual(persisted["sandbox"], "read-only")
        self.assertEqual(persisted["approval"], "never")
        self.assertEqual(persisted["network"], "restricted")
        self.assertEqual(persisted["cli_version"], "codex-cli 0.144.1-fixture")
        for field in (
            "codex_binary_sha256",
            "events_sha256",
            "stderr_sha256",
            "raw_review_sha256",
            "review_sha256",
            "outer_rollout_sha256",
            "review_rollout_sha256",
            "profile_preflight_sha256",
        ):
            self.assertRegex(persisted[field], r"^[0-9a-f]{64}$")
        self.assertRegex(
            persisted["containment"]["binary_sha256"], r"^[0-9a-f]{64}$"
        )
        self.assertEqual(
            persisted["source_git_visible_sha256_before"],
            persisted["source_git_visible_sha256_after"],
        )
        self.assertEqual(
            persisted["review_tree_sha256_before"],
            persisted["review_tree_sha256_after"],
        )
        for field, filename in (
            ("events_sha256", "events.jsonl"),
            ("stderr_sha256", "stderr.log"),
            ("review_sha256", "review.md"),
            ("reviewed_packet_sha256", "packet.md"),
            ("profile_preflight_sha256", "preflight.log"),
        ):
            self.assertEqual(
                persisted[field],
                hashlib.sha256((output / filename).read_bytes()).hexdigest(),
            )
        self.assertFalse((output / "runtime").exists())
        self.assertFalse(any(path.name == "auth.json" for path in output.rglob("*")))
        command = persisted["command"]
        contained = persisted["contained_command"]
        self.assertEqual(contained[-len(command) :], command)
        self.assertEqual(
            contained[1:8],
            [
                "--user",
                "--map-root-user",
                "--pid",
                "--fork",
                "--mount-proc",
                "--kill-child=SIGKILL",
                "--",
            ],
        )
        self.assertIn("--base", command)
        self.assertIn(base, command)
        self.assertNotIn("-", command)
        rendered = " ".join(command)
        for phrase in (
            "exec review",
            "--json",
            "--strict-config",
            "-m gpt-5.6-sol",
            "project_doc_max_bytes=0",
            "tools.web_search=false",
        ):
            self.assertIn(phrase, rendered)
        for feature in (
            "plugins",
            "apps",
            "hooks",
            "multi_agent",
            "browser_use",
            "browser_use_external",
            "computer_use",
            "image_generation",
        ):
            self.assertIn(
                feature,
                [
                    command[index + 1]
                    for index, item in enumerate(command[:-1])
                    if item == "--disable"
                ],
            )

    def test_runtime_helper_aliases_do_not_escape_through_symlinks(self) -> None:
        root = self.make_temp()
        binary = root / "codex"
        binary.write_bytes(b"fixture-binary")
        binary.chmod(0o755)
        aliases = root / "aliases"

        review_runner._prepare_aliases(aliases, binary)

        for name in ("codex-linux-sandbox", "codex-execve-wrapper", "apply_patch"):
            helper = aliases / name
            self.assertTrue(helper.is_file())
            self.assertFalse(helper.is_symlink())
            self.assertEqual(helper.read_bytes(), binary.read_bytes())
            self.assertTrue(os.access(helper, os.X_OK))

    def test_outer_runtime_path_starts_with_verified_helper_aliases(self) -> None:
        root = self.make_temp()
        home = root / "home"
        codex_home = root / "codex"
        aliases = root / "aliases"

        environment = review_runner._codex_environment(
            home, codex_home, root, aliases
        )

        self.assertEqual(environment["PATH"].split(os.pathsep)[0], str(aliases))

    def test_pid_namespace_contains_detached_children_on_exit_and_timeout(self) -> None:
        unshare = review_runner._resolve_containment_binary()

        def marker_processes(marker: str) -> list[Path]:
            matches = []
            for path in Path("/proc").glob("[0-9]*/cmdline"):
                try:
                    if marker.encode() in path.read_bytes():
                        matches.append(path)
                except OSError:
                    continue
            return matches

        for timeout in (False, True):
            with self.subTest(timeout=timeout):
                marker = f"NCL_DAEMON_{os.getpid()}_{time.time_ns()}"
                code = (
                    "import subprocess,sys,time;"
                    "subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)',"
                    "sys.argv[1]],start_new_session=True,stdin=subprocess.DEVNULL,"
                    "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
                    + ("time.sleep(60)" if timeout else "")
                )
                command = review_runner._containment_command(
                    unshare, [sys.executable, "-c", code, marker]
                )
                sibling = subprocess.Popen(
                    [sys.executable, "-c", "import time;time.sleep(30)", marker + "_SIBLING"]
                )
                self.addCleanup(
                    lambda process=sibling: process.poll() is None and process.kill()
                )
                if timeout:
                    with self.assertRaises(subprocess.TimeoutExpired):
                        review_runner._run_process(
                            command,
                            cwd=self.make_temp(),
                            env=os.environ.copy(),
                            timeout=0.1,
                        )
                else:
                    completed = review_runner._run_process(
                        command,
                        cwd=self.make_temp(),
                        env=os.environ.copy(),
                        timeout=5,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIsNone(sibling.poll())
                sibling.terminate()
                sibling.wait(timeout=5)
                for _ in range(50):
                    if not marker_processes(marker):
                        break
                    time.sleep(0.02)
                self.assertEqual(marker_processes(marker), [])

    def test_run_review_rejects_dirty_source_repo(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head)

    def test_run_review_rejects_assume_unchanged_worktree_edits(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        (repo / "feature.txt").write_text("base\nhead\nhidden\n", encoding="utf-8")
        self.git(repo, "update-index", "--assume-unchanged", "feature.txt")
        self.assertEqual(self.git(repo, "status", "--porcelain"), "")

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head)

    def test_run_review_rejects_runtime_effort_mismatch(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        with mock.patch.dict(os.environ, {"NCL_FAKE_EFFORT": "high"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

    def test_run_review_rejects_non_ancestor_base(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        tree = self.git(repo, "rev-parse", f"{base}^{{tree}}")
        unrelated = self.git(repo, "commit-tree", tree, "-m", "unrelated")

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, unrelated, head)

    def test_run_review_rejects_empty_review_range(self) -> None:
        root = self.make_temp()
        repo, _, head = self.make_repo(root)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, head, head)

    def test_run_review_rejects_empty_or_stale_task_packet(self) -> None:
        for stale in (False, True):
            with self.subTest(stale=stale):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                packet = root / "invalid-packet.md"
                packet.write_text(
                    ""
                    if not stale
                    else f"Acceptance criteria: stale\nBase: {base}\nHead: {'0' * 40}\n",
                    encoding="utf-8",
                )
                with self.assertRaises(review_runner.ReviewRunnerError):
                    self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_detects_clone_write_even_if_tool_claims_read_only(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)

        with mock.patch.dict(os.environ, {"NCL_FAKE_WRITE": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

    def test_run_review_rejects_nested_forbidden_tool_call(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)

        with mock.patch.dict(os.environ, {"NCL_FAKE_FORBIDDEN": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

    def test_run_review_redacts_and_rejects_credential_output(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        output = root / "output"

        with mock.patch.dict(os.environ, {"NCL_FAKE_LEAK_AUTH": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head, output=output)

        persisted = b"\n".join(
            path.read_bytes() for path in output.rglob("*") if path.is_file()
        )
        self.assertNotIn(b"AUTH_FIXTURE_SECRET_12345", persisted)

    def test_run_review_binds_completed_event_stream_to_outer_rollout(self) -> None:
        for environment in (
            {"NCL_FAKE_THREAD_ID": "different"},
            {"NCL_FAKE_NO_COMPLETED": "1"},
            {"NCL_FAKE_WRONG_CWD": "1"},
        ):
            with self.subTest(environment=environment):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                with mock.patch.dict(os.environ, environment):
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head)

    def test_run_review_rejects_unproven_isolation_or_inspection(self) -> None:
        for environment in (
            {"NCL_FAKE_DECEPTIVE_CANARY": "1"},
            {"NCL_FAKE_DIFF_CHECK_ONLY": "1"},
            {"NCL_FAKE_BROAD_PROFILE": "1"},
            {"NCL_FAKE_SAME_SESSION": "1"},
        ):
            with self.subTest(environment=environment):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                with mock.patch.dict(os.environ, environment):
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head)

    def test_run_review_fails_before_model_when_profile_preflight_fails(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)

        with mock.patch.dict(os.environ, {"NCL_FAKE_PREFLIGHT_FAIL": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

    def test_run_review_times_out_and_never_persists_auth(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        output = root / "output"

        with mock.patch.dict(os.environ, {"NCL_FAKE_SLEEP": "2"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head, output=output, timeout_seconds=0.01)

        self.assertFalse(any(path.name == "auth.json" for path in output.rglob("*")))

    def test_run_review_refuses_nonempty_output(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        output = root / "output"
        output.mkdir()
        (output / "preserve").write_text("keep\n", encoding="utf-8")

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, output=output)

        self.assertEqual((output / "preserve").read_text(encoding="utf-8"), "keep\n")

    def test_run_review_refuses_output_inside_source_repo(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, output=repo / "review-output")

    def test_head_only_bundle_excludes_unrelated_oracle_object(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        oracle = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=repo,
            input="oracle-only\n",
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        with mock.patch.dict(os.environ, {"NCL_FORBIDDEN_OBJECT": oracle}):
            receipt = self.invoke(root, repo, base, head)

        self.assertTrue(receipt["ok"])

    def test_head_only_bundle_supports_detached_candidate(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        self.git(repo, "checkout", "--quiet", "--detach", head)

        self.assertTrue(self.invoke(root, repo, base, head)["ok"])

    def test_series_counts_failures_and_mechanically_caps_at_two(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        source = self.make_source_home(root)
        fake = self.make_fake_codex(root)
        packet = self.make_packet(root, base, head)
        series = review_runner.canonical_series_path(source, repo, base)
        arguments = {
            "repo": repo,
            "base": base,
            "head": head,
            "packet": packet,
            "source_codex_home": source,
            "codex_binary": fake,
        }

        with mock.patch.dict(os.environ, {"NCL_FAKE_EFFORT": "high"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                review_runner.run_series_review(**arguments)
        receipt = review_runner.run_series_review(**arguments)
        with self.assertRaises(review_runner.ReviewRunnerError):
            review_runner.run_series_review(**arguments)

        state = json.loads((series / "series.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [item["status"] for item in state["attempts"]], ["failed", "succeeded"]
        )
        self.assertEqual(receipt["attempt"], 2)
        self.assertEqual(Path(receipt["review_file"]).parent, series / "attempt-2")


if __name__ == "__main__":
    unittest.main()
