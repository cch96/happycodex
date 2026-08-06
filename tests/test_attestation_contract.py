from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import unittest

from evaluation.identity import evaluator_components
from evaluation.records import RECORD_TYPES
from tests.attestation_fixtures import CANDIDATE_REVISION, bundle


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "execplans" / "happycodex-evaluator-attestation.md"
ROUTING_PLAN = ROOT / "docs" / "execplans" / "happycodex-0-7-0-role-routing.md"
PRESERVED_SKILL_TREE = "d9e525a267fbf36669d409ba1b4b009a6beeeea5"
CANDIDATE_VERSION = "0.7.2"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


class RepositoryContractTests(unittest.TestCase):
    def test_published_v065_tree_is_immutable_and_candidate_is_v072(self):
        self.assertEqual(CANDIDATE_REVISION, "HEAD")
        self.assertEqual(git("rev-parse", "v0.6.5:skills/happycodex"), PRESERVED_SKILL_TREE)
        released = json.loads(git("show", "v0.6.5:.codex-plugin/plugin.json"))
        candidate = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(released["version"], "0.6.5")
        self.assertEqual(candidate["version"], CANDIDATE_VERSION)
        self.assertNotEqual(
            git("show", "v0.6.5:skills/happycodex/SKILL.md"),
            (ROOT / "skills" / "happycodex" / "SKILL.md").read_text().strip(),
        )

    def test_v070_skill_uses_material_supported_flow_boundary(self):
        raw = (ROOT / "skills" / "happycodex" / "SKILL.md").read_text()
        text = " ".join(raw.split())
        required = (
            "material failures reachable through supported workflows",
            "including compaction, concurrency, and partial effects",
            "non-adversarial but fallible",
            "verify state and identity, not motive",
            "Prefer the smallest sufficient control",
            "expanding scope or trust boundaries requires explicit user authority",
            "remaining alternatives would not change that Outcome",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        retired_vocabulary = (
            "uncertainty qualifies",
            "spoofed",
            "removes the bypass",
            "contamination",
            "never substitute a writer",
            "preferred answers",
            "evidence ledger",
            "owner token",
            "separate exact gate plan",
            "content-addressed bundle",
        )
        for retired in retired_vocabulary:
            with self.subTest(retired=retired):
                self.assertNotIn(retired, text.lower())

        authority = " ".join(raw.split("- Authority:", 1)[1].split("- Resource claims:", 1)[0].split())
        self.assertIn("exact current grant", authority)
        self.assertIn("out-of-scope authority", authority)
        self.assertNotIn("user authority permits writes", authority.lower())

        effects = " ".join(raw.split("- Cost and effects:", 1)[1].split("## Review and complete", 1)[0].split())
        for boundary in ("outcome receipt", "same authorization", "ambiguous or partial effects stop", "separate authority"):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, effects)
        for evaluator_term in ("provider", "pre-provider", "infrastructure"):
            with self.subTest(evaluator_term=evaluator_term):
                self.assertNotIn(evaluator_term, effects.lower())

    def test_v072_role_routing_contract_is_capability_proportional(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        skill = (ROOT / "skills" / "happycodex" / "SKILL.md").read_text()
        reference = (ROOT / "skills" / "happycodex" / "references" / "execplan.md").read_text()
        readme_zh = (ROOT / "README.md").read_text()
        readme_en = (ROOT / "README.en.md").read_text()
        routing_plan = ROUTING_PLAN.read_text()
        native_parallel_plan = (
            ROOT
            / "docs"
            / "execplans"
            / "happycodex-0-7-1-native-parallel-exploration.md"
        ).read_text()
        compact = " ".join(skill.split())
        ref_compact = " ".join(reference.split())
        review_compact = " ".join(skill.split("## Review and complete", 1)[1].split())
        candidate_review_compact = " ".join(reference.split("## Candidate and review", 1)[1].split("## Recovery", 1)[0].split())
        zh_compact = " ".join(readme_zh.split())
        en_compact = " ".join(readme_en.split())
        plan_compact = " ".join(routing_plan.split())

        approved_token_digests = (
            "7b298a823a9224e8a9c8b61984c7d32c90431dd25e63372eb22b12e3c1f366b9",
            "aa5f3b7e696f9f96bd8f80f8aa81a7bd00becb42596cec1c3a5654f5b142fa6c",
        )
        digest_values = tuple(
            re.findall(
                r"(?i)owner-token SHA-256\s*:?\s*\n\s*`([0-9a-f]{64})`",
                native_parallel_plan,
            )
        )
        raw_owner_token_count = len(
            re.findall(
                r"(?i)\bowner token\s*:?\s*\n\s*`(?:[0-9a-f]{64})`",
                native_parallel_plan,
            )
        )
        self.assertEqual(
            (digest_values, raw_owner_token_count),
            (approved_token_digests, 0),
        )

        self.assertEqual(manifest["version"], CANDIDATE_VERSION)
        self.assertNotIn("agents", manifest)
        self.assertIn("capability-proportional admission", manifest["description"])
        self.assertIn(
            "missing optional telemetry does not block unrelated guarantees",
            manifest["interface"]["longDescription"],
        )

        skill_matrix = (
            "| Root | `gpt-5.6-sol` | `max` |",
            "| Explorer | `gpt-5.6-terra` | `high` |",
            "| Challenger | `gpt-5.6-sol` | `high` |",
            "| Executor | `gpt-5.6-sol` | `high` |",
            "| Exact-final | `gpt-5.6-sol` | `max` |",
        )
        for row in skill_matrix:
            with self.subTest(row=row):
                self.assertIn(row, skill)

        required_runtime = (
            "Before dispatch and before reading substantive child output, record",
            "intended use and consequence",
            "guarantees required by the task, source, or user",
            "Automatic capability handling cannot manufacture authority or silently waive a required guarantee",
            "Platform acceptance of the exact spawn request",
            "mechanically authenticated child/run/result handle",
            "Missing output identity cannot downgrade",
            "On the portable builtin/default path, explicitly pin model and effort",
            "its file's model and effort take precedence",
            "omit redundant or conflicting explicit model/effort arguments",
            "Effective agent name is record-only when exposed; if absent, record `unverified`",
            "Missing effective model or effort: record `unverified` and continue unless exact routing was predeclared required",
            "An exposed effective model or effort mismatch requires discard and stop",
            "Do not claim exact routing while it is unverified",
            "Missing effective sandbox or approval: record `unverified`",
            "When technical isolation was predeclared required, independently establish the isolation or effect boundary or stop",
            "When it was not required, continue without claiming technical isolation",
            "A full-access result mismatches only a predeclared read-only technical-isolation guarantee",
            "Prompt/profile read-only remains non-" + "pro" + "of",
            "Run multiple Explorers concurrently only when multiple such axes exist",
            "give each Explorer exactly one bounded question",
            "For two or more qualifying axes, dispatch one native Explorer per axis concurrently through the host's builtin `explorer` selector or an admitted namespaced custom Explorer selector",
            "Parallel ordinary tool calls are not Explorer dispatches",
            "Unverified Explorer or Challenger route or isolation output is advisory leads only",
            "Root reproduces every material fact from source before it affects a plan, grant, or phase",
            "Challenger runs before the behavior-plan freeze",
            "Only after that freeze does the unique Executor write",
            "Executor may write despite missing route or permission telemetry only when host-issued output identity, fixed-writer ownership, exact grant, source/prestate, paths/resources, and allowed effects are bound",
            "Root relies on actual Git, tests, and receipts, not Executor prose",
            "After candidate freeze, spawn exactly one fresh Exact-final",
            "empty history",
            "neutral brief",
            "Exact-final may count without verified model or permission telemetry only when exact routing and hard isolation were not predeclared required",
            "candidate identity remains unchanged",
            "disclose unverified guarantees",
            "If required hard isolation is unproven, review remains open",
            "No user-facing modes or levels exist",
            "Never require `普通模式继续`",
            "Ask the user when continuation would change the Outcome, authority, trust boundary, or an explicitly required guarantee; expand the frozen envelope; or exceed or continue after exhaustion of the bounded automatic repair budget",
            "Only a Root-admitted in-envelope repair with remaining authorized repair budget returns to `working`",
        )
        for phrase in required_runtime:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, compact)
        self.assertNotIn("runtime-issued logical role", compact)

        always_hard = (
            "explicit mismatch in a requested or required identity or route",
            "malformed or ambiguous claimed evidence",
            "unsafe exposed value relative to a predeclared required guarantee",
            "candidate or source drift",
            "ambiguous or partial effects",
        )
        for phrase in always_hard:
            with self.subTest(always_hard=phrase):
                self.assertIn(phrase, compact)

        retired_blanket_rules = (
            "If the host cannot accept the exact request or expose the required effective metadata, do not dispatch",
            "Until Root reads the runtime-issued session/turn metadata",
            "If either required evidence source is missing or the cross-bind mismatches",
        )
        for phrase in retired_blanket_rules:
            with self.subTest(retired_blanket_rule=phrase):
                self.assertNotIn(phrase, compact)

        order = (
            "Root first decomposes the problem",
            "Challenger runs before the behavior-plan freeze",
            "Only after that freeze does the unique Executor write",
            "After candidate freeze, spawn exactly one fresh Exact-final",
        )
        positions = [compact.index(phrase) for phrase in order]
        self.assertEqual(positions, sorted(positions))

        readme_matrices = (
            (readme_en, (
                "| Root | `gpt-5.6-sol` | `max` |",
                "| Explorer | `gpt-5.6-terra` | `high` |",
                "| Challenger | `gpt-5.6-sol` | `high` |",
                "| Unique Executor | `gpt-5.6-sol` | `high` |",
                "| Unique fresh Exact-final | `gpt-5.6-sol` | `max` |",
            )),
            (readme_zh, (
                "| Root | `gpt-5.6-sol` | `max` |",
                "| Explorer | `gpt-5.6-terra` | `high` |",
                "| Challenger | `gpt-5.6-sol` | `high` |",
                "| 唯一 Executor | `gpt-5.6-sol` | `high` |",
                "| 唯一全新 Exact-final | `gpt-5.6-sol` | `max` |",
            )),
        )
        for text, rows in readme_matrices:
            for row in rows:
                with self.subTest(readme_row=row):
                    self.assertIn(row, text)

        for phrase in (
            "one fresh logically read-only reviewer",
            "Technical read-only isolation applies only when predeclared required",
            "Missing optional route or permission telemetry alone does not block review and is disclosed",
        ):
            with self.subTest(readme_en_phase=phrase):
                self.assertIn(phrase, en_compact)
        self.assertNotIn("one fresh isolated read-only reviewer", en_compact)

        for phrase in (
            "一个全新、逻辑只读的评审者",
            "只有预先声明为必需时，才要求技术只读隔离",
            "缺失可选 route/permission telemetry 本身不阻塞评审，但必须披露",
        ):
            with self.subTest(readme_zh_phase=phrase):
                self.assertIn(phrase, zh_compact)
        self.assertNotIn("全新、隔离、只读的评审者", zh_compact)

        public_native_explorer_contract = (
            "For two or more qualifying independent decision-changing axes, Root concurrently dispatches one native Explorer per axis through the host's builtin `explorer` selector or an admitted namespaced custom Explorer selector",
            "Ordinary parallel tool calls are not Explorer dispatches",
        )
        for surface, text in (
            ("README.en.md", en_compact),
            ("README.md", zh_compact),
            ("skills/happycodex/references/execplan.md", ref_compact),
        ):
            for phrase in public_native_explorer_contract:
                with self.subTest(surface=surface, phrase=phrase):
                    self.assertIn(phrase, text)

        for phrase in (
            "Version 0.7.2 uses capability-proportional admission",
            "Normal users choose no mode and enter no continuation phrase",
            "Missing optional telemetry records `unverified` and reduces only the guarantee or use that depends on it",
            "Missing output identity is never optional",
            "An exposed mismatch or a missing predeclared guarantee stops",
            "Unverified Explorer or Challenger output supplies advisory leads only",
            "Executor writes remain governed by its fixed identity, exact grant, source/prestate, paths/resources, and allowed effects",
            "Exact-final can count under unverified optional telemetry only for a fresh empty-history neutral review of an unchanged candidate",
            "Unverified exact routing or technical isolation is never claimed",
        ):
            self.assertIn(phrase, en_compact)
        for phrase in (
            "0.7.2 使用 capability-proportional admission",
            "普通用户不选模式，也不输入继续口令",
            "缺失可选 telemetry 时记录 `unverified`，只降低依赖它的保证或用途",
            "缺失 output identity 永远不是可降级项",
            "暴露值不匹配，或预先声明的必需保证缺失时，必须停止",
            "未验证路由或隔离的 Explorer/Challenger 输出只能提供 advisory leads",
            "Executor 写入仍受固定身份、精确 grant、source/prestate、paths/resources 与 allowed effects 约束",
            "Exact-final 只可在全新空历史、中性 brief、candidate 不变时按可选 telemetry 未验证处理",
            "不得声称未验证的精确路由或技术隔离",
        ):
            self.assertIn(phrase, zh_compact)

        fields = (
            "Logical role", "Intended use/consequence", "Selected agent request", "Single question",
            "Requested route or config", "Fork mode", "Parallel independence",
            "Input identities", "Prompt/brief digest", "Required guarantees", "Spawn acceptance",
            "Output identity",
            "Actual agent role/name", "Effective route", "Effective permissions",
            "Runtime identity", "Phase", "Admission state", "Phase gate",
            "Terminal receipt",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(f"| {field} |", reference)
        dispatch_rows = (
            "Logical role", "Intended use/consequence", "Selected agent request", "Single question",
            "Requested route or config", "Fork mode", "Parallel independence",
            "Input identities", "Prompt/brief digest", "Required guarantees",
        )
        for field in dispatch_rows:
            row = next(line for line in reference.splitlines() if line.startswith(f"| {field} |"))
            self.assertIn("authenticated Root-owned dispatch/tool receipt", row)
        output_identity_row = next(
            line for line in reference.splitlines()
            if line.startswith("| Output identity |")
        )
        self.assertIn("host-issued dispatch/result receipt", output_identity_row)
        runtime_rows = ("Actual agent role/name", "Effective route", "Effective permissions")
        for field in runtime_rows:
            row = next(line for line in reference.splitlines() if line.startswith(f"| {field} |"))
            self.assertIn("runtime-issued session/turn metadata", row)
        runtime_identity_row = next(
            line for line in reference.splitlines()
            if line.startswith("| Runtime identity |")
        )
        self.assertIn("exposed runtime supplement or `unverified`; never substitutes for Output identity", runtime_identity_row)
        self.assertIn("runtime-issued session/turn metadata when exposed", runtime_identity_row)
        for field in ("Phase", "Admission state", "Phase gate"):
            row = next(line for line in reference.splitlines() if line.startswith(f"| {field} |"))
            self.assertIn("Root admission record", row)
        terminal_row = next(
            line for line in reference.splitlines()
            if line.startswith("| Terminal receipt |")
        )
        self.assertIn(
            "Root admission record bound to host-authenticated Output identity and terminal result, plus any exposed runtime metadata",
            terminal_row,
        )
        for phrase in (
            "Output identity | authenticated child/run/result handle; missing is a hard stop",
            "Actual agent role/name | exposed value or `unverified`; record-only",
            "Effective route | exposed model/effort, `unverified`, or mismatch",
            "Effective permissions | exposed sandbox/approval, `unverified`, or mismatch against a required isolation guarantee",
            "Missing optional telemetry never waives a required guarantee",
            "Exact routing and technical isolation claims remain withheld while their evidence is `unverified`",
            "advisory leads only until Root reproduces every material fact from source",
            "Root relies on Git, tests, and receipts rather than Executor prose",
            "Required hard isolation that is not independently established leaves review open",
            "No user-facing mode, level, or continuation phrase is part of this protocol",
        ):
            self.assertIn(phrase, ref_compact)
        self.assertNotIn("all child output is inadmissible", ref_compact)
        self.assertNotIn("unverified output remains inadmissible", ref_compact)

        for phrase in (
            "one fresh logically read-only reviewer",
            "Technical read-only isolation is a hard requirement only when predeclared",
            "receipt always binds authenticated output identity, frozen source and candidate identities, neutral brief, checks, diff and obligation coverage, terminal result, findings, and Root reproduction",
            "Record the requested and any exposed or `unverified` model, effort, and permissions",
            "Missing optional route or permission telemetry alone does not leave review open",
            "A required but unproven guarantee, missing output identity or coverage, explicit mismatch, candidate drift, unsupported evidence, or an unchanged rerun leaves review open",
        ):
            with self.subTest(final_review=phrase):
                self.assertIn(phrase, review_compact)
        for retired in (
            "one fresh isolated read-only reviewer",
            "receipt binds session, source/config, model/effort, isolation",
            "Missing coverage, loss of isolation",
        ):
            with self.subTest(retired_final_review=retired):
                self.assertNotIn(retired, review_compact)

        for phrase in (
            "one fresh logically read-only review",
            "requested route and permissions",
            "exposed values or `unverified`",
            "hard technical isolation only when predeclared required",
            "authenticated Output identity",
            "frozen source/candidate identities",
            "Missing optional route or permission telemetry alone does not leave review open",
        ):
            with self.subTest(template_final_review=phrase):
                self.assertIn(phrase, candidate_review_compact)
        self.assertNotIn("isolated read-only session", candidate_review_compact)
        self.assertNotIn("exact source/config/model/effort/permissions", candidate_review_compact)

        for row in skill_matrix:
            self.assertIn(row, routing_plan)
        self.assertIn("| Challenger | `gpt-5.6-sol` | `high` | read-only, before behavior-plan freeze |", routing_plan)
        self.assertNotIn("| Challenger | `gpt-5.6-sol` | `high` | read-only, before candidate freeze |", routing_plan)
        for phrase in (
            "## Runtime routing receipts",
            "019fd0fe-6294-7270-a204-4a68d63df579",
            "019fd0fe-81ee-79c2-896d-b2c0f87203c0",
            "unknown agent_type 'happycodex_explorer'",
            "tomli 2.4.1",
            "baseline-unchanged accepted validation limitation",
            "authenticated Root-owned dispatch/tool receipt",
            "runtime-issued session/turn metadata",
            "Root admits output only after cross-binding",
            "new-task activation deferred, not a 0.7.0 source-candidate blocker",
        ):
            self.assertIn(phrase, plan_compact)

        for normalized in (compact, ref_compact, en_compact):
            self.assertIn('sandbox_mode = "read-only"', normalized)
            self.assertIn("full-access parent", normalized)
            self.assertIn("read-only top-level or parent", normalized)
        self.assertIn('sandbox_mode = "read-only"', zh_compact)
        self.assertIn("full-access 父任务", zh_compact)
        self.assertIn("read-only 顶层或父环境", zh_compact)
        self.assertIn("插件安装不打包、安装、激活或要求自定义代理", zh_compact)
        self.assertIn("Plugin installation does not bundle, install, activate, or require custom agents", en_compact)
        self.assertIn("不代表已经发布或激活", readme_zh)
        self.assertIn("does not claim that 0.7.2 has been released or activated", en_compact)
        self.assertEqual(compact.count("普通模式继续"), 1)

    def test_review_findings_respect_frozen_envelope_and_repair_stop_line(self):
        skill = (ROOT / "skills" / "happycodex" / "SKILL.md").read_text()
        reference = (
            ROOT / "skills" / "happycodex" / "references" / "execplan.md"
        ).read_text()

        def section(raw: str, start: str, end: str) -> str:
            return raw.split(start, 1)[1].split(end, 1)[0]

        skill_contract = " ".join(
            (
                section(skill, "## Select and freeze", "## Roles and grants")
                + section(skill, "## Roles and grants", "## Event correction")
                + section(skill, "## Event correction", "## Implement and recover")
                + section(skill, "## Review and complete", "Enter `closed`")
            ).split()
        )
        reference_contract = " ".join(
            (
                section(reference, "## Contract", "## Roles and authority")
                + section(reference, "## Roles and authority", "## Obligations and evidence")
                + section(reference, "## Obligations and evidence", "## Recovery")
            ).split()
        )
        skill_recurrence = " ".join(
            (
                "After terminal GREEN"
                + section(skill, "- After terminal GREEN", "- Immediately before any effect")
            ).split()
        )
        reference_recurrence = " ".join(
            section(reference, "source tree.", "Corrections occur only").split()
        )

        common = (
            "freeze a named supported-workflow envelope before the behavior-plan freeze",
            "Findings after the behavior-plan freeze cannot manufacture obligations or write authority",
            "Root must reproduce and classify every Exact-final finding before any affected-surface expansion or write grant",
            "`in-envelope blocker` is a reproduced failure of a frozen obligation, or a candidate-new safety regression reachable through an already named supported workflow; it remains blocking",
            "`envelope expansion` is a request for a new supported workflow, trust/design guarantee, or architectural complexity not required to repair an in-envelope blocker",
            "cannot automatically become an obligation or write grant",
            "Unknown classification remains open and returns to the user before any write",
            "Unknown evidence blocks closure only when it concerns a frozen required guarantee; out-of-envelope uncertainty is disclosed rather than silently promoted",
            "A source-derived obligation may be added only when the frozen envelope requires it",
            "default automatic repair budget is exactly one Exact-final-triggered repair wave",
            "Only a Root-admitted `in-envelope blocker` may consume that automatic repair wave",
            "After refreeze, any `in-envelope blocker` or `unknown` classification remains open, truthful, and blocking",
            "`envelope expansion` remains a disclosed follow-up unless separately authorized and never consumes the automatic repair wave",
            "After the budget is exhausted, no automatic product write, refreeze, or review rerun is permitted",
            "return to the user before another product write, grant, or review rerun",
            "Exact-final identifies findings; Root owns admission and disposition",
            "cap limits automatic repair authority, never reviewer truth",
            "fresh empty-history neutral Exact-final",
            "Ask the user when continuation would change the Outcome, authority, trust boundary, or an explicitly required guarantee; expand the frozen envelope; or exceed or continue after exhaustion of the bounded automatic repair budget",
        )
        for surface, text in (("Skill", skill_contract), ("reference", reference_contract)):
            for phrase in common:
                with self.subTest(surface=surface, phrase=phrase):
                    self.assertIn(phrase, text)

        self.assertLess(
            skill_contract.index("Root must reproduce and classify every Exact-final finding"),
            skill_contract.index("Every write grant binds"),
        )
        self.assertLess(
            reference_contract.index("Root must reproduce and classify every Exact-final finding"),
            reference_contract.index("For each grant record"),
        )
        self.assertLess(
            skill_contract.index("classify the finding against the frozen envelope"),
            skill_contract.index("expand the affected-surface inventory"),
        )
        self.assertLess(
            reference_contract.index("classify the finding against the frozen envelope"),
            reference_contract.index("expand the affected-surface inventory"),
        )

        for phrase in (
            "Missing optional telemetry never asks the user to choose a fallback",
            "Missing output identity cannot downgrade",
            "explicit mismatch in a requested or required identity or route",
            "unsafe exposed value relative to a predeclared required guarantee",
            "grant/source/path/effect boundary drift",
            "candidate or source drift",
            "ambiguous or partial effects",
        ):
            with self.subTest(skill_hard_stop=phrase):
                self.assertIn(phrase, skill_contract)
        for phrase in (
            "Missing optional telemetry never waives a required guarantee",
            "Missing output identity is a hard stop",
            "Discard explicit mismatch",
            "unsafe value against a required guarantee",
            "identity/scope drift",
            "ambiguous or partial effects",
        ):
            with self.subTest(reference_hard_stop=phrase):
                self.assertIn(phrase, reference_contract)
        self.assertIn(
            "| Finding identity | Reproduced evidence | Envelope class | Disposition | Repair budget / consumed | Stop-line decision |",
            reference,
        )
        for surface, text in (("Skill", skill_contract), ("reference", reference_contract)):
            with self.subTest(surface=surface, relation="qualified_repair"):
                self.assertIn(
                    "Only a Root-admitted in-envelope repair with remaining authorized repair budget returns to `working`",
                    text,
                )
            for contradictory in (
                "A repair returns to `working`",
                "The first adverse Exact-final",
                "Any adverse or unknown finding",
            ):
                with self.subTest(surface=surface, contradictory=contradictory):
                    self.assertNotIn(contradictory, text)

        recurrence_relation = (
            "After terminal GREEN, only a Root-admitted in-envelope material "
            "recurrence may use at most one boundary-level alternative while "
            "an applicable explicit repair budget remains; using the "
            "alternative consumes that budget"
        )
        exact_final_stop = (
            "A post-refreeze Exact-final finding follows the Exact-final "
            "stop-line above and cannot use this recurrence clause to bypass "
            "return-to-user or no-more-write behavior"
        )
        for surface, local in (
            ("Skill", skill_recurrence),
            ("reference", reference_recurrence),
        ):
            with self.subTest(surface=surface, recurrence="admission_budget"):
                self.assertIn(recurrence_relation, local)
            with self.subTest(surface=surface, recurrence="exact_final_stop"):
                self.assertIn(exact_final_stop, local)
            if recurrence_relation in local and exact_final_stop in local:
                self.assertLess(local.index("Root-admitted"), local.index("boundary-level alternative"))
                self.assertLess(local.index("boundary-level alternative"), local.index("consumes that budget"))
                self.assertLess(local.index("consumes that budget"), local.index("post-refreeze Exact-final"))
            for unqualified in (
                "one material recurrence permits at most one boundary-level alternative",
                "One post-GREEN recurrence may use one boundary-level alternative",
            ):
                with self.subTest(surface=surface, unqualified=unqualified):
                    self.assertNotIn(unqualified, local)

    def test_no_active_ledger_or_retired_engine_files_exist(self):
        retired = [
            "evaluation/results/current.json", "evaluation/contracts-v7.json",
            "evaluation/live.py", "evaluation/core/ledger.py",
            "evaluation/core/receipt.py", "evaluation/semantic/replay.py",
            "evaluation/corpus/engine.py", "evaluation/holdout/engine.py",
        ]
        self.assertEqual([path for path in retired if (ROOT / path).exists()], [])

    def test_only_four_durable_record_type_literals_exist(self):
        discovered = set()
        for path in (ROOT / "evaluation").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and node.value in RECORD_TYPES:
                    discovered.add(node.value)
        self.assertEqual(discovered, set(RECORD_TYPES))

    def test_no_retired_control_plane_vocabulary_in_evaluator(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "evaluation").rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
        for retired in ("GatePlan", "GateReceipt", "EvidenceJoin", "current.json", "promotion", "reconcile", "adaptive", "public-0.2"):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, text)

    def test_fixed_host_raw_capture_has_no_legacy_verification_surface(self):
        roots = (ROOT / "evaluation", ROOT / "tests")
        sources = [
            path
            for root in roots
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        ]
        forbidden = ("pro" + "of", "ver" + "ifier")
        offenders = [
            str(path.relative_to(ROOT))
            for path in sources
            if any(token in path.name.lower() or token in path.read_text(encoding="utf-8", errors="ignore").lower() for token in forbidden)
        ]
        self.assertEqual(offenders, [])

    def test_evaluation_python_loc_is_bounded(self):
        modules = list((ROOT / "evaluation").rglob("*.py"))
        counts = {path: len(path.read_text(encoding="utf-8").splitlines()) for path in modules}
        self.assertLess(sum(counts.values()), 3600)
        self.assertTrue(all(count <= 600 for count in counts.values()), counts)

    def test_execplan_is_bounded_current_index(self):
        text = PLAN.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 3000)
        self.assertEqual(text.count("## Current checkpoint"), 1)
        self.assertNotIn("adaptive", text.lower())
        self.assertNotIn("public-0.2", text.lower())

    def test_evaluator_components_are_separate_and_nonempty(self):
        components = evaluator_components(ROOT)
        self.assertEqual(
            set(components),
            {"evaluator_bundle_sha256", "provider_component_sha256", "oracle_component_sha256", "harness_component_sha256"},
        )
        self.assertEqual(len(set(components.values())), 4)

    def test_effect_cap_is_separate_from_ex_post_token_qualification(self):
        spec = bundle()[2]

        self.assertIn("effect_cap", spec)
        self.assertEqual(
            set(spec["effect_cap"]),
            {"model_calls", "wall_milliseconds"},
        )
        self.assertIn("token_qualification", spec)
        self.assertEqual(
            set(spec["token_qualification"]),
            {"input_tokens", "output_tokens"},
        )
        self.assertNotIn("total_cap", spec)

    def test_production_inventory_excludes_conditional_mechanisms(self):
        evaluation = ROOT / "evaluation"
        manifest = json.loads((evaluation / "manifest-v1.json").read_text())
        fixtures = json.loads((evaluation / "provider-fixtures-v1.json").read_text())
        oracles = json.loads((evaluation / "hidden-oracles-v1.json").read_text())
        schemas = json.loads((evaluation / "report-schemas-v1.json").read_text())
        expected = {
            "goal-divergence", "no-commit-secret", "qualification-high-risk",
            "qualification-low-risk", "qualification-midflight",
        }
        self.assertEqual(set(manifest["core_roles"]), expected)
        self.assertEqual(set(fixtures["core"]), expected)
        self.assertEqual(set(oracles["core"]), expected)
        self.assertEqual(set(schemas["core"]), expected)
        for retired in ("same-task-compaction", "no-summary-reconstruction"):
            self.assertNotIn(retired, str((manifest, fixtures, oracles, schemas)))

    def test_qualification_fixtures_define_one_activation_boundary_without_execution(self):
        fixtures = json.loads((ROOT / "evaluation" / "provider-fixtures-v1.json").read_text())["core"]
        expected_boundaries = {
            "qualification-high-risk": "pre-selection",
            "qualification-low-risk": "pre-selection",
            "qualification-midflight": "after-new-fact",
        }
        for role_id, boundary in expected_boundaries.items():
            case = fixtures[role_id]
            self.assertEqual(case["fixture"]["qualification_boundary"], boundary)
            self.assertIn("qualifies to activate or apply HappyCodex", case["prompt"])

        low = fixtures["qualification-low-risk"]
        self.assertEqual(
            {key: low["fixture"][key] for key in ("confirmed", "bounded", "read_only", "local")},
            {"confirmed": True, "bounded": True, "read_only": True, "local": True},
        )
        self.assertFalse(low["workspace"]["execution_required"])
        self.assertFalse(low["workspace"]["repository_write_requested"])
        self.assertFalse(low["workspace"]["external_effect_requested"])
        self.assertNotIn("empty workspace", json.dumps(low).lower())

    def test_holdout_decision_safe_semantics_are_provider_visible_and_oracle_blind(self):
        evaluation = ROOT / "evaluation"
        fixtures = json.loads((evaluation / "provider-fixtures-v1.json").read_text())["holdouts"]
        oracles = json.loads((evaluation / "hidden-oracles-v1.json").read_text())["holdouts"]
        prompts = {case["prompt"] for case in fixtures.values()}
        self.assertEqual(len(prompts), 1)
        prompt = next(iter(prompts))
        self.assertIn("recommended handling", prompt)
        self.assertIn("not whether the current scenario itself is safe", prompt)
        for case in fixtures.values():
            self.assertEqual(
                case["fixture"]["decision_safe_semantics"],
                "recommended-handling-safe-not-current-scenario-safe",
            )
        _, _, spec, _ = bundle()
        for unit in (item for item in spec["units"] if item["stage"] == "holdout"):
            projection = unit["invocation"]["provider_input"]
            self.assertEqual(
                projection["fixture"]["decision_safe_semantics"],
                "recommended-handling-safe-not-current-scenario-safe",
            )
            self.assertFalse({"oracle", "expected", "mapping"} & set(projection))
        provider_projection = json.dumps(fixtures, sort_keys=True)
        self.assertIn("decision_safe_semantics", provider_projection)
        for oracle in oracles.values():
            self.assertNotIn(json.dumps(oracle, sort_keys=True), provider_projection)


if __name__ == "__main__":
    unittest.main()
