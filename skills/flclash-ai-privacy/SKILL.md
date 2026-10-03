---
name: flclash-ai-privacy
description: Plan and verify AI routing and network stability across Clash-family clients. Discover Clash, Premium or Mihomo capabilities; preserve Chinese AI DIRECT, verified foreign AI exits and ordinary routing. Includes portable rules and optional Mihomo DNS/chaining. No account-safety guarantee.
---

# Clash-family AI routing and privacy

The installed Skill name and directory remain `flclash-ai-privacy` for compatibility. The workflow now covers Clash-family clients by their actual core capabilities, including legacy Clash/Premium and modern Mihomo clients. It does not assume every client accepts one complete YAML file. Only the originating macOS FlClash v0.8.98 operation was exercised on a live device.

Use this Markdown workflow with any agent that can inspect the local machine, obtain authorization and operate its installed client. An agent without these capabilities should produce a concrete plan and instructions instead of claiming configuration success.

Keep AI traffic on user-selected, independently verified exits. Preserve other traffic's routing, airport subscription settings, LAN and split DNS. A node label containing “residential” is not evidence of residential ownership, fixedness or a supported region.

## Select a compatible recipe

Read [clash-compatibility.md](references/clash-compatibility.md) first. Identify the client, actual embedded core and version, then choose:

- **Portable baseline:** [routing-policy.portable.yaml](templates/routing-policy.portable.yaml) uses explicit groups and inline domain rules. It requires neither MRS nor RULE-SET. Reuse existing supported nodes and expand approved category lists locally when rule providers are unavailable. This is an incremental template, not a complete importable profile.
- **Verified rule-provider support:** use the installed core's documented payload format and fields, or flatten reviewed supported rules into the baseline. A `.yaml` extension does not make MRS or a domain payload into classical rules.
- **Verified Mihomo capabilities:** [routing-policy.redacted.yaml](templates/routing-policy.redacted.yaml) uses MRS. Optional `dialer-proxy`, DNS group fragments and the bundled helper each require separate capability checks; newer fields must not be silently ignored by an older parser.

Do not replace unsupported proxy protocols, install another core, migrate a subscription or recreate TUN as an implicit compatibility fix. Complete a reviewable baseline plan when an advanced feature is unavailable. Applying still requires a supported existing exit and a verified client loading method.

## How the proxy page relates to routing

In Rule mode, the first matching rule selects DIRECT, REJECT, a node or a group; a group then follows its current selection or automatic policy. The proxy page changes that group's choice. Choosing a Japanese node in an ordinary group does not override a separate foreign-AI residential group. DIRECT uses the direct outbound; “residential direct” still uses a proxy without an extra upstream.

Confirm the parent groups, live connection rule/chain and mode. Global mode bypasses normal domain splitting; Direct mode does not implement this policy. Delay cards test a configured probe URL through a candidate, rather than proving the route or quality of an AI request. Changing an automatic group member or pin can affect future traffic using that group, including groups that reference it.

## Claude access and the redacted routing recipe

For requests described as “Claude 防封”, separate network reachability, stable egress and account eligibility. Check Anthropic's current [supported-regions policy](https://www.anthropic.com/supported-countries) and [safeguards/appeals guidance](https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals). A residential or US exit does not establish eligibility or guarantee account safety. Do not treat a timeout, API rate limit or overload as evidence of a ban.

Read [sanitized-network-case.md](references/sanitized-network-case.md) when adapting the originating case or its Chinese-AI/ordinary-traffic split. Its latest policy is Chinese AI and mainland traffic DIRECT, foreign AI on the selected residential direct path, and ordinary overseas traffic through an existing URLTest group. HK chaining is an optional alternative, not the current selected AI path.

Both routing templates are non-importable policy fragments with reader-supplied names and settings. Merge only reviewed changes into an existing private profile; preserve its outbounds, subscriptions, rejection rules, DNS/TUN settings and terminal MATCH. The existing automatic group can contain both airport and residential candidates; selecting it does not change its membership.

The bundled helper's JSON contract does not implement this Chinese-AI priority split or ordinary URLTest changes. Do not feed the YAML fragment to it or assume that prepending a broad AI provider preserves Chinese-AI DIRECT precedence. Those changes require a separately reviewed merge and client-selection procedure.

## Workflow

