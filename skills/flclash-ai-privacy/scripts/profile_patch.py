#!/usr/bin/env python3
"""Patch a local profile without operating the network or printing its content."""

import argparse
import copy
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from typing import Any
from urllib.parse import quote, unquote, urlsplit

import yaml


JsonObject = dict[str, Any]


class PlanError(Exception):
    """Only fixed, non-sensitive error codes may be exposed."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise PlanError(code)


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: UniqueLoader, node: yaml.MappingNode, deep: bool = False) -> JsonObject:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        require(isinstance(key, str) and key not in result, "duplicate_or_invalid_yaml_key")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def parse_profile(text: str) -> tuple[JsonObject, dict[str, str], str]:
    require("\r" not in text, "profile_requires_lf_line_endings")
    tokens = yaml.scan(text)
    require(not any(isinstance(t, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken))
                    for t in tokens), "yaml_anchors_require_manual_review")
    data = yaml.load(text, Loader=UniqueLoader)
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    require(isinstance(data, dict) and isinstance(root, yaml.MappingNode), "profile_not_mapping")
    starts = []
    for key, value in root.value:
        require(key.start_mark.column == 0, "top_level_requires_block_style")
        if isinstance(value, (yaml.SequenceNode, yaml.MappingNode)):
            require(not value.flow_style, "top_level_requires_block_style")
        starts.append((key.value, key.start_mark.index))
    blocks = {}
    for index, (key, start) in enumerate(starts):
        end = starts[index + 1][1] if index + 1 < len(starts) else len(text)
        blocks[key] = text[start:end]
    prefix = text[:starts[0][1]] if starts else text
    return data, blocks, prefix


def named(items: Any) -> dict[str, JsonObject]:
    require(isinstance(items, list), "expected_named_sequence")
    result = {}
    for item in items:
        require(isinstance(item, dict) and isinstance(item.get("name"), str), "invalid_named_item")
        require(item["name"] not in result, "duplicate_item_name")
        result[item["name"]] = item
    return result


def safe_name(value: Any) -> str:
    require(isinstance(value, str) and value.strip() == value and bool(value), "invalid_plan_name")
    require(not any(x in value for x in ("\n", "\r", ",", "#", "&", "://", "@", "`")), "unsafe_plan_name")
    require(value not in {"DIRECT", "COMPATIBLE", "GLOBAL", "REJECT"}, "reserved_plan_name")
    return value


def public_url(value: Any, numeric: bool = False) -> str:
    require(isinstance(value, str), "invalid_public_url")
    parts = urlsplit(value)
    require(parts.scheme == "https" and bool(parts.hostname) and not parts.username
            and not parts.password and not parts.query and not parts.fragment,
            "public_https_url_required")
    if numeric:
        ipaddress.ip_address(parts.hostname)
    return value


def reject_sensitive_state(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(not re.search(r"password|token|secret|authorization|credential", key, re.I),
                    "sensitive_rollback_section")
            reject_sensitive_state(child)
    elif isinstance(value, list):
        for child in value:
            reject_sensitive_state(child)
    elif isinstance(value, str) and "://" in value:
        parts = urlsplit(value)
        require(not parts.username and not parts.password and not parts.query,
                "sensitive_rollback_url")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render(key: str, value: Any) -> str:
    return yaml.safe_dump({key: value}, allow_unicode=True, sort_keys=False)


def append_sequence(block: str, items: list[JsonObject]) -> tuple[str, int]:
    require(block.endswith("\n"), "append_requires_final_newline")
    collection = yaml.compose(block, Loader=yaml.SafeLoader).value[0][1]
    indentation = collection.start_mark.column
    addition = "".join(" " * indentation + line for line in
                       yaml.safe_dump(items, allow_unicode=True, sort_keys=False).splitlines(True))
    return block + addition, len(addition)


def append_mapping(block: str, item: JsonObject) -> tuple[str, int]:
    require(block.endswith("\n"), "append_requires_final_newline")
    collection = yaml.compose(block, Loader=yaml.SafeLoader).value[0][1]
    indentation = collection.start_mark.column
    addition = "".join(" " * indentation + line for line in
                       yaml.safe_dump(item, allow_unicode=True, sort_keys=False).splitlines(True))
    return block + addition, len(addition)


def check_graph(data: JsonObject, start: str) -> None:
    nodes = named(data["proxies"])
    groups = named(data["proxy-groups"])
    providers = data.get("proxy-providers", {})
    active, done = set(), set()

    def visit(name: str) -> None:
        require(name not in {"DIRECT", "COMPATIBLE", "GLOBAL"}, "direct_or_unqualified_ai_path")
        if name == "REJECT" or name in done:
            return
        require(name not in active, "proxy_dependency_cycle")
        active.add(name)
        if name in nodes:
            if nodes[name].get("dialer-proxy"):
                visit(nodes[name]["dialer-proxy"])
        elif name in groups:
            group = groups[name]
            require(not group.get("include-all") and not group.get("include-all-proxies")
                    and not group.get("include-all-providers"), "unbounded_ai_group")
            children = group.get("proxies", [])
            uses = group.get("use", [])
            require(bool(children) or bool(uses), "empty_ai_group")
            if uses:
                require(group.get("empty-fallback") == "REJECT", "dynamic_group_requires_reject")
            for child in children:
                visit(child)
            for provider_name in uses:
                require(provider_name in providers, "missing_proxy_provider")
                download_proxy = providers[provider_name].get("proxy")
                if download_proxy:
                    visit(download_proxy)
        else:
            raise PlanError("unknown_proxy_reference")
        active.remove(name)
        done.add(name)

    visit(start)


def configure_managed_groups(data: JsonObject, blocks: dict[str, str],
                             plan: JsonObject) -> tuple[dict[str, JsonObject], int]:
    nodes = named(data["proxies"])
    groups = named(data["proxy-groups"])
    source_name = safe_name(plan["static_node_name"])
    require(source_name in nodes, "static_node_missing")
    source = nodes[source_name]
    require(not source.get("dialer-proxy"), "bootstrap_node_already_chained")
    ipaddress.ip_address(source["server"])
    names = plan["group_names"]
    ai, direct = safe_name(names["ai"]), safe_name(names["direct"])
    require(ai != direct and ai not in nodes and direct not in nodes, "group_name_collision")
    desired = {direct: {"name": direct, "type": "select", "proxies": [source_name]}}
    exits = [direct]
    proxy_suffix = 0
    chain = plan["chain"]
    if chain is not None:
        chain_node = safe_name(chain["node_name"])
        chain_group = safe_name(names["chain"])
        dialer = safe_name(chain["dialer_proxy_name"])
        require(chain_group not in {ai, direct} and chain_group not in nodes
                and chain_node not in groups and chain_node not in {ai, direct, chain_group},
                "chain_name_collision")
        clone = copy.deepcopy(source)
        clone["name"], clone["dialer-proxy"] = chain_node, dialer
        if chain_node in nodes:
            require(nodes[chain_node] == clone, "existing_chain_node_differs")
        else:
            blocks["proxies"], proxy_suffix = append_sequence(blocks["proxies"], [clone])
            data["proxies"].append(clone)
        desired[chain_group] = {"name": chain_group, "type": "select", "proxies": [chain_node]}
        exits.append(chain_group)
    for exit_name in plan["additional_verified_exit_names"]:
        exit_name = safe_name(exit_name)
        require(exit_name in nodes and exit_name not in exits, "extra_exit_requires_local_verified_node")
        exits.append(exit_name)
    require(plan["default_exit_name"] in exits, "default_exit_not_verified")
    exits = [plan["default_exit_name"]] + [name for name in exits if name != plan["default_exit_name"]]
    desired[ai] = {"name": ai, "type": "select", "proxies": exits}
    for name, group in desired.items():
        if name != ai and name in groups:
            require(groups[name] == group, "existing_managed_group_differs")
    return desired, proxy_suffix


def configure_groups(data: JsonObject, desired: dict[str, JsonObject],
                     chain: JsonObject | None) -> list[JsonObject]:
    groups = named(data["proxy-groups"])
    updated_groups = []
    for group in data["proxy-groups"]:
        updated = copy.deepcopy(desired.get(group["name"], group))
        if chain is not None and group["name"] not in desired and (
                group.get("include-all") or group.get("include-all-proxies")):
            exclusion = "^" + re.escape(chain["node_name"]) + "$"
            existing = group.get("exclude-filter", "")
            if exclusion not in existing.split("`"):
                updated["exclude-filter"] = existing + "`" + exclusion if existing else exclusion
        updated_groups.append(updated)
    updated_groups.extend(group for name, group in desired.items() if name not in groups)
    return updated_groups


def validate_resolver(value: Any, allowed_groups: set[str], local_plaintext: bool) -> None:
    require(isinstance(value, str), "invalid_resolver_policy_value")
    if "://" in value:
        parts = urlsplit(value)
        public_url(parts._replace(fragment="").geturl())
        require(unquote(parts.fragment) in allowed_groups, "resolver_policy_route_must_be_explicit")
    else:
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            raise PlanError("unencrypted_or_implicit_resolver_refused") from None
        require(local_plaintext, "plaintext_resolver_requires_scoped_local_policy")
        require(not address.is_global and not address.is_loopback and not address.is_unspecified
                and not address.is_multicast, "public_or_loopback_plaintext_resolver_refused")


def configure_resolver_paths(dns_plan: JsonObject, ai: str, direct: str) -> JsonObject:
    paths = dns_plan["resolver_paths"]
    require(set(paths) == {"fallback", "nameserver-policy", "direct-nameserver",
                           "proxy-server-nameserver-policy"}, "explicit_resolver_paths_required")
    local_keys = dns_plan["local_dns_policy_keys"]
    require(isinstance(local_keys, list) and all(isinstance(key, str) and
            re.fullmatch(r"(?:\+\.)?[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*", key)
            for key in local_keys), "local_dns_policy_keys_invalid")
    for key, value in paths.items():
        expected_type = dict if key.endswith("policy") else list
        require(isinstance(value, expected_type), "invalid_resolver_path_type")
        allowed = {direct} if key == "proxy-server-nameserver-policy" else {ai, direct}
        if isinstance(value, dict):
            for policy_key, resolvers in value.items():
                require(isinstance(policy_key, str), "invalid_resolver_policy_key")
                values = resolvers if isinstance(resolvers, list) else [resolvers]
                require(bool(values), "empty_resolver_policy_value")
                for resolver in values:
                    local = key == "nameserver-policy" and policy_key in local_keys
                    validate_resolver(resolver, allowed, local)
        else:
            for resolver in value:
                validate_resolver(resolver, allowed, False)
    require(all(key in paths["nameserver-policy"] for key in local_keys), "local_dns_policy_key_missing")
    return copy.deepcopy(paths)


def configure_dns(data: JsonObject, plan: JsonObject, ai: str, direct: str) -> JsonObject:
    dns_plan = plan["dns"]
    main_urls = dns_plan["main_doh_urls"]
    bootstrap_urls = dns_plan["bootstrap_doh_urls"]
    require(bool(main_urls) and bool(bootstrap_urls), "doh_urls_missing")
    settings = dns_plan["settings"]
    require(settings == {"enable": True, "respect-rules": True, "prefer-h3": False},
            "dns_settings_require_enabled_rule_routing_without_h3")
    updated_dns = copy.deepcopy(data["dns"])
    updated_dns.update(settings)
    updated_dns["nameserver"] = [public_url(url) + "#" + quote(ai, safe="") for url in main_urls]
    bootstrap = [public_url(url, numeric=True) + "#" + quote(direct, safe="") for url in bootstrap_urls]
    updated_dns["default-nameserver"] = list(bootstrap)
    updated_dns["proxy-server-nameserver"] = list(bootstrap)
    updated_dns.update(configure_resolver_paths(dns_plan, ai, direct))
    return updated_dns


def retarget_rules(data: JsonObject, plan: JsonObject, ai: str) -> list[str]:
    updated_rules = list(data["rules"])
    require(all(isinstance(rule, str) for rule in updated_rules), "unsupported_rule_format")
    for original in plan["retarget_ai_rules"]:
        parts = original.split(",")
        require(len(parts) == 3 and parts[0] in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "RULE-SET"},
                "retarget_requires_exact_domain_rule")
        replacement = ",".join(parts[:2] + [ai])
        require(original in updated_rules or replacement in updated_rules, "retarget_rule_missing")
        updated_rules = [replacement if rule == original else rule for rule in updated_rules]
    return updated_rules


def configure_rule_provider(data: JsonObject, blocks: dict[str, str],
                            plan: JsonObject, direct: str) -> tuple[str, bool, int]:
    rule_provider = plan["ai_rule_provider"]
    provider_name = safe_name(rule_provider["name"])
    specification = rule_provider["specification"]
    require(set(specification) == {"type", "behavior", "format", "url", "path", "interval", "proxy"},
            "rule_provider_fields_invalid")
    require(specification["type"] == "http" and specification["behavior"] == "classical"
            and specification["format"] == "text" and specification["proxy"] == direct,
            "rule_provider_type_or_route_invalid")
    public_url(specification["url"])
    require(isinstance(specification["interval"], int) and not isinstance(specification["interval"], bool)
            and specification["interval"] > 0 and isinstance(specification["path"], str)
            and bool(specification["path"]), "rule_provider_interval_or_path_invalid")
    rule_providers = data.get("rule-providers", {})
    provider_suffix = 0
    provider_added = provider_name not in rule_providers
    if provider_added:
        if "rule-providers" in blocks:
            blocks["rule-providers"], provider_suffix = append_mapping(
                blocks["rule-providers"], {provider_name: specification})
        else:
            blocks["rule-providers"] = render("rule-providers", {provider_name: specification})
    else:
        require(rule_providers[provider_name] == specification, "existing_ai_rule_provider_differs")
    return provider_name, provider_added, provider_suffix


def prioritize_rules(updated_rules: list[str], plan: JsonObject,
                     provider_name: str, ai: str) -> tuple[list[str], int]:
    priority_rules = ["RULE-SET," + provider_name + "," + ai]
    for domain in plan["additional_ai_domain_suffixes"]:
        require(isinstance(domain, str) and re.fullmatch(r"[a-zA-Z0-9.-]+", domain)
                and "." in domain and not domain.startswith("."), "invalid_ai_domain_suffix")
        priority_rules.append("DOMAIN-SUFFIX," + domain + "," + ai)
    updated_rules = list(dict.fromkeys(priority_rules)) + [rule for rule in updated_rules if rule not in priority_rules]
    return updated_rules, len(priority_rules)


def validate_preservation(result: str, baseline: JsonObject) -> None:
    validated, _, _ = parse_profile(result)
    require(validated["proxies"][:len(baseline["proxies"])] == baseline["proxies"], "existing_nodes_changed")
    require(validated.get("proxy-providers") == baseline.get("proxy-providers"), "airport_subscription_changed")
    for key, value in baseline.items():
        if key not in {"proxies", "proxy-groups", "rules", "dns", "rule-providers"}:
            require(validated[key] == value, "unrelated_section_changed")


def prepare(text: str, plan: JsonObject) -> tuple[str, JsonObject, JsonObject]:
    require(plan.get("schema_version") == 1, "unsupported_plan_version")
    data, blocks, prefix = parse_profile(text)
    for key in ("proxies", "proxy-groups", "rules", "dns"):
        require(key in data, "required_profile_section_missing")
    baseline = copy.deepcopy(data)
    desired, proxy_suffix = configure_managed_groups(data, blocks, plan)
    updated_groups = configure_groups(data, desired, plan["chain"])
    data["proxy-groups"] = updated_groups
    ai, direct = plan["group_names"]["ai"], plan["group_names"]["direct"]
    check_graph(data, ai)
    check_graph(data, direct)
    updated_dns = configure_dns(data, plan, ai, direct)
    provider_name, provider_added, provider_suffix = configure_rule_provider(data, blocks, plan, direct)
    updated_rules, priority_count = prioritize_rules(retarget_rules(data, plan, ai), plan, provider_name, ai)
    originals = {}
    for key, updated in (("dns", updated_dns), ("proxy-groups", updated_groups), ("rules", updated_rules)):
        if baseline[key] != updated:
            reject_sensitive_state(baseline[key])
            originals[key] = blocks[key]
            blocks[key] = render(key, updated)
    result = prefix + "".join(blocks.values())
    validate_preservation(result, baseline)
    summary = {"status": "review", "changed": result != text,
               "managed_group_names": list(desired), "added_proxy_count": bool(proxy_suffix),
               "ai_rule_provider_added": provider_added, "priority_rule_count": priority_count,
               "retarget_rule_count": len(plan["retarget_ai_rules"]),
               "network_actions": 0, "live_effective_state": "not_verified"}
    inverse = {"before_sections": originals, "proxy_suffix_chars": proxy_suffix,
               "rule_provider_suffix_chars": provider_suffix,
               "rule_provider_section_created": provider_added and "rule-providers" not in data}
    return result, summary, inverse


def read_regular(path: Path) -> tuple[bytes, os.stat_result]:
    require(not path.is_symlink(), "symlink_refused")
    with path.open("rb") as handle:
        info = os.fstat(handle.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "regular_unlinked_file_required")
        content = handle.read()
    return content, info


def configured_path(value: str) -> Path:
    path = Path(value).expanduser().absolute()
    require(not path.is_symlink(), "symlink_refused")
    return path.resolve()


def same_file(path: Path, content: bytes, info: os.stat_result) -> None:
    current, observed = read_regular(path)
    require(current == content and (observed.st_dev, observed.st_ino, observed.st_mtime_ns,
                                   observed.st_size, observed.st_mode, observed.st_uid,
                                   observed.st_gid, observed.st_ctime_ns) ==
            (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size, info.st_mode,
             info.st_uid, info.st_gid, info.st_ctime_ns),
            "concurrent_profile_change")


def private_json(path: Path, value: JsonObject) -> None:
    require(not path.exists() and not path.is_symlink(), "private_state_path_already_exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())


def atomic_replace(path: Path, original: bytes, info: os.stat_result, replacement: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        os.fchmod(fd, stat.S_IMODE(info.st_mode))
        if hasattr(os, "fchown"):
            os.fchown(fd, info.st_uid, info.st_gid)
        with os.fdopen(fd, "wb") as handle:
            fd = None
            handle.write(replacement)
            handle.flush()
            os.fsync(handle.fileno())
        same_file(path, original, info)
        os.replace(temporary, path)
    finally:
        if fd is not None:
            os.close(fd)
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_locked(plan_path: Path, plan_bytes: bytes, apply: bool = False,
               rollback: bool = False) -> JsonObject:
    plan = json.loads(plan_bytes)
    paths = plan["paths"]
    profile, receipt_path, state_path = (configured_path(paths[key])
                                         for key in ("profile", "receipt", "rollback_state"))
    require(len({profile, receipt_path, state_path, plan_path.resolve(),
                 Path(paths["lock"]).expanduser().resolve()}) == 5, "paths_must_be_distinct")
    original, info = read_regular(profile)
    if rollback:
        state_bytes, _ = read_regular(state_path)
        state = json.loads(state_bytes)
        require(state["profile_path"] == str(profile) and state["after_sha256"] == sha(original),
                "rollback_profile_changed_or_wrong_target")
        _, blocks, prefix = parse_profile(original.decode("utf-8"))
        blocks.update(state["before_sections"])
        for key, count in (("proxies", state["proxy_suffix_chars"]),
                           ("rule-providers", state["rule_provider_suffix_chars"])):
            if count:
                blocks[key] = blocks[key][:-count]
        if state["rule_provider_section_created"]:
            blocks.pop("rule-providers")
        restored = (prefix + "".join(blocks.values())).encode("utf-8")
        require(sha(restored) == state["before_sha256"], "rollback_inverse_mismatch")
        atomic_replace(profile, original, info, restored)
        return {"status": "rolled_back", "network_actions": 0, "live_effective_state": "not_verified"}
    result, summary, inverse = prepare(original.decode("utf-8"), plan)
    replacement = result.encode("utf-8")
    if not summary["changed"]:
        summary["status"] = "already_matches"
        return summary
    if not apply:
        private_json(receipt_path, {"profile_sha256": sha(original), "plan_sha256": sha(plan_bytes)})
        same_file(profile, original, info)
        return summary
    receipt_bytes, _ = read_regular(receipt_path)
    require(json.loads(receipt_bytes) == {"profile_sha256": sha(original), "plan_sha256": sha(plan_bytes)},
            "review_receipt_missing_or_stale")
    private_json(state_path, {**inverse, "profile_path": str(profile),
                             "before_sha256": sha(original), "after_sha256": sha(replacement)})
    atomic_replace(profile, original, info, replacement)
    summary["status"] = "source_file_updated"
    return summary


def run(plan_path: Path, apply: bool = False, rollback: bool = False) -> JsonObject:
    plan_bytes, plan_info = read_regular(plan_path)
    plan = json.loads(plan_bytes)
    lock = Path(plan["paths"]["lock"]).expanduser().absolute()
    require(not lock.is_symlink(), "lock_symlink_refused")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, stat.S_IRUSR | stat.S_IWUSR)
    except FileExistsError:
        raise PlanError("another_patch_or_stale_lock") from None
    try:
        os.close(fd)
        same_file(plan_path, plan_bytes, plan_info)
        return run_locked(plan_path, plan_bytes, apply, rollback)
    finally:
        lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Use only after human authorization")
    mode.add_argument("--rollback", action="store_true", help="Restore only this unchanged patch")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.plan, args.apply, args.rollback), ensure_ascii=False))
        return 0
    except PlanError as error:
        print(json.dumps({"status": "error", "code": str(error)}), file=sys.stderr)
    except Exception as error:
        print(json.dumps({"status": "error", "code": type(error).__name__}), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
