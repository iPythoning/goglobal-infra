# Local helper contract

Use the bundled [network-plan.example.json](../templates/network-plan.example.json) as a structure template. Its angle-bracket strings are deliberately invalid until replaced locally. There are no endpoint, port, refresh or profile-path defaults in the helper.

The caller supplies a JSON object with these fields:

| Field | Contract |
| --- | --- |
| `schema_version` | Integer `1`, the file-format protocol version. |
| `paths.profile` | Existing local, user-owned exported/source profile. Never a credential store. |
| `paths.receipt` | New private file for review hashes. Review creates it; apply checks both plan and profile still match. |
| `paths.rollback_state` | New private local state file. Apply refuses an existing file. |
| `paths.lock` | Shared lock file path for this profile, agreed by all agents. The helper creates/removes it; a pre-existing lock blocks execution. |
| `static_node_name` | An existing local outbound with a numeric server and no `dialer-proxy`. Independently verify its actual public exit and authorization. |
| `group_names.ai/direct/chain` | Reader-selected names. The AI group may replace a specifically approved existing AI group; direct/chain groups must be new or already identical. Chain name is unused when `chain` is null. |
| `default_exit_name` | One of the created direct/chain groups or an approved additional local node. Client-persisted selections may override this field; verify the live selection. |
| `chain` | Null, or `node_name` for a new clone and `dialer_proxy_name` for an existing verified HK outbound/group. Cloning does not change the source node's credentials or gateway. |
| `additional_verified_exit_names` | Existing local outbound names with independent classification/egress evidence. Subscription-only nodes must first be handled by the agent's separately reviewed provider workflow. |
| `dns.main_doh_urls` | Nonempty public HTTPS DoH endpoints without query, credentials or fragment. The helper appends the percent-encoded AI group fragment. |
| `dns.bootstrap_doh_urls` | Nonempty HTTPS DoH endpoints whose host is numeric; the helper appends the direct group's fragment. Verify numeric-host TLS support first. |
| `dns.settings` | Explicitly supply enable=true, respect-rules=true, prefer-h3=false for this supported recipe. Existing listener, fake-IP range/filter, IPv6, host behavior and TUN settings are retained. |
| `dns.resolver_paths` | Explicit fallback/direct-nameserver arrays of strings and nameserver-policy/proxy-server-nameserver-policy maps with string or nonempty string-array values. Preserve necessary LAN/VPN policies. Public HTTPS DoH requires an explicit AI/direct group fragment; proxy-host policy requires direct. System/implicit resolvers and blanket plaintext fallbacks are refused. The empty template is not permission to erase existing policies. |
| `dns.local_dns_policy_keys` | Explicit, reader-verified local domain keys present in nameserver-policy, such as the reader's LAN/corporate/VPN namespaces. Only these narrowly approved keys may use nonpublic unicast plaintext resolvers. Do not declare public AI domains or blanket selectors as local. Plaintext remains forbidden in fallback, direct-nameserver and proxy-host policies. |
| `ai_rule_provider.name/specification` | New provider name and explicit type=http, behavior=classical, format=text, public HTTPS URL, client-appropriate cache path, positive integer refresh interval and proxy equal to the direct group name. Existing provider definitions are preserved. |
| `retarget_ai_rules` | Exact existing DOMAIN, DOMAIN-SUFFIX, DOMAIN-KEYWORD or RULE-SET strings with three comma-separated fields. Only their target is replaced with the AI group. Do not supply non-AI matches. |
| `additional_ai_domain_suffixes` | Approved domain suffixes absent from the external ruleset; these and the new RULE-SET are prepended before existing rules. |

Review:

```sh
python3 <SKILL_DIRECTORY>/scripts/profile_patch.py <PRIVATE_PLAN_JSON>
```

Review output shows only managed group names, operation counts and `live_effective_state=not_verified`. The requested default exit is placed first; client-persisted selections may override it. The receipt is private hash metadata, never something to paste into chat or publish. Review refuses to overwrite an existing receipt; use a new receipt path after a source/plan change. An already matching profile needs no receipt and returns `already_matches`.

After explicit authorization for this reviewed source and scope:

```sh
python3 <SKILL_DIRECTORY>/scripts/profile_patch.py <PRIVATE_PLAN_JSON> --apply
```

The apply path writes local rollback state with owner-only permissions before atomically replacing the profile. It copies the original file's owner and mode. It does not preserve platform-specific extended attributes or ACLs; use an ordinary user-owned exported/source profile, not a protected managed system file. Modified DNS/groups/rules are normalized as YAML; existing outbound bytes and airport proxy-provider blocks remain intact. Unrelated routing entries keep their relative order and semantics. Newly cloned chain nodes are excluded from existing automatic include-all groups so they cannot unexpectedly enter non-AI routing.

Rollback:

```sh
python3 <SKILL_DIRECTORY>/scripts/profile_patch.py <PRIVATE_PLAN_JSON> --rollback
```

Rollback requires the current profile to exactly match that apply's result. It will not undo later user/client edits. State records old DNS/group/rule sections and lengths of newly appended node/provider text; it does **not** record cloned credentials, full outbound blocks or existing provider URLs. The state still contains private paths and network policy; never publish it. Existing DNS/group sections with credential-like fields or authenticated/query-bearing URLs are rejected before state is saved; unusual private annotations should be reviewed by a human.

Stop on errors. A stale lock can remain after a process crash; confirm no running patcher owns it before the user removes it. Cooperative locking plus a final byte/identity check catches many concurrent edits, but an unrelated client that ignores this lock can still write between the final check and replacement. Coordinate other writers and verify the file and live state after loading. Do not retry apply using a new receipt merely to bypass a detected change.

Supported inputs are a single UTF-8 YAML mapping with LF endings, block-style top-level collections, unique keys/names and no anchors/aliases. The helper does not migrate a client database, install a subscription, update a runtime selected-map, issue privileged commands, or claim Windows/Linux client loading has been verified. Unsupported forms require a narrowly reviewed alternative, never an unrestricted whole-profile rewrite.

Authoritative semantics to verify for the installed core: [DNS configuration](https://wiki.metacubex.one/en/config/dns/), [dialer-proxy](https://wiki.metacubex.one/en/config/proxies/dialer-proxy/), [proxy-group fields](https://wiki.metacubex.one/en/config/proxy-groups/) and the installed FlClash release's official source.
