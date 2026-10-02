"""All profiles, endpoints and credentials are synthetic fixture data."""

import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml


HERE = Path(__file__).parent
SCRIPT = HERE.parent / "profile_patch.py"
SPEC = importlib.util.spec_from_file_location("profile_patch", SCRIPT)
PATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCH)


class ProfilePatchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.text = (HERE / "fixtures/profile.yaml").read_text(encoding="utf-8")
        self.plan = json.loads((HERE / "fixtures/plan.json").read_text(encoding="utf-8"))
        self.profile = self.root / "profile.yaml"
        self.profile.write_text(self.text, encoding="utf-8")
        self.profile.chmod(stat.S_IRUSR | stat.S_IWUSR)
        self.plan_path = self.root / "plan.json"
        self.plan["paths"] = {
            "profile": str(self.profile), "receipt": str(self.root / "receipt.json"),
            "rollback_state": str(self.root / "rollback.json"), "lock": str(self.root / "lock")}
        self.save_plan()

    def save_plan(self):
        self.plan_path.write_text(json.dumps(self.plan), encoding="utf-8")

    def apply(self):
        PATCH.run(self.plan_path)
        return PATCH.run(self.plan_path, apply=True)

    def test_plan_does_not_change_profile_or_disclose_credentials(self):
        summary = PATCH.run(self.plan_path)
        self.assertEqual(self.profile.read_text(), self.text)
        self.assertEqual(summary["network_actions"], 0)
        self.assertEqual(summary["live_effective_state"], "not_verified")
        output = json.dumps(summary)
        original = yaml.safe_load(self.text)
        self.assertNotIn(original["proxies"][0]["password"], output)
        self.assertNotIn(original["proxy-providers"]["AirportOriginal"]["url"], output)
        self.assertFalse(Path(self.plan["paths"]["rollback_state"]).exists())

    def test_apply_preserves_source_nodes_subscription_and_other_rules(self):
        self.apply()
        changed = self.profile.read_text()
        before, before_blocks, _ = PATCH.parse_profile(self.text)
        after, after_blocks, _ = PATCH.parse_profile(changed)
        self.assertTrue(after_blocks["proxies"].startswith(before_blocks["proxies"]))
        self.assertEqual(after["proxies"][:len(before["proxies"])], before["proxies"])
        self.assertEqual(after_blocks["proxy-providers"], before_blocks["proxy-providers"])
        self.assertTrue(after_blocks["rule-providers"].startswith(before_blocks["rule-providers"]))
        self.assertEqual(after["tun"], before["tun"])
        self.assertEqual(after["mode"], before["mode"])
        self.assertEqual(after["mixed-port"], before["mixed-port"])
        self.assertEqual(after["rules"][-3:], before["rules"][-3:])
        clone = after["proxies"][-1]
        expected = {**before["proxies"][0], "name": self.plan["chain"]["node_name"],
                    "dialer-proxy": self.plan["chain"]["dialer_proxy_name"]}
        self.assertEqual(clone, expected)
        for key in ("listen", "ipv6", "fake-ip-range", "fake-ip-filter", "enhanced-mode"):
            self.assertEqual(after["dns"][key], before["dns"][key])
        automatic = PATCH.named(after["proxy-groups"])["ExistingAuto"]
        self.assertTrue(automatic["exclude-filter"].startswith("^OriginalExcluded$`"))
        self.assertIn(self.plan["chain"]["node_name"], automatic["exclude-filter"])
        self.assertEqual(stat.S_IMODE(self.profile.stat().st_mode), stat.S_IRUSR | stat.S_IWUSR)

    def test_bootstrap_route_is_independent_and_unicode_fragment_exact(self):
        self.plan["group_names"]["ai"] = "AI 海外"
        self.plan["group_names"]["direct"] = "住宅直连"
        self.plan["default_exit_name"] = self.plan["group_names"]["direct"]
        self.plan["ai_rule_provider"]["specification"]["proxy"] = self.plan["group_names"]["direct"]
        result, _, _ = PATCH.prepare(self.text, self.plan)
        data = yaml.safe_load(result)
        from urllib.parse import unquote, urlsplit
        self.assertEqual(unquote(urlsplit(data["dns"]["nameserver"][0]).fragment), self.plan["group_names"]["ai"])
        for key in ("default-nameserver", "proxy-server-nameserver"):
            self.assertEqual(unquote(urlsplit(data["dns"][key][0]).fragment), self.plan["group_names"]["direct"])
        self.assertNotIn("+", data["dns"]["nameserver"][0])

    def test_rollback_exact_bytes_without_credentials_in_state(self):
        self.apply()
        state_path = Path(self.plan["paths"]["rollback_state"])
        state = state_path.read_text()
        before = yaml.safe_load(self.text)
        self.assertNotIn(before["proxies"][0]["password"], state)
        self.assertNotIn(before["proxy-providers"]["AirportOriginal"]["url"], state)
        self.assertNotIn(before["rule-providers"]["OriginalMedia"]["url"], state)
        self.assertEqual(stat.S_IMODE(state_path.stat().st_mode), stat.S_IRUSR | stat.S_IWUSR)
        PATCH.run(self.plan_path, rollback=True)
        self.assertEqual(self.profile.read_text(), self.text)

    def test_reapply_is_idempotent(self):
        self.apply()
        applied = self.profile.read_bytes()
        summary = PATCH.run(self.plan_path, apply=True)
        self.assertEqual(summary["status"], "already_matches")
        self.assertEqual(self.profile.read_bytes(), applied)

    def test_changed_source_and_changed_plan_reject_stale_receipt(self):
        PATCH.run(self.plan_path)
        edited = self.text + "# unrelated user edit\n"
        self.profile.write_text(edited)
        with self.assertRaisesRegex(PATCH.PlanError, "review_receipt_missing_or_stale"):
            PATCH.run(self.plan_path, apply=True)
        self.assertEqual(self.profile.read_text(), edited)
        self.profile.write_text(self.text)
        self.plan["additional_ai_domain_suffixes"].append("new-ai.example.invalid")
        self.save_plan()
        with self.assertRaisesRegex(PATCH.PlanError, "review_receipt_missing_or_stale"):
            PATCH.run(self.plan_path, apply=True)

    def test_rollback_refuses_later_user_edit(self):
        self.apply()
        edited = self.profile.read_text() + "# later writer\n"
        self.profile.write_text(edited)
        with self.assertRaisesRegex(PATCH.PlanError, "rollback_profile_changed_or_wrong_target"):
            PATCH.run(self.plan_path, rollback=True)
        self.assertEqual(self.profile.read_text(), edited)

    def test_final_race_guard_preserves_other_writer(self):
        original, info = PATCH.read_regular(self.profile)
        replacement = b"replacement: true\n"
        edited = b"other_writer: true\n"
        check = PATCH.same_file

        def simulate_writer(path, content, observed):
            path.write_bytes(edited)
            check(path, content, observed)

        with mock.patch.object(PATCH, "same_file", side_effect=simulate_writer):
            with self.assertRaisesRegex(PATCH.PlanError, "concurrent_profile_change"):
                PATCH.atomic_replace(self.profile, original, info, replacement)
        self.assertEqual(self.profile.read_bytes(), edited)
        self.assertEqual(list(self.root.glob(".profile.yaml.*")), [])

    def test_numeric_bootstrap_and_proxy_cycles_rejected(self):
        domain_gateway = self.text.replace("server: 192.0.2.10", "server: gateway.example.invalid")
        with self.assertRaises(ValueError):
            PATCH.prepare(domain_gateway, self.plan)
        loop = self.text.replace("proxy: StaticGateway", "proxy: ExistingAI")
        with self.assertRaisesRegex(PATCH.PlanError, "proxy_dependency_cycle"):
            PATCH.prepare(loop, self.plan)
        self.plan["dns"]["bootstrap_doh_urls"] = self.plan["dns"]["main_doh_urls"]
        with self.assertRaises(ValueError):
            PATCH.prepare(self.text, self.plan)

    def test_dynamic_group_requires_reject_and_direct_is_forbidden(self):
        unsafe = self.text.replace("empty-fallback: REJECT", "empty-fallback: COMPATIBLE")
        with self.assertRaisesRegex(PATCH.PlanError, "dynamic_group_requires_reject"):
            PATCH.prepare(unsafe, self.plan)
        unsafe = self.text.replace("  use:\n  - AirportOriginal", "  proxies:\n  - DIRECT")
        with self.assertRaisesRegex(PATCH.PlanError, "direct_or_unqualified_ai_path"):
            PATCH.prepare(unsafe, self.plan)

    def test_no_chain_and_new_rule_provider_section_rollback(self):
        _, blocks, prefix = PATCH.parse_profile(self.text)
        blocks.pop("rule-providers")
        self.text = prefix + "".join(blocks.values())
        self.profile.write_text(self.text)
        self.plan["chain"] = None
        self.save_plan()
        summary = self.apply()
        self.assertFalse(summary["added_proxy_count"])
        PATCH.run(self.plan_path, rollback=True)
        self.assertEqual(self.profile.read_text(), self.text)

    def test_missing_authorization_mode_is_read_only_and_errors_redacted(self):
        malformed = self.text.replace("  password: SYNTHETIC_PROXY_PASSWORD", "  password: [SYNTHETIC_PROXY_PASSWORD")
        self.profile.write_text(malformed)
        process = subprocess.run([sys.executable, str(SCRIPT), str(self.plan_path)],
                                 capture_output=True, text=True, check=False)
        self.assertNotEqual(process.returncode, 0)
        self.assertNotIn("SYNTHETIC_PROXY_PASSWORD", process.stdout + process.stderr)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(self.profile.read_text(), malformed)

    def test_authenticated_dns_and_existing_chain_collision_rejected(self):
        self.plan["dns"]["main_doh_urls"] = ["https://user:password@resolver.example.invalid/dns-query"]
        with self.assertRaisesRegex(PATCH.PlanError, "public_https_url_required"):
            PATCH.prepare(self.text, self.plan)
        self.plan["dns"]["main_doh_urls"] = ["https://resolver.example.invalid/dns-query"]
        self.plan["chain"]["node_name"] = self.plan["static_node_name"]
        with self.assertRaisesRegex(PATCH.PlanError, "existing_chain_node_differs"):
            PATCH.prepare(self.text, self.plan)

    def test_lock_and_symlink_rejected(self):
        lock = Path(self.plan["paths"]["lock"])
        lock.touch()
        with self.assertRaisesRegex(PATCH.PlanError, "another_patch_or_stale_lock"):
            PATCH.run(self.plan_path)
        lock.unlink()
        link = self.root / "profile-link.yaml"
        link.symlink_to(self.profile)
        self.plan["paths"]["profile"] = str(link)
        self.save_plan()
        with self.assertRaisesRegex(PATCH.PlanError, "symlink_refused"):
            PATCH.run(self.plan_path)

    def test_plan_edit_during_lock_acquisition_is_rejected(self):
        opening = PATCH.os.open

        def changing_plan(path, *args, **kwargs):
            descriptor = opening(path, *args, **kwargs)
            if Path(path) == Path(self.plan["paths"]["lock"]):
                self.plan["paths"]["lock"] = str(self.root / "different-lock")
                self.plan["paths"]["profile"] = str(self.root / "different-profile")
                self.save_plan()
            return descriptor

        with mock.patch.object(PATCH.os, "open", side_effect=changing_plan):
            with self.assertRaisesRegex(PATCH.PlanError, "concurrent_profile_change"):
                PATCH.run(self.plan_path)
        self.assertEqual(self.profile.read_text(), self.text)
        self.assertFalse((self.root / "lock").exists())
        self.assertFalse((self.root / "different-lock").exists())

    def test_indented_outbound_and_provider_append_preserve_rollback(self):
        _, blocks, prefix = PATCH.parse_profile(self.text)
        for key in ("proxies", "rule-providers"):
            lines = blocks[key].splitlines(True)
            blocks[key] = lines[0] + "".join("  " + line for line in lines[1:])
        self.text = prefix + "".join(blocks.values())
        self.profile.write_text(self.text)
        self.apply()
        changed = yaml.safe_load(self.profile.read_text())
        self.assertEqual(changed["proxies"][-1]["name"], self.plan["chain"]["node_name"])
        PATCH.run(self.plan_path, rollback=True)
        self.assertEqual(self.profile.read_text(), self.text)

    def test_explicit_split_dns_preserved_and_public_plaintext_rejected(self):
        self.plan["dns"]["resolver_paths"]["nameserver-policy"] = {"+.lan": ["10.0.0.53"]}
        self.plan["dns"]["local_dns_policy_keys"] = ["+.lan"]
        result, _, _ = PATCH.prepare(self.text, self.plan)
        self.assertEqual(yaml.safe_load(result)["dns"]["nameserver-policy"], {"+.lan": ["10.0.0.53"]})
        self.plan["dns"]["resolver_paths"]["direct-nameserver"] = ["system"]
        with self.assertRaisesRegex(PATCH.PlanError, "unencrypted_or_implicit_resolver_refused"):
            PATCH.prepare(self.text, self.plan)
        self.plan["dns"]["resolver_paths"]["direct-nameserver"] = ["8.8.8.8"]
        with self.assertRaisesRegex(PATCH.PlanError, "plaintext_resolver_requires_scoped_local_policy"):
            PATCH.prepare(self.text, self.plan)
        self.plan["dns"]["resolver_paths"]["direct-nameserver"] = ["https://resolver.example.invalid/dns-query"]
        with self.assertRaisesRegex(PATCH.PlanError, "resolver_policy_route_must_be_explicit"):
            PATCH.prepare(self.text, self.plan)

    def test_router_fallback_and_nested_resolver_values_are_rejected(self):
        paths = self.plan["dns"]["resolver_paths"]
        paths["fallback"] = ["10.0.0.53"]
        with self.assertRaisesRegex(PATCH.PlanError, "plaintext_resolver_requires_scoped_local_policy"):
            PATCH.prepare(self.text, self.plan)
        paths["fallback"] = [{"nested": "https://resolver.example.invalid/dns-query#ExistingAI"}]
        with self.assertRaisesRegex(PATCH.PlanError, "invalid_resolver_policy_value"):
            PATCH.prepare(self.text, self.plan)
        paths["fallback"] = []
        paths["nameserver-policy"] = {"+.public-ai.example.invalid": ["10.0.0.53"]}
        with self.assertRaisesRegex(PATCH.PlanError, "plaintext_resolver_requires_scoped_local_policy"):
            PATCH.prepare(self.text, self.plan)
        paths["nameserver-policy"] = {}
        paths["proxy-server-nameserver-policy"] = {
            "hk.example.invalid": "https://resolver.example.invalid/dns-query#ExistingAI"}
        with self.assertRaisesRegex(PATCH.PlanError, "resolver_policy_route_must_be_explicit"):
            PATCH.prepare(self.text, self.plan)

    def test_requested_default_is_first_without_version_specific_group_key(self):
        self.plan["default_exit_name"] = self.plan["group_names"]["chain"]
        result, _, _ = PATCH.prepare(self.text, self.plan)
        ai = PATCH.named(yaml.safe_load(result)["proxy-groups"])[self.plan["group_names"]["ai"]]
        self.assertEqual(ai["proxies"][0], self.plan["default_exit_name"])
        self.assertNotIn("default-selected", ai)

    def test_chain_name_cannot_inject_multi_regex_delimiter(self):
        self.plan["chain"]["node_name"] = "Foo`Bar"
        with self.assertRaisesRegex(PATCH.PlanError, "unsafe_plan_name"):
            PATCH.prepare(self.text, self.plan)
        self.assertEqual(self.profile.read_text(), self.text)


if __name__ == "__main__":
    unittest.main()
