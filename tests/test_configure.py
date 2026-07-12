from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import configure


ROOT = Path(__file__).resolve().parents[1]


class ConfigureTests(unittest.TestCase):
    def make_home(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name) / "codex"

    def snapshot(self, root: Path) -> dict[str, bytes]:
        if not root.exists():
            return {}
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and not path.is_symlink()
        }

    def test_enable_empty_home_and_doctor_without_custom_agent(self) -> None:
        home = self.make_home()

        receipt = configure.enable(home, ROOT)

        self.assertEqual(receipt["status"], "enabled")
        self.assertIn(
            configure.GUIDANCE_START, (home / "AGENTS.md").read_text(encoding="utf-8")
        )
        self.assertEqual(stat.S_IMODE((home / "AGENTS.md").stat().st_mode), 0o644)
        self.assertEqual(
            stat.S_IMODE((home / "native-codex-loop/install.json").stat().st_mode),
            0o600,
        )
        self.assertFalse((home / "agents").exists())
        self.assertFalse((home / "config.toml").exists())
        self.assertTrue(configure.doctor(home, ROOT)["ok"])

    def test_enable_preserves_unrelated_bytes_mode_and_disable_restores(self) -> None:
        home = self.make_home()
        home.mkdir(parents=True)
        agents_file = home / "AGENTS.md"
        original = b"# Existing\n\nKeep this byte-for-byte.\n"
        agents_file.write_bytes(original)
        agents_file.chmod(0o640)

        configure.enable(home, ROOT)

        installed = agents_file.read_bytes()
        self.assertTrue(installed.startswith(original))
        self.assertIn(configure.GUIDANCE_START.encode(), installed)
        self.assertEqual(stat.S_IMODE(agents_file.stat().st_mode), 0o640)
        configure.disable(home)
        self.assertEqual(agents_file.read_bytes(), original)
        self.assertEqual(stat.S_IMODE(agents_file.stat().st_mode), 0o640)

    def test_enable_is_byte_idempotent(self) -> None:
        home = self.make_home()

        configure.enable(home, ROOT)
        first = self.snapshot(home)
        receipt = configure.enable(home, ROOT)

        self.assertFalse(receipt["changed"])
        self.assertEqual(self.snapshot(home), first)

    def test_nonempty_override_rejects_enable_before_writes(self) -> None:
        home = self.make_home()
        home.mkdir(parents=True)
        (home / "AGENTS.override.md").write_text("override\n", encoding="utf-8")
        before = self.snapshot(home)

        with self.assertRaises(configure.ConfigurationError):
            configure.enable(home, ROOT)

        self.assertEqual(self.snapshot(home), before)

    def test_malformed_or_unmanaged_markers_are_rejected_before_writes(self) -> None:
        for content in (
            f"prefix\n{configure.GUIDANCE_START}\nmissing end\n",
            f"{configure.GUIDANCE_START}\nforeign\n{configure.GUIDANCE_END}\n",
            f"{configure.GUIDANCE_END}\nforeign\n{configure.GUIDANCE_START}\n",
        ):
            with self.subTest(content=content):
                home = self.make_home()
                home.mkdir(parents=True)
                (home / "AGENTS.md").write_text(content, encoding="utf-8")
                before = self.snapshot(home)

                with self.assertRaises(configure.ConfigurationError):
                    configure.enable(home, ROOT)

                self.assertEqual(self.snapshot(home), before)

    def test_enable_rejects_symlinked_configuration_paths(self) -> None:
        home = self.make_home()
        home.mkdir(parents=True)
        target = home.parent / "outside.md"
        target.write_text("outside\n", encoding="utf-8")
        (home / "AGENTS.md").symlink_to(target)

        with self.assertRaises(configure.ConfigurationError):
            configure.enable(home, ROOT)

        self.assertEqual(target.read_text(encoding="utf-8"), "outside\n")
        self.assertFalse((home / "native-codex-loop").exists())

    def test_disable_rejects_user_modified_guidance(self) -> None:
        home = self.make_home()
        configure.enable(home, ROOT)
        agents_file = home / "AGENTS.md"
        agents_file.write_text(
            agents_file.read_text(encoding="utf-8").replace(
                "use $native-codex-loop", "use the locally edited workflow"
            ),
            encoding="utf-8",
        )
        before = self.snapshot(home)

        with self.assertRaises(configure.ConfigurationError):
            configure.disable(home)

        self.assertEqual(self.snapshot(home), before)

    def test_enable_rolls_back_if_state_write_fails(self) -> None:
        home = self.make_home()
        home.mkdir(parents=True)
        agents_file = home / "AGENTS.md"
        original = b"# Existing\n"
        agents_file.write_bytes(original)
        real_write = configure._atomic_write
        calls = 0

        def fail_second(path: Path, data: bytes, mode: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected state failure")
            real_write(path, data, mode)

        with mock.patch.object(configure, "_atomic_write", side_effect=fail_second):
            with self.assertRaises(configure.ConfigurationError):
                configure.enable(home, ROOT)

        self.assertEqual(agents_file.read_bytes(), original)
        self.assertFalse((home / "native-codex-loop/install.json").exists())

    def test_doctor_reports_drift_without_repairing_it(self) -> None:
        home = self.make_home()
        configure.enable(home, ROOT)
        agents_file = home / "AGENTS.md"
        agents_file.write_text(
            agents_file.read_text(encoding="utf-8") + "drift\n", encoding="utf-8"
        )
        before = self.snapshot(home)

        receipt = configure.doctor(home, ROOT)

        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["status"], "drifted")
        self.assertEqual(self.snapshot(home), before)

    def test_corrupt_state_shape_fails_closed(self) -> None:
        home = self.make_home()
        state = home / "native-codex-loop/install.json"
        state.parent.mkdir(parents=True)
        state.write_text('{"schema_version": 1, "guidance": {}}\n', encoding="utf-8")

        self.assertFalse(configure.doctor(home, ROOT)["ok"])
        with self.assertRaises(configure.ConfigurationError):
            configure.enable(home, ROOT)

    def test_non_object_state_fails_closed(self) -> None:
        home = self.make_home()
        state = home / "native-codex-loop/install.json"
        state.parent.mkdir(parents=True)
        state.write_text("[]\n", encoding="utf-8")

        self.assertFalse(configure.doctor(home, ROOT)["ok"])
        with self.assertRaises(configure.ConfigurationError):
            configure.enable(home, ROOT)

    def test_enable_upgrades_managed_block_and_disable_still_restores(self) -> None:
        home = self.make_home()
        home.mkdir(parents=True)
        agents = home / "AGENTS.md"
        original = b"# Existing\n"
        agents.write_bytes(original)
        configure.enable(home, ROOT)
        upgraded = (
            f"{configure.GUIDANCE_START}\n## Native Codex Loop vNext\n"
            f"Use the upgraded gate.\n{configure.GUIDANCE_END}"
        )

        with mock.patch.object(configure, "GUIDANCE_BLOCK", upgraded):
            self.assertFalse(configure.doctor(home, ROOT)["ok"])
            configure.enable(home, ROOT)
            self.assertTrue(configure.doctor(home, ROOT)["ok"])
            configure.disable(home)

        self.assertEqual(agents.read_bytes(), original)

    def test_cli_uses_codex_home_environment(self) -> None:
        home = self.make_home()
        env = os.environ.copy()
        env["CODEX_HOME"] = str(home)

        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "configure.py"), "enable"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["codex_home"], str(home))
        self.assertTrue((home / "AGENTS.md").is_file())
        self.assertFalse((home / "agents").exists())


if __name__ == "__main__":
    unittest.main()
