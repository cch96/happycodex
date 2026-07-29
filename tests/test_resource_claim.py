from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills" / "happycodex" / "scripts" / "resource_claim.py"


def run_claim(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class ResourceClaimTests(unittest.TestCase):
    def acquire(
        self,
        receipt: Path,
        *resources: str,
        owner: str = "Root",
        task: str = "task-a",
    ) -> subprocess.CompletedProcess[str]:
        return run_claim(
            "acquire",
            "--owner",
            owner,
            "--task",
            task,
            "--execplan",
            str(receipt.parent / "ExecPlan.md"),
            "--receipt",
            str(receipt),
            *(
                argument
                for resource in resources
                for argument in ("--resource", resource)
            ),
        )

    def test_same_resource_has_exactly_one_owner(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            resource = f"ledger={root / 'ledger.json'}"
            first = root / "first.json"
            second = root / "second.json"
            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        str(HELPER),
                        "acquire",
                        "--owner",
                        f"owner-{index}",
                        "--task",
                        f"task-{index}",
                        "--execplan",
                        str(root / f"plan-{index}.md"),
                        "--receipt",
                        str(receipt),
                        "--resource",
                        resource,
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                for index, receipt in enumerate((first, second), start=1)
            ]
            returns = [
                process.communicate()[0:2] + (process.returncode,)
                for process in processes
            ]
            self.assertEqual(sorted(item[2] for item in returns), [0, 2], returns)
            winner = first if first.exists() else second
            self.assertEqual(
                run_claim("verify", "--receipt", str(winner)).returncode, 0
            )
            self.assertEqual(
                run_claim("release", "--receipt", str(winner)).returncode, 0
            )

    def test_disjoint_resource_sets_can_run_in_parallel(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            receipts = (root / "a.json", root / "b.json")
            sets = (
                (
                    f"worktree={root / 'repo-a'}",
                    f"ref={root / 'repo-a'}::refs/tasks/a",
                    f"ledger={root / 'ledger-a.json'}",
                    f"output={root / 'output-a'}",
                    f"activation={root / 'activation-a'}",
                ),
                (
                    f"worktree={root / 'repo-b'}",
                    f"ref={root / 'repo-b'}::refs/tasks/b",
                    f"ledger={root / 'ledger-b.json'}",
                    f"output={root / 'output-b'}",
                    f"activation={root / 'activation-b'}",
                ),
            )
            for repo in (root / "repo-a", root / "repo-b"):
                subprocess.run(["git", "init", "-q", str(repo)], check=True)
            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        str(HELPER),
                        "acquire",
                        "--owner",
                        "Root",
                        "--task",
                        f"task-{index}",
                        "--execplan",
                        str(root / f"plan-{index}.md"),
                        "--receipt",
                        str(receipt),
                        *(
                            argument
                            for resource in resources
                            for argument in ("--resource", resource)
                        ),
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                for index, (receipt, resources) in enumerate(
                    zip(receipts, sets), start=1
                )
            ]
            completed = [
                process.communicate()[0:2] + (process.returncode,)
                for process in processes
            ]
            self.assertEqual([item[2] for item in completed], [0, 0], completed)
            for receipt in receipts:
                self.assertEqual(
                    run_claim("verify", "--receipt", str(receipt)).returncode, 0
                )
                self.assertEqual(
                    run_claim("release", "--receipt", str(receipt)).returncode, 0
                )

    def test_partial_acquire_rolls_back_without_write_permission(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            blocked = f"output={root / 'z-blocked'}"
            free = f"ledger={root / 'a-free.json'}"
            blocker = root / "blocker.json"
            attempted = root / "attempted.json"
            retry = root / "retry.json"
            self.assertEqual(self.acquire(blocker, blocked).returncode, 0)
            failed = self.acquire(attempted, free, blocked, task="task-b")
            self.assertEqual(failed.returncode, 2, failed.stderr)
            self.assertFalse(attempted.exists())
            self.assertEqual(self.acquire(retry, free, task="task-c").returncode, 0)
            for receipt in (retry, blocker):
                self.assertEqual(
                    run_claim("release", "--receipt", str(receipt)).returncode, 0
                )

    def test_stale_or_tampered_claim_blocks_and_is_never_auto_released(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            resource = f"activation={root / 'active-plugin'}"
            receipt = root / "owner.json"
            contender = root / "contender.json"
            self.assertEqual(self.acquire(receipt, resource).returncode, 0)
            data = json.loads(receipt.read_text(encoding="utf-8"))
            claim_dir = Path(data["claims"][0]["claim_dir"])
            metadata = claim_dir / "claim"
            metadata.write_text('{"schema_version":999}\n', encoding="utf-8")

            self.assertEqual(
                run_claim("verify", "--receipt", str(receipt)).returncode,
                2,
            )
            self.assertEqual(
                self.acquire(contender, resource, task="task-b").returncode,
                2,
            )
            self.assertTrue(claim_dir.is_dir())
            self.assertFalse(contender.exists())

    def test_git_ref_claims_use_the_common_git_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = root / "repo"
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            receipt = root / "ref.json"
            resource = f"ref={repo}::refs/tasks/rb-008"
            acquired = self.acquire(receipt, resource)
            self.assertEqual(acquired.returncode, 0, acquired.stderr)
            data = json.loads(receipt.read_text(encoding="utf-8"))
            common_dir = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-common-dir",
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertTrue(
                Path(data["claims"][0]["claim_dir"]).is_relative_to(Path(common_dir))
            )
            self.assertEqual(
                run_claim("release", "--receipt", str(receipt)).returncode, 0
            )

    def test_worktree_uses_common_dir_but_file_claim_is_resource_adjacent(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = root / "repo"
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            state = repo / "state"
            state.mkdir()
            ledger = state / "current.json"
            receipt = root / "locations.json"
            acquired = self.acquire(
                receipt,
                f"worktree={repo}",
                f"ledger={ledger}",
            )
            self.assertEqual(acquired.returncode, 0, acquired.stderr)
            claims = {
                item["resource"].split("=", 1)[0]: Path(item["claim_dir"])
                for item in json.loads(receipt.read_text(encoding="utf-8"))["claims"]
            }
            common_dir = Path(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "rev-parse",
                        "--path-format=absolute",
                        "--git-common-dir",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
            self.assertEqual(
                claims["worktree"].parent,
                common_dir / "happycodex-resource-claims",
            )
            self.assertEqual(
                claims["ledger"].parent,
                ledger.parent / ".happycodex-resource-claims",
            )
            self.assertEqual(
                run_claim("release", "--receipt", str(receipt)).returncode,
                0,
            )
