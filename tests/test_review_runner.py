from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from contextlib import redirect_stdout

from scripts import review_runner


ROOT = Path(__file__).resolve().parents[1]


class ReviewRunnerTests(unittest.TestCase):
    def make_temp(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name)

    def marker_processes(self, marker: str) -> list[Path]:
        matches = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                if marker.encode() in path.read_bytes():
                    matches.append(path)
            except OSError:
                continue
        return matches

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

    def make_contract(
        self, root: Path, base: str, repo: Path | None = None
    ) -> Path:
        repo = repo or root / "repo"
        contract = root / "task-contract.md"
        contract.write_text(
            "# Task Contract\n\n"
            "Objective: add one reviewed line.\n"
            "Acceptance: preserve the base line and add the head line.\n"
            "Exclusions: no other behavior.\n"
            f"Baseline: {base}\n"
            f"Repository/worktree: {repo}\n"
            "Goal thread ID: goal-fixture\n"
            f"Goal objective SHA256: {'b' * 64}\n"
            "Verification: inspect the exact base-to-head diff.\n"
            "Stop conditions: any failed review gate.\n",
            encoding="utf-8",
        )
        contract.chmod(0o600)
        return contract

    def make_packet(
        self, root: Path, base: str, head: str, repo: Path | None = None
    ) -> Path:
        repo = repo or root / "repo"
        contract = self.make_contract(root, base, repo)
        contract_text = contract.read_text(encoding="utf-8").rstrip()
        contract_hash = hashlib.sha256(contract.read_bytes()).hexdigest()
        packet = root / "packet.md"
        packet.write_text(
            "# Review packet\n\n"
            "- Objective: review the feature change.\n"
            f"- Repository root: {repo}\n"
            f"- Base commit: `{base}`\n"
            f"- Head commit: `{head}`\n"
            f"- Task contract SHA256: `{contract_hash}`\n"
            "- Acceptance: feature.txt gains one line without changing the first.\n"
            "- Applicable instructions: None.\n"
            "- Changed paths: feature.txt.\n"
            "- Verification receipt: focused test exit 0.\n"
            "- Scope exclusions: no unrelated paths.\n"
            "- Output contract: native review JSON with residual risk.\n\n"
            "--- TASK CONTRACT START ---\n"
            f"{contract_text}\n"
            "--- TASK CONTRACT END ---\n",
            encoding="utf-8",
        )
        packet.chmod(0o600)
        return packet

    def make_fake_codex(self, root: Path) -> Path:
        fake = root / "fake-codex"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, re, shlex, subprocess, sys, time\n"
            "if '--version' in sys.argv:\n"
            " print((pathlib.Path(os.environ['CODEX_HOME']) / 'auth.json').read_text() if os.environ.get('NCL_FAKE_VERSION_LEAK') else 'codex-cli 0.144.1-fixture')\n"
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
            "if os.environ.get('NCL_FAKE_OUTER_PROMPT_LEAK'):\n"
            " outer.append({'type':'response_item','payload':{'type':'message','role':'assistant','content':[{'type':'output_text','text':'prefix '+prompt}]}})\n"
            "reviewer = [\n"
            " {'type':'session_meta','payload':{'session_id':'outer','id':'outer' if os.environ.get('NCL_FAKE_SAME_SESSION') else 'review','parent_thread_id':'outer','cwd':cwd,'thread_source':'subagent','source':{'subagent':'review'}}},\n"
            " {'type':'response_item','payload':{'type':'message','role':'assistant' if os.environ.get('NCL_FAKE_WRONG_PROMPT_ROLE') else 'developer','content':[{'type':'input_text','text':prompt}]}},\n"
            " {'type':'turn_context','payload':{'cwd':context_cwd,'workspace_roots':[context_cwd],'model':'gpt-5.6-sol','effort':effort,'approval_policy':'never','sandbox_policy':{'type':'read-only'},'permission_profile':{'type':'managed','file_system':{'type':'restricted','entries':[{'path':{'type':'special','value':{'kind':'minimal'}},'access':'read'},{'path':{'type':'path','path':cwd},'access':'read'}] + ([{'path':{'type':'path','path':'/'},'access':'read'}] if os.environ.get('NCL_FAKE_BROAD_PROFILE') else [])},'network':'restricted'},'multi_agent_version':'disabled'}},\n"
            "]\n"
            "if os.environ.get('NCL_FAKE_FORBIDDEN'):\n"
            " reviewer.append({'type':'response_item','payload':{'type':'custom_tool_call','name':'exec','input':'await tools.web__run({})'}})\n"
            "if os.environ.get('NCL_FAKE_FORBIDDEN_FUNCTION'):\n"
            " reviewer.append({'type':'response_item','payload':{'type':'function_call','name':'mcp_call','arguments':'{}','call_id':'forbidden'}})\n"
            "if os.environ.get('NCL_FAKE_FORBIDDEN_DIRECT'):\n"
            " reviewer.append({'type':'response_item','payload':{'type':'function_call','name':os.environ['NCL_FAKE_FORBIDDEN_DIRECT'],'arguments':'{}','call_id':'forbidden-direct'}})\n"
            "result = {'findings':[],'overall_correctness':'patch is correct','overall_explanation':'No actionable findings.','overall_confidence_score':0.99,'review_root':str(pathlib.Path.cwd())}\n"
            "if os.environ.get('NCL_FAKE_DROP_FINDING'):\n"
            " result.update({'findings':[{'title':'[P1] Material defect','body':'Concrete failure','priority':1}],'overall_correctness':'patch is incorrect','overall_explanation':'A material defect remains.'})\n"
            "if os.environ.get('NCL_FAKE_INCONSISTENT_VERDICT') == 'empty-incorrect':\n"
            " result.update({'overall_correctness':'patch is incorrect','overall_explanation':'Incorrect without a finding.'})\n"
            "if os.environ.get('NCL_FAKE_INCONSISTENT_VERDICT') == 'finding-correct':\n"
            " result.update({'findings':[{'title':'[P1] Material defect','body':'Concrete failure','priority':1}],'overall_correctness':'patch is correct','overall_explanation':'[P1] Material defect Concrete failure'})\n"
            "if os.environ.get('NCL_FAKE_INCOMPLETE_FINDING'):\n"
            " result.update({'findings':[{'title':'[P1] Material defect','body':'Concrete failure'}],'overall_correctness':'patch is incorrect','overall_explanation':'[P1] Material defect Concrete failure'})\n"
            "if os.environ.get('NCL_FAKE_VALID_FINDING'):\n"
            " result.update({'findings':[{'title':'[P1] Material defect','body':'Criterion A fails; evidence and reproduction: run focused-test.','priority':1,'confidence_score':0.98,'code_location':{'absolute_file_path':str(pathlib.Path.cwd() / 'feature.txt'),'line_range':{'start':1,'end':2}}}],'overall_correctness':'patch is incorrect','overall_explanation':'[P1] Material defect Criterion A fails; evidence and reproduction: run focused-test.'})\n"
            "if os.environ.get('NCL_FAKE_LEAK_AUTH'):\n"
            " result['leak'] = (home / 'auth.json').read_text(encoding='utf-8')\n"
            "if os.environ.get('NCL_FAKE_MASK_INDEX'):\n"
            " subprocess.run(['git','update-index','--assume-unchanged','feature.txt'],check=True)\n"
            "print(json.dumps({'type':'thread.started','thread_id':os.environ.get('NCL_FAKE_THREAD_ID','outer')}))\n"
            "if os.environ.get('NCL_FAKE_EARLY_COMMAND'):\n"
            " print(json.dumps({'type':'item.started','item':{'id':'early','type':'command_execution','command':'cat '+str(home / 'auth.json'),'status':'in_progress'}}))\n"
            "canary_event = '/bin/bash -c ' + shlex.quote(canary_command + (' || true' if os.environ.get('NCL_FAKE_DECEPTIVE_CANARY') else ''))\n"
            "proof_event = f'git diff --check {base}..{head}' if os.environ.get('NCL_FAKE_DIFF_CHECK_ONLY') else f'git diff {base}..{head}'\n"
            "review_text = '   ' if os.environ.get('NCL_FAKE_BLANK_MESSAGE') else json.dumps(result)\n"
            "outer_text = '   ' if os.environ.get('NCL_FAKE_BLANK_MESSAGE') else ('No actionable findings.' if os.environ.get('NCL_FAKE_DROP_FINDING') else result['overall_explanation'])\n"
            "reviewer.append({'type':'response_item','payload':{'type':'message','role':'assistant','content':[{'type':'output_text','text':review_text}]}})\n"
            "outer.append({'type':'response_item','payload':{'type':'message','role':'assistant','content':[{'type':'output_text','text':'different' if os.environ.get('NCL_FAKE_OUTER_VERDICT_MISMATCH') else outer_text}]}})\n"
            "(session_dir / 'outer.jsonl').write_text(''.join(json.dumps(x)+'\\n' for x in outer), encoding='utf-8')\n"
            "(session_dir / 'review.jsonl').write_text(''.join(json.dumps(x)+'\\n' for x in reviewer), encoding='utf-8')\n"
            "print(json.dumps({'type':'item.started','item':{'id':'canary','type':'command_execution','command':canary_event,'status':'in_progress'}}))\n"
            "print(json.dumps({'type':'item.completed','item':{'id':'canary','type':'command_execution','command':canary_event,'aggregated_output':'','exit_code':0}}))\n"
            "print(json.dumps({'type':'item.started','item':{'id':'diff','type':'command_execution','command':proof_event,'status':'in_progress'}}))\n"
            "print(json.dumps({'type':'item.completed','item':{'id':'diff','type':'command_execution','command':proof_event,'aggregated_output':'' if os.environ.get('NCL_FAKE_DIFF_CHECK_ONLY') else 'diff --git evidence','exit_code':0}}))\n"
            "if os.environ.get('NCL_FAKE_FORBIDDEN_EVENT'):\n"
            " print(json.dumps({'type':'item.completed','item':{'id':'forbidden-event','type':'function_call','name':os.environ['NCL_FAKE_FORBIDDEN_EVENT'],'arguments':'{}'}}))\n"
            "if os.environ.get('NCL_FAKE_FORBIDDEN_ITEM_TYPE'):\n"
            " print(json.dumps({'type':'item.completed','item':{'id':'forbidden-item','type':os.environ['NCL_FAKE_FORBIDDEN_ITEM_TYPE']}}))\n"
            "print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':outer_text}}))\n"
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
            "output": root / "output",
        }
        arguments.update(overrides)
        if "packet" not in arguments:
            arguments["packet"] = self.make_packet(root, base, head)
        arguments.setdefault("task_contract", root / "task-contract.md")
        if "source_codex_home" not in arguments:
            arguments["source_codex_home"] = self.make_source_home(root)
        if "codex_binary" not in arguments:
            arguments["codex_binary"] = self.make_fake_codex(root)
        inherited = {
            key: value for key, value in os.environ.items() if key.startswith("NCL_")
        }
        original = review_runner._codex_environment
        with mock.patch.object(
            review_runner,
            "_codex_environment",
            side_effect=lambda *args: {**original(*args), **inherited},
        ):
            return review_runner.run_review(**arguments)

    def test_run_review_is_fresh_max_read_only_and_writes_receipt(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        output = root / "review-output"

        receipt = self.invoke(root, repo, base, head, output=output)

        self.assertTrue(receipt["ok"], receipt)
        review = json.loads((output / "review.md").read_text(encoding="utf-8"))
        self.assertEqual(review["findings"], [])
        self.assertEqual(review["overall_correctness"], "patch is correct")
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
            "review_runner_sha256",
        ):
            self.assertRegex(persisted[field], r"^[0-9a-f]{64}$")
        self.assertRegex(
            persisted["containment"]["binary_sha256"], r"^[0-9a-f]{64}$"
        )
        self.assertEqual(
            persisted["review_runner_sha256"],
            hashlib.sha256(Path(review_runner.__file__).read_bytes()).hexdigest(),
        )
        self.assertEqual(
            persisted["task_contract_sha256"],
            hashlib.sha256((root / "task-contract.md").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            persisted["source_packet_sha256"], persisted["reviewed_packet_sha256"]
        )
        self.assertIn(
            str(repo), (output / "packet.md").read_text(encoding="utf-8")
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

    def test_run_review_preserves_json_when_repo_path_needs_escaping(self) -> None:
        root = self.make_temp() / 'has"quote'
        root.mkdir()
        repo, base, head = self.make_repo(root)
        output = root / "review-output"

        self.assertTrue(self.invoke(root, repo, base, head, output=output)["ok"])

        review = json.loads((output / "review.md").read_text(encoding="utf-8"))
        self.assertEqual(review["review_root"], str(repo))

    def test_network_probe_fails_closed_when_interpreter_is_missing(self) -> None:
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        self.addCleanup(listener.close)
        clause = review_runner._network_probe_clause(listener.getsockname()[1])

        accessible = subprocess.run(
            ["/bin/sh", "-c", clause], check=False, capture_output=True
        )
        missing = subprocess.run(
            [
                "/bin/sh",
                "-c",
                clause.replace("python3", "/definitely/missing-python", 1),
            ],
            check=False,
            capture_output=True,
        )

        self.assertNotEqual(accessible.returncode, 0)
        self.assertNotEqual(missing.returncode, 0)

    def test_filesystem_hash_streams_regular_files(self) -> None:
        root = self.make_temp()
        target = root / "large.pack"
        target.write_bytes(b"pack-data" * 1024)
        original = Path.read_bytes

        def reject_whole_file_read(path: Path) -> bytes:
            if path == target:
                raise AssertionError("regular files must be streamed")
            return original(path)

        with mock.patch.object(Path, "read_bytes", reject_whole_file_read):
            digest = review_runner._filesystem_hash(root)

        self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_runtime_helper_aliases_do_not_escape_through_symlinks(self) -> None:
        root = self.make_temp()
        binary = root / "codex"
        binary.write_bytes(b"fixture-binary")
        binary.chmod(0o755)
        aliases = root / "aliases"

        review_runner._prepare_aliases(aliases, binary)

        for name in (
            "codex",
            "codex-linux-sandbox",
            "codex-execve-wrapper",
            "apply_patch",
        ):
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

    def test_runtime_environments_drop_host_credentials_proxies_and_loaders(self) -> None:
        root = self.make_temp()
        aliases = root / "aliases"
        with mock.patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sentinel-key",
                "HTTPS_PROXY": "http://sentinel.invalid",
                "LD_PRELOAD": "/tmp/sentinel.so",
                "PYTHONPATH": "/tmp/sentinel-python",
            },
        ):
            codex = review_runner._codex_environment(
                root / "home", root / "codex", root, aliases
            )
            git = review_runner._git_environment(root / "home")
        for environment in (codex, git):
            for key in ("OPENAI_API_KEY", "HTTPS_PROXY", "LD_PRELOAD", "PYTHONPATH"):
                self.assertNotIn(key, environment)
            self.assertEqual(environment["GIT_NO_LAZY_FETCH"], "1")

    def test_pid_namespace_contains_detached_children_on_exit_and_timeout(self) -> None:
        unshare = review_runner._resolve_containment_binary()

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
                    if not self.marker_processes(marker):
                        break
                    time.sleep(0.02)
                self.assertEqual(self.marker_processes(marker), [])

    def test_pid_namespace_dies_when_runner_is_killed(self) -> None:
        root = self.make_temp()
        marker = f"NCL_CRASH_{os.getpid()}_{time.time_ns()}"
        ready = root / "ready"
        inner = (
            "import pathlib,subprocess,sys,time;"
            "subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)',"
            "sys.argv[1]],start_new_session=True,stdin=subprocess.DEVNULL,"
            "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
            "pathlib.Path(sys.argv[2]).touch();time.sleep(60)"
        )
        command = review_runner._containment_command(
            review_runner._resolve_containment_binary(),
            [sys.executable, "-c", inner, marker, str(ready)],
        )
        outer = (
            "import json,os,sys;from pathlib import Path;"
            "from scripts import review_runner as r;"
            "r._run_process(json.loads(sys.argv[1]),cwd=Path(sys.argv[2]),"
            "env=os.environ.copy(),timeout=60)"
        )
        runner = subprocess.Popen(
            [sys.executable, "-c", outer, json.dumps(command), str(root)], cwd=ROOT
        )
        try:
            for _ in range(100):
                if ready.exists():
                    break
                time.sleep(0.02)
            self.assertTrue(ready.exists())
            runner.kill()
            runner.wait(timeout=5)
            for _ in range(100):
                if not self.marker_processes(marker):
                    break
                time.sleep(0.02)
            self.assertEqual(self.marker_processes(marker), [])
        finally:
            runner.kill() if runner.poll() is None else None
            for path in self.marker_processes(marker):
                os.kill(int(path.parent.name), signal.SIGKILL)

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

        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = root / "missing-contract.md"
        packet.write_text(
            f"Objective: x\nBase: {base}\nHead: {head}\n"
            "Acceptance: x\nVerification: x\n",
            encoding="utf-8",
        )
        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_requires_private_packet_and_preserves_its_bytes(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        source = self.make_source_home(root)
        binary = self.make_fake_codex(root)
        packet.chmod(0o644)
        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(
                root,
                repo,
                base,
                head,
                packet=packet,
                source_codex_home=source,
                codex_binary=binary,
            )

        packet.chmod(0o600)
        original_run = review_runner._run_process

        def mutate_after_review(*args, **kwargs):
            completed = original_run(*args, **kwargs)
            command = args[0]
            if "review" in command:
                packet.write_text("changed during review\n", encoding="utf-8")
                packet.chmod(0o600)
            return completed

        with mock.patch.object(
            review_runner, "_run_process", side_effect=mutate_after_review
        ):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(
                    root,
                    repo,
                    base,
                    head,
                    packet=packet,
                    source_codex_home=source,
                    codex_binary=binary,
                )

    def test_run_review_binds_contract_repository_to_candidate(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        contract = root / "task-contract.md"
        original_contract = contract.read_text(encoding="utf-8")
        wrong_contract = original_contract.replace(str(repo), "/definitely/wrong")
        old_hash = hashlib.sha256(original_contract.encode()).hexdigest()
        new_hash = hashlib.sha256(wrong_contract.encode()).hexdigest()
        contract.write_text(wrong_contract, encoding="utf-8")
        contract.chmod(0o600)
        packet.write_text(
            packet.read_text(encoding="utf-8")
            .replace(old_hash, new_hash)
            .replace(original_contract.rstrip(), wrong_contract.rstrip()),
            encoding="utf-8",
        )
        packet.chmod(0o600)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(
                root,
                repo,
                base,
                head,
                packet=packet,
                task_contract=contract,
            )

    def test_run_review_rejects_empty_contract_field_without_crossing_lines(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        contract = root / "task-contract.md"
        original_contract = contract.read_text(encoding="utf-8")
        empty_objective = original_contract.replace(
            "Objective: add one reviewed line.", "Objective:"
        )
        old_hash = hashlib.sha256(original_contract.encode()).hexdigest()
        new_hash = hashlib.sha256(empty_objective.encode()).hexdigest()
        contract.write_text(empty_objective, encoding="utf-8")
        contract.chmod(0o600)
        packet.write_text(
            packet.read_text(encoding="utf-8")
            .replace(old_hash, new_hash)
            .replace(original_contract.rstrip(), empty_objective.rstrip()),
            encoding="utf-8",
        )
        packet.chmod(0o600)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(
                root,
                repo,
                base,
                head,
                packet=packet,
                task_contract=contract,
            )

    def test_run_review_binds_packet_head_field_not_incidental_text(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        packet.write_text(
            packet.read_text(encoding="utf-8")
            .replace(f"- Head commit: `{head}`", f"- Head commit: `{'0' * 40}`")
            .replace(
                "- Verification receipt: focused test exit 0.",
                f"- Verification receipt: focused test exit 0; incidental {head}.",
            ),
            encoding="utf-8",
        )
        packet.chmod(0o600)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_requires_structured_packet_header(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        packet_text = packet.read_text(encoding="utf-8")
        contract_block = packet_text[packet_text.index(review_runner.TASK_CONTRACT_START) :]
        contract_hash = hashlib.sha256(
            (root / "task-contract.md").read_bytes()
        ).hexdigest()
        packet.write_text(
            "# Review packet\n\n"
            f"Head incidental {head}\n"
            f"Task contract SHA256: `{contract_hash}`\n\n"
            f"{contract_block}",
            encoding="utf-8",
        )
        packet.chmod(0o600)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_rejects_duplicate_contract_markers(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        packet.write_text(
            packet.read_text(encoding="utf-8").replace(
                review_runner.TASK_CONTRACT_START,
                f"{review_runner.TASK_CONTRACT_START}\nstale contract\n"
                f"{review_runner.TASK_CONTRACT_END}\n\n"
                f"{review_runner.TASK_CONTRACT_START}",
                1,
            ),
            encoding="utf-8",
        )
        packet.chmod(0o600)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_requires_every_review_packet_field(self) -> None:
        for line in (
            "- Repository root:",
            "- Applicable instructions:",
            "- Changed paths:",
            "- Scope exclusions:",
            "- Output contract:",
        ):
            with self.subTest(line=line):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                packet = self.make_packet(root, base, head)
                packet.write_text(
                    "\n".join(
                        item
                        for item in packet.read_text(encoding="utf-8").splitlines()
                        if not item.startswith(line)
                    )
                    + "\n",
                    encoding="utf-8",
                )
                packet.chmod(0o600)

                with self.assertRaises(review_runner.ReviewRunnerError):
                    self.invoke(root, repo, base, head, packet=packet)

        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        packet = self.make_packet(root, base, head)
        packet.write_text(
            packet.read_text(encoding="utf-8").replace(
                f"- Repository root: {repo}",
                "- Repository root: /definitely/wrong",
            ),
            encoding="utf-8",
        )
        packet.chmod(0o600)
        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_requires_canonical_no_goal_pair(self) -> None:
        for objective_hash, accepted in (("none", True), ("b" * 64, False)):
            with self.subTest(objective_hash=objective_hash, accepted=accepted):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                packet = self.make_packet(root, base, head)
                contract = root / "task-contract.md"
                original_contract = contract.read_text(encoding="utf-8")
                rewritten = original_contract.replace(
                    "Goal thread ID: goal-fixture\n"
                    f"Goal objective SHA256: {'b' * 64}",
                    "Goal thread ID: none\n"
                    f"Goal objective SHA256: {objective_hash}",
                )
                old_hash = hashlib.sha256(original_contract.encode()).hexdigest()
                new_hash = hashlib.sha256(rewritten.encode()).hexdigest()
                contract.write_text(rewritten, encoding="utf-8")
                contract.chmod(0o600)
                packet.write_text(
                    packet.read_text(encoding="utf-8")
                    .replace(old_hash, new_hash)
                    .replace(original_contract.rstrip(), rewritten.rstrip()),
                    encoding="utf-8",
                )
                packet.chmod(0o600)

                if accepted:
                    self.assertTrue(
                        self.invoke(root, repo, base, head, packet=packet)["ok"]
                    )
                else:
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head, packet=packet)

    def test_run_review_detects_clone_write_even_if_tool_claims_read_only(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)

        with mock.patch.dict(os.environ, {"NCL_FAKE_WRITE": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

    def test_run_review_rejects_nested_forbidden_tool_call(self) -> None:
        for key in ("NCL_FAKE_FORBIDDEN", "NCL_FAKE_FORBIDDEN_FUNCTION"):
            with self.subTest(key=key):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                with mock.patch.dict(os.environ, {key: "1"}):
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head)

    def test_run_review_rejects_forbidden_tools_from_events_and_direct_calls(self) -> None:
        environments = [
            {"NCL_FAKE_FORBIDDEN_EVENT": "image_gen__imagegen"},
            {"NCL_FAKE_FORBIDDEN_EVENT": "browser_open"},
            {"NCL_FAKE_FORBIDDEN_DIRECT": "request_plugin_install"},
            {"NCL_FAKE_FORBIDDEN_DIRECT": "computer_use"},
            {"NCL_FAKE_FORBIDDEN_ITEM_TYPE": "web_search"},
            {"NCL_FAKE_FORBIDDEN_ITEM_TYPE": "image_generation"},
            {"NCL_FAKE_FORBIDDEN_ITEM_TYPE": "collab_agent_tool_call"},
            {"NCL_FAKE_FORBIDDEN_ITEM_TYPE": "dynamic_tool_call"},
        ]
        for environment in environments:
            with self.subTest(environment=environment):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                with mock.patch.dict(os.environ, environment):
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head)

    def test_run_review_pins_binary_before_execution(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        binary = self.make_fake_codex(root)
        expected_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
        original_prepare = review_runner._prepare_aliases

        def replace_source_after_aliases(directory: Path, source: Path) -> Path | None:
            pinned = original_prepare(directory, source)
            replacement = root / "replacement-codex"
            replacement.write_bytes(
                source.read_bytes().replace(
                    b"codex-cli 0.144.1-fixture", b"codex-cli 9.9.9-race"
                )
            )
            replacement.chmod(0o755)
            os.replace(replacement, source)
            return pinned

        with mock.patch.object(
            review_runner, "_prepare_aliases", side_effect=replace_source_after_aliases
        ):
            receipt = self.invoke(root, repo, base, head, codex_binary=binary)

        self.assertEqual(receipt["cli_version"], "codex-cli 0.144.1-fixture")
        self.assertEqual(receipt["codex_binary_sha256"], expected_hash)

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

    def test_run_review_rejects_credential_output_from_version_probe(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        output = root / "output"
        with mock.patch.dict(os.environ, {"NCL_FAKE_VERSION_LEAK": "1"}):
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
            {"NCL_FAKE_BLANK_MESSAGE": "1"},
            {"NCL_FAKE_EARLY_COMMAND": "1"},
            {"NCL_FAKE_WRONG_PROMPT_ROLE": "1"},
            {"NCL_FAKE_OUTER_PROMPT_LEAK": "1"},
            {"NCL_FAKE_OUTER_VERDICT_MISMATCH": "1"},
            {"NCL_FAKE_DROP_FINDING": "1"},
        ):
            with self.subTest(environment=environment):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                with mock.patch.dict(os.environ, environment):
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head)

    def test_run_review_rejects_internally_inconsistent_verdict(self) -> None:
        for mode in ("empty-incorrect", "finding-correct"):
            with self.subTest(mode=mode):
                root = self.make_temp()
                repo, base, head = self.make_repo(root)
                with mock.patch.dict(
                    os.environ, {"NCL_FAKE_INCONSISTENT_VERDICT": mode}
                ):
                    with self.assertRaises(review_runner.ReviewRunnerError):
                        self.invoke(root, repo, base, head)

    def test_run_review_rejects_incomplete_and_accepts_complete_finding(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        with mock.patch.dict(os.environ, {"NCL_FAKE_INCOMPLETE_FINDING": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        with mock.patch.dict(os.environ, {"NCL_FAKE_VALID_FINDING": "1"}):
            receipt = self.invoke(root, repo, base, head)
        review = json.loads(Path(receipt["review_file"]).read_text(encoding="utf-8"))
        self.assertEqual(review["findings"][0]["priority"], 1)

    def test_run_review_requires_git_worktree_root(self) -> None:
        root = self.make_temp()
        repo, base, _ = self.make_repo(root)
        nested = repo / "nested"
        nested.mkdir()
        (nested / "tracked.txt").write_text("nested\n", encoding="utf-8")
        self.git(repo, "add", "nested/tracked.txt")
        self.git(repo, "commit", "-q", "-m", "nested head")
        head = self.git(repo, "rev-parse", "HEAD")
        packet = self.make_packet(root, base, head, nested)

        with self.assertRaises(review_runner.ReviewRunnerError):
            self.invoke(
                root,
                nested,
                base,
                head,
                packet=packet,
                task_contract=root / "task-contract.md",
            )

    def test_run_review_rejects_index_mask_added_during_review(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        with mock.patch.dict(os.environ, {"NCL_FAKE_MASK_INDEX": "1"}):
            with self.assertRaises(review_runner.ReviewRunnerError):
                self.invoke(root, repo, base, head)

    def test_run_review_accepts_clean_smudge_filtered_source(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        self.git(repo, "config", "filter.demo.clean", "sed 's/^SMUDGED://'")
        self.git(repo, "config", "filter.demo.smudge", "sed 's/^/SMUDGED:/'")
        (repo / ".gitattributes").write_text("feature.txt filter=demo\n", encoding="utf-8")
        self.git(repo, "add", ".gitattributes")
        self.git(repo, "commit", "-q", "-m", "filter")
        base = self.git(repo, "rev-parse", "HEAD")
        self.git(repo, "checkout", "--quiet", "HEAD", "--", "feature.txt")
        (repo / "feature.txt").write_text(
            "SMUDGED:base\nSMUDGED:head\nSMUDGED:third\n", encoding="utf-8"
        )
        self.git(repo, "add", "feature.txt")
        self.git(repo, "commit", "-q", "-m", "filtered head")
        head = self.git(repo, "rev-parse", "HEAD")
        self.git(repo, "checkout", "--quiet", "HEAD", "--", "feature.txt")
        self.assertEqual(self.git(repo, "status", "--porcelain"), "")

        self.assertTrue(self.invoke(root, repo, base, head)["ok"])

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
            "task_contract": root / "task-contract.md",
            "source_codex_home": source,
            "codex_binary": fake,
        }

        with mock.patch.dict(os.environ, {"NCL_FAKE_EFFORT": "high"}):
            original = review_runner._codex_environment
            with mock.patch.object(
                review_runner,
                "_codex_environment",
                side_effect=lambda *args: {
                    **original(*args),
                    "NCL_FAKE_EFFORT": "high",
                },
            ):
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

    def test_series_rejects_symlinked_canonical_directory(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        source = self.make_source_home(root)
        series = review_runner.canonical_series_path(source, repo, base)
        series.parent.mkdir(parents=True)
        external = root / "external-series"
        external.mkdir()
        series.symlink_to(external, target_is_directory=True)

        with self.assertRaises(review_runner.ReviewRunnerError):
            review_runner.run_series_review(
                repo=repo,
                base=base,
                head=head,
                packet=self.make_packet(root, base, head),
                task_contract=root / "task-contract.md",
                source_codex_home=source,
                codex_binary=self.make_fake_codex(root),
            )
        self.assertEqual(list(external.iterdir()), [])

    def test_series_rejects_dangling_attempt_symlink(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        source = self.make_source_home(root)
        series = review_runner.canonical_series_path(source, repo, base)
        series.mkdir(parents=True)
        (series / "series.json").write_text(
            json.dumps(
                {
                    "schema_version": review_runner.SERIES_SCHEMA,
                    "repo": str(repo),
                    "base": base,
                    "attempts": [],
                }
            ),
            encoding="utf-8",
        )
        external = root / "external-attempt"
        (series / "attempt-1").symlink_to(external, target_is_directory=True)

        with self.assertRaises(review_runner.ReviewRunnerError):
            review_runner.run_series_review(
                repo=repo,
                base=base,
                head=head,
                packet=self.make_packet(root, base, head),
                task_contract=root / "task-contract.md",
                source_codex_home=source,
                codex_binary=self.make_fake_codex(root),
            )
        self.assertFalse(external.exists())

    def test_series_rejects_hardlinked_lock_without_clobbering_target(self) -> None:
        root = self.make_temp()
        repo, base, head = self.make_repo(root)
        source = self.make_source_home(root)
        series = review_runner.canonical_series_path(source, repo, base)
        series.mkdir(parents=True)
        victim = root / "victim"
        victim.write_text("DO NOT CLOBBER\n", encoding="utf-8")
        victim.chmod(0o600)
        os.link(victim, series / ".lock")

        with self.assertRaises(review_runner.ReviewRunnerError):
            review_runner.run_series_review(
                repo=repo,
                base=base,
                head=head,
                packet=self.make_packet(root, base, head),
                task_contract=root / "task-contract.md",
                source_codex_home=source,
                codex_binary=self.make_fake_codex(root),
            )

        self.assertEqual(victim.read_text(encoding="utf-8"), "DO NOT CLOBBER\n")

    def test_cli_requires_and_routes_task_contract(self) -> None:
        root = self.make_temp()
        contract = root / "contract.md"
        with mock.patch.object(
            review_runner, "run_series_review", return_value={"ok": True}
        ) as run:
            with redirect_stdout(io.StringIO()):
                exit_code = review_runner.main(
                    [
                        "--repo",
                        str(root),
                        "--base",
                        "base",
                        "--head",
                        "head",
                        "--packet",
                        str(root / "packet.md"),
                        "--task-contract",
                        str(contract),
                    ]
                )
        self.assertEqual(exit_code, 0)
        self.assertEqual(run.call_args.kwargs["task_contract"], contract)


if __name__ == "__main__":
    unittest.main()