1. **Discover read-only.** Identify OS, client and embedded-core versions, active profile, Rule/Global/Direct mode, selected groups, system proxy, TUN, DNS ownership, browser Secure DNS, IPv6 and long-lived connections. Read local instructions. Do not output raw profile, subscription URLs, environment variables, cookies or credentials. Read [agent-workflow.md](references/agent-workflow.md) for the detailed sequence and verification evidence.
2. **Verify the applicable source.** Use [the compatibility reference](references/clash-compatibility.md) and official documentation/source for that installed version. Record supported inline rules, protocols, provider formats, chaining, DNS fields and loading behavior. Validate a private candidate with that exact core in configuration-test mode, isolated from the running instance and its provider cache. Generic YAML parsing is insufficient: parsers can ignore unknown fields. Other clients and platforms require fresh verification.
3. **Prepare a reviewable plan.** Use reader-supplied paths, node names, group names, DNS endpoints and rule subscription settings. Existing credentials remain in the local profile and are read only by the reviewed runtime helper. Do not request secret values in chat. Read [plan-schema.md](references/plan-schema.md) when using the optional helper.
4. **Apply within human authorization.** Existing explicit authorization for the same target and scope remains valid. Use the client's durable local/merge/override mechanism so subscription refresh does not erase the patch. The Mihomo helper defaults to a plan; `--apply` only changes the source file. Load through the verified client workflow and verify effective output rather than only the source. If the client can only stop/restart its core, recreate TUN or terminate connections, leave loading pending when uninterrupted connectivity was requested.
5. **Test fresh connections.** Verify the selected AI path, Chinese AI exceptions when requested, unrelated routing and automatic-group membership. Compare an optional direct/HK alternative only within the authorized scope. Check DNS, browser WebRTC, IPv6, rule-provider loading and subscription update persistence when relevant; report untested layers as unknown. Existing streams can retain their old path; do not close them without authorization.
6. **Report or roll back honestly.** A valid YAML file is not a live test. Keep intermittent errors, airport nodes that fail classification, browser UDP mismatches and unsupported platform behavior visible. Roll back only changes owned by this operation and reload through the same verified client procedure.

## Essential invariants

- The portable baseline leaves DNS ownership/settings intact. For the optional Mihomo DNS recipe, the independent bootstrap route is a numeric gateway node without a dialer. Main DNS can follow the AI group; bootstrap and proxy-hostname DNS must not depend on the HK/provider route they are needed to resolve.
- The optional Mihomo chain clones the existing static node locally and adds verified `dialer-proxy`. A legacy `relay` group is a separate, version/protocol-specific recipe; it is not a universal equivalent and must not be emitted for a core that has removed it. Confirm gateway authorization and final egress; a gateway's server address can differ from its public exit.
- Use explicit nonempty, verified AI/HK candidates on the baseline. Dynamic membership is allowed only with proven failure behavior; on compatible Mihomo versions use `empty-fallback: REJECT`. If the core cannot guarantee rejection when the group empties, keep explicit members. Do not use DIRECT/COMPATIBLE as an automatic escape path.
- Put narrowly selected AI rules ahead of broader routing. An external rule list can be incomplete; maintain approved additional domains. Preserve unrelated rules and original airport provider URLs/refresh settings.
- When Chinese AI DIRECT is requested, put its rules before broad AI rules, and put foreign AI before broad China routing. Classify by the approved provider policy, not by TLD or an assumed server country. Preserve earlier rejection/private-network priorities and the original terminal MATCH.
- A URLTest group chooses by its documented health/latency policy. Fallback uses ordered availability, rather than URLTest's latency tolerance. Neither moves existing sessions or guarantees instant recovery. A client may display TLS/DNS/test-target errors as Timeout; inspect actual request paths before attributing failure to every node. Clear a URLTest manual pin only after verifying the client's explicit pin indicator and the user's intended automatic behavior.
- DNS encryption, fixed TCP egress, residential classification, WebRTC, IPv6 and an account's eligibility are separate conclusions. Heuristic browser scores do not predict account enforcement.
- Do not blindly reset network adapters, set every system DNS server, disable IPv6, alter time zone/language/fonts, or add unstable CDN addresses to hosts.

## Optional local helper

`scripts/profile_patch.py` is an optional **Mihomo-specific** helper, not the portable adapter. Verify all emitted features against the installed core before using it; the script does not detect the running core. Its JSON contract does not implement the Chinese-AI priority split or ordinary automatic selection. Use a separately reviewed patch for that policy.

It uses Python and PyYAML, performs no network requests and never loads or restarts a client. Its plan output contains managed names/counts, without proxy content. It preserves existing outbound nodes and airport provider blocks, can append a credential-preserving chain clone, and guards review/apply/rollback against changed source files. It deliberately refuses unsupported YAML forms rather than guessing.

Run its synthetic tests before treating it as a trusted local component:

```sh
python3 -m unittest discover -s <SKILL_DIRECTORY>/scripts/tests
python3 <SKILL_DIRECTORY>/scripts/profile_patch.py <PRIVATE_PLAN_JSON>
# After authorization for the reviewed target and scope:
python3 <SKILL_DIRECTORY>/scripts/profile_patch.py <PRIVATE_PLAN_JSON> --apply
# If necessary, and only while its produced source remains unchanged:
python3 <SKILL_DIRECTORY>/scripts/profile_patch.py <PRIVATE_PLAN_JSON> --rollback
```

Synthetic tests were run with PyYAML 6.0.3. Install PyYAML from its official package using the reader's approved package/version policy; see [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation). Keep plan, receipt and rollback state outside any public repository. No client, account or platform permissions are granted by this Skill.
