# Agent execution and evidence

## Discovery and concrete plan

Ask for the active profile and traffic scope only when discovery cannot determine them. Use the existing user authorization and preferences. Read local instructions before opening any source file. Credential-bearing files must be consumed by a reviewed local runtime, not dumped into an agent's prompt. Expose only approved node/group names, feature states and counts.

Record OS/browser/client/core versions, profile type, provider ownership and refresh behavior. Establish which layer owns DNS: system DNS, browser Secure DNS, FlClash source DNS, a global override, and TUN interception are different controls. Identify LAN, corporate VPN and split-DNS requirements before proposing a change. Inspect ongoing connections without displaying their sensitive URLs or request headers.

Use official documentation and source corresponding to the installed version to confirm:

- Whether client “apply/overwrite” hot loads the core or recreates TUN; which action closes existing connections.
- Whether global client overrides supersede source DNS and group settings.
- How provider cache paths are rewritten, which interval unit is used and whether an imported subscription is overwritten by future refreshes.
- Whether the core accepts DNS group fragments and `empty-fallback: REJECT`.

The public recipe comes from macOS FlClash v0.8.98. Its source-driven configuration was applied while keeping core and TUN running. This is evidence about that operation, not a promise that another version or provider reload preserves every connection.

Present a concrete plan with: target source, AI rule/group changes, direct/chain choices, verified bootstrap dependency, DNS/browser change, unchanged non-AI/subscription scope, current-session effect, rollback method and validation criteria. A ready-made file is not permission to mutate unrelated network settings.

## Configuration choices

Use the user's existing numerical gateway as the independent bootstrap exit. Test the gateway separately from its public exit; a gateway can return a different public IP. Some upstreams authorize the intermediary IP, so the HK entry must reach that authorized gateway and the final HTTP egress must still match the intended static endpoint.

Keep a verified direct choice and an optional HK chain choice. Never select a node as residential based only on “US/住宅/home” in its name. Test every offered choice; a WARP, datacenter or frequently rotating exit can fail the user's intended qualification while still functioning as a proxy.

Preserve the original airport subscription's URL, refresh interval and automatic-update setting. If integrating it as an independent provider is necessary, the reviewed runtime copies its existing URL locally, without exposing the token. Confirm download routing does not depend on the same provider it must download, and qualification remains true after refresh. This provider integration is deliberately outside the bundled helper's narrow scope.

Use [ACL4SSR's AI rule list](https://github.com/ACL4SSR/ACL4SSR/blob/master/Clash/Ruleset/AI.list) if the user selects that source; record the date/revision and completeness limitations. Do not assume a subscription enumerates every overseas AI domain or that a general Google rule should send every Google service to AI. Add only approved missing AI suffixes before broader rules.

Check the resolver's numeric-host certificate support. Route main encrypted DNS explicitly through the AI group and bootstrap/proxy-hostname DNS through the independent direct group. Remove or consciously preserve every resolver path that can bypass this intended route, including client global overrides. An all-residential AI requirement does not automatically authorize routing other sites' TCP traffic through the same exit.

At the browser layer, a user can choose to disable Secure DNS so intercepted system DNS follows FlClash. A browser security policy blocking access to its settings is a real boundary: explain it and let the user use the native settings; do not work around the block via another automation surface. A confirmation is evidence of user action, not a programmatic verification.

Do not blindly clear system DNS, change Wi-Fi/router settings or disable IPv6. Test UDP and TCP DNS interception on the active interface; system resolver displays alone do not show the actual upstream path. Preserve VPN/corporate split-DNS entries and LAN names. If the requested no-disconnection condition cannot be met by verified available controls, complete the plan and report that dependent application is pending.

## Acceptance matrix

Use fresh requests and a real browser in the reader's normal profile. Public test services receive the public address and normal browser metadata; disclose that when relevant. Do not log in to an AI account or transmit keys to a leak-testing website.

| Check | Evidence and limit |
| --- | --- |
| AI routing | Domain rules and actual connection chain for several approved AI sites/APIs; observed HTTP public IP/country for each direct and HK choice. Test the actual hostname, not just a generic IP site that can follow another rule. |
| Non-AI behavior | Representative previously direct and airport-routed sites still follow the intended original groups; LAN/VPN names still resolve. |
| DNS | Extended multi-round browser test with groups stable throughout; resolver IP/ASN set, absence/presence of the unwanted ISP, UDP/TCP interception and encrypted upstream query success. Anycast DNS may appear outside the exit city or differ from HTTP IP. |
| WebRTC | Compare browser ICE candidates with expected permitted public exits, including UDP/STUN and IPv6. A candidate can use the airport path even when AI HTTPS uses a fixed exit. A failed/short STUN test cannot prove no leak. |
| IPv6 | Effective interface/core state plus fresh IPv6 HTTP and browser observations. “No IPv6 result” describes the tested conditions, not every future network. |
| Residential/fixedness | Provider evidence and independent IP/ASN classification plus observations across time. A single successful trace proves neither residential ownership nor permanence. Conflicting databases remain unresolved evidence. |
| Subscription | Providers/rules loaded, original airport settings preserved, no circular download dependency, and a refresh retains intended qualification. |
| Session continuity | Core/TUN identifiers and active connections remain where observable; old TCP streams may retain their prior route. New route choices apply to fresh connections. |
| Account status | Not assessed by IP/locale heuristics. Actual service eligibility/account enforcement is a separate question. |

For browser environment inspection, the user may select [FuckClaude](https://github.com/LinXiaoTao/FuckClaude) or [check-cc](https://github.com/yacuo/check-cc). Read their current source first. Scores are project heuristics; treat invalid IPs, unavailable STUN, truncated timeouts and unsupported APIs as unknown/false positives rather than proof. Do not change time zone, locale, fonts or fingerprints to chase a score.

Retry a failed connection only within an agreed, bounded diagnostic plan. Compare fresh TUN/system-proxy requests, controlled remote-DNS through the same trusted runtime and direct resolver query results without printing credentials. Record unresolved intermittent TLS/DNS failures; do not pin changing CDN IPs in hosts as a silent repair.

## Completion and rollback

Report source changes separately from live state. Give tested versions/time, actual exit results, resolver findings, browser UDP/IPv6 findings, subscription evidence, residual unknowns and long-lived connections that were left intact. Never claim zero disruption, total anonymity, all future AI coverage, residential qualification without evidence, or guaranteed account safety.

On failure, preserve other writers' edits. The helper's rollback only works when its complete produced source still matches. Otherwise compare the owned sections privately and make a new narrow plan; do not restore a whole old snapshot over later changes. Loading a restored source is again a client-version-specific action. Keep private state local and publish only placeholder configurations and aggregated, sanitized findings.
