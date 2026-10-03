---
name: flclash-ai-privacy
description: Plan and verify Claude and other AI routing in FlClash, including fixed residential exits, Chinese AI direct routing, ordinary automatic selection and privacy checks. Use for network stability or account-access concerns; IP checks cannot guarantee account safety.
---

# FlClash AI privacy

Use this Markdown workflow with any agent that can inspect the local machine, obtain authorization and operate its installed client. An agent without these capabilities should produce a concrete plan and instructions instead of claiming configuration success.

Keep AI traffic on user-selected, independently verified exits. Preserve other traffic's routing, airport subscription settings, LAN and split DNS. A node label containing “residential” is not evidence of residential ownership, fixedness or a supported region.

## Claude access and the redacted routing recipe

For requests described as “Claude 防封”, separate network reachability, stable egress and account eligibility. Check Anthropic's current [supported-regions policy](https://www.anthropic.com/supported-countries) and [safeguards/appeals guidance](https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals). A residential or US exit does not establish eligibility or guarantee account safety. Do not treat a timeout, API rate limit or overload as evidence of a ban.

Read [sanitized-network-case.md](references/sanitized-network-case.md) when adapting the originating case or its Chinese-AI/ordinary-traffic split. Its latest policy is Chinese AI and mainland traffic DIRECT, foreign AI on the selected residential direct path, and ordinary overseas traffic through an existing URLTest group. HK chaining is an optional alternative, not the current selected AI path.

[routing-policy.redacted.yaml](templates/routing-policy.redacted.yaml) is a non-importable policy fragment with reader-supplied names and settings. Merge only reviewed changes into an existing private profile; preserve its outbounds, subscriptions, rejection rules, DNS/TUN settings and terminal MATCH. The existing automatic group can contain both airport and residential candidates; selecting it does not change its membership.

The bundled helper's JSON contract does not implement this Chinese-AI priority split or ordinary URLTest changes. Do not feed the YAML fragment to it or assume that prepending a broad AI provider preserves Chinese-AI DIRECT precedence. Those changes require a separately reviewed merge and client-selection procedure.

## Workflow

1. **Discover read-only.** Identify OS, FlClash version, Mihomo version, active profile, selected groups, system proxy, TUN, DNS ownership, browser Secure DNS, IPv6 and long-lived connections. Read local instructions. Do not output raw profile, subscription URLs, environment variables, cookies or credentials. Read [agent-workflow.md](references/agent-workflow.md) for the detailed sequence and verification evidence.
2. **Verify the applicable source.** Check official documentation/source for that installed version, especially `dialer-proxy`, DNS URL fragments, provider paths, empty-group behavior and hot loading. macOS FlClash v0.8.98 was exercised in the originating case. Other versions, Windows and Linux loading procedures require fresh verification.
3. **Prepare a reviewable plan.** Use reader-supplied paths, node names, group names, DNS endpoints and rule subscription settings. Existing credentials remain in the local profile and are read only by the reviewed runtime helper. Do not request secret values in chat. Read [plan-schema.md](references/plan-schema.md) when using the optional helper.
4. **Apply within human authorization.** Existing explicit authorization for the same target and scope remains valid. The helper defaults to a plan; `--apply` only changes the source file. Load it through the verified client workflow. If the client can only stop/restart its core, recreate TUN or terminate connections, leave loading pending when uninterrupted connectivity was requested.
5. **Test fresh connections.** Verify the selected AI path, Chinese AI exceptions when requested, unrelated routing and automatic-group membership. Compare an optional direct/HK alternative only within the authorized scope. Check DNS, browser WebRTC, IPv6, rule-provider loading and subscription update persistence when relevant; report untested layers as unknown. Existing streams can retain their old path; do not close them without authorization.
6. **Report or roll back honestly.** A valid YAML file is not a live test. Keep intermittent errors, airport nodes that fail classification, browser UDP mismatches and unsupported platform behavior visible. Roll back only changes owned by this operation and reload through the same verified client procedure.

## Essential invariants

- The independent bootstrap route is a numeric gateway node without a dialer. Main DNS can follow the AI group; bootstrap and proxy-hostname DNS must not depend on the HK/provider route they are needed to resolve.
- An optional chain clones the existing static node locally and adds `dialer-proxy` to a verified HK node/group. Confirm gateway authorization and final egress; a gateway's server address can differ from its public exit.
- Dynamic groups on an AI/HK path require `empty-fallback: REJECT` and qualified membership. Do not use DIRECT/COMPATIBLE as an automatic escape path.
- Put narrowly selected AI rules ahead of broader routing. An external rule list can be incomplete; maintain approved additional domains. Preserve unrelated rules and original airport provider URLs/refresh settings.
- When Chinese AI DIRECT is requested, put its rules before broad AI rules, and put foreign AI before broad China routing. Classify by the approved provider policy, not by TLD or an assumed server country. Preserve earlier rejection/private-network priorities and the original terminal MATCH.
- A URLTest group can choose another candidate after health checks mark one unavailable. It does not move existing sessions or guarantee instant recovery. FlClash may display TLS/DNS/test-target errors as Timeout; inspect actual request paths before attributing failure to every node. Clear a URLTest manual pin only after verifying the client's explicit pin indicator and the user's intended automatic behavior.
- DNS encryption, fixed TCP egress, residential classification, WebRTC, IPv6 and an account's eligibility are separate conclusions. Heuristic browser scores do not predict account enforcement.
- Do not blindly reset network adapters, set every system DNS server, disable IPv6, alter time zone/language/fonts, or add unstable CDN addresses to hosts.

## Optional local helper

`scripts/profile_patch.py` uses Python and PyYAML, performs no network requests and never loads or restarts FlClash. Its plan output contains managed names/counts, without proxy content. It preserves existing outbound nodes and airport provider blocks, can append a credential-preserving chain clone, and guards review/apply/rollback against changed source files. It deliberately refuses unsupported YAML forms rather than guessing.

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
