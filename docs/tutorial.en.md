# Your First Clash Setup: Installation, Subscriptions, YAML and Skills

[中文](tutorial.zh-CN.md) · [Project home](../README.en.md) · [Advanced troubleshooting](advanced-routing.en.md)

Start here if you have never used Clash or written a configuration file. First get one ordinary browser connection working. Then learn how different sites use different routes, and how to ask a local agent to help. The initial steps require no terminal, residential proxy or Hong Kong server.

Clash-family software handles network connections according to rules. You normally install a graphical client, such as FlClash or Clash Verge Rev. Its embedded **core** performs the forwarding. This guide demonstrates FlClash; the concepts apply across clients, but their buttons and supported fields differ.

Sources were checked on **2026-10-03**: the official latest release was 0.8.99, with key controls checked in its public source. The only device-tested case remains **macOS FlClash 0.8.98**. Newer versions and other platforms have not been device-tested here. Locate controls by names/icons rather than fixed screen coordinates. For another client, read the [compatibility reference](../skills/flclash-ai-privacy/references/clash-compatibility.md).

## 1. Download and install

### Choose the package for your device

| Device | How to identify it | Package name contains |
| --- | --- | --- |
| Apple Silicon Mac | Apple menu → About This Mac shows an Apple M-series chip | `macos-arm64.dmg` |
| Intel Mac | About This Mac shows Intel | `macos-amd64.dmg` |
| Intel/AMD Windows PC | Settings → System → About shows an x64 system | `windows-amd64-setup.exe` |
| Windows ARM PC | The same screen shows ARM64 | `windows-arm64-setup.exe` |
| Android | Match the device architecture; modern ARM phones usually use arm64-v8a | The matching APK |
| Linux | Identify distribution and processor architecture | Matching DEB, RPM or AppImage |

The official FlClash packages used for this guide do not include iPhone/iPad. An Android APK cannot be installed on an iPhone.

1. Open the [official FlClash download page](https://github.com/chen08209/FlClash/releases/latest).
2. Expand **Assets**, the release's downloadable files.
3. Select the package in the table. **Source code** is for developers, not a normal installer.
4. Wait for the download, then open it from your browser's downloads or your Downloads folder.

**Mac:** open the DMG, drag FlClash into Applications, then launch it from Applications. If macOS blocks it, confirm the official source and use the normal system prompts; do not copy commands that disable system security.

**Windows:** open the setup EXE, check that the installer is FlClash, finish installation and launch it from Start. Administrator authorization may be required. A ZIP build does not establish that helper/TUN components were installed.

**Android:** open the APK and follow your device's installation authorization. A separate VPN permission appears when starting a connection later.

**Linux:** use the distribution's package installer for DEB/RPM. For AppImage, allow execution in file properties and run it. Follow [FlClash's instructions](https://github.com/chen08209/FlClash) and [AppImage's instructions](https://docs.appimage.org/introduction/quickstart.html); an Ubuntu dependency command is not valid for every distribution.

**Checkpoint:** the app opens with Dashboard, Proxies and Profiles entries. An empty node list is normal before importing a service.

## 2. Understand nodes, providers and subscriptions

| Term | Meaning | Where you use it |
| --- | --- | --- |
| Node | Settings for one proxy connection: service address, port, protocol and authentication | A selectable entry on Proxies |
| “Airport” | Chinese community terminology for a service provider offering a set of proxies | The provider's account site, plans and usage instructions |
| Subscription URL | A private link for downloading and updating configuration | Copy from the provider and paste into the client's URL import |
| Profile / configuration | A complete set of settings, commonly a YAML file | One card on Profiles, containing nodes, groups and rules |
| Proxy group | A set of nodes or other groups with manual or automatic selection | Group tabs such as Auto Select |
| Rule / routing | A match that sends a connection to DIRECT, a node or a group | Request/connection records and the YAML rules list |
| DIRECT | Connect using the device's network without the selected proxy | Mainland China and local-network routes where requested |
| Static residential proxy | A proxy service intended to have a fixed residential exit; those properties need separate verification | Optional fixed egress for selected services |

Installing FlClash does not supply a subscription or a working proxy. Obtain a subscription or complete profile you are authorized to use. This guide does not select or endorse a provider.

Subscription links can contain access credentials. Keep them in the client or private local files, away from chat, public comments and screenshots. Treat proxy passwords the same way.

## 3. Import your subscription

### Copy the right link

1. In your provider's account site, find Subscription, Client Subscription or Usage Instructions.
2. Choose a **Clash / Clash Meta / Mihomo** format compatible with your client.
3. Use its copy-link button. The account webpage's address and another client's export format are not interchangeable with this URL.

If the provider supplies a complete `.yaml` file, use file import below.

### Paste it into FlClash

1. Open **Profiles** (配置).
2. Use **+ Add Profile** (添加配置), or the empty screen's Add Profile action.
3. Choose **URL**.
4. Paste the private subscription URL into the import dialog. In 0.8.99, an optional name is also available; use an identifiable name such as “Daily subscription”. The 0.8.98 dialog is titled “Import from URL”.
5. Choose **Submit** (提交) and wait for the download.
6. Click the new profile card to select it. With several profiles present, a new import is not necessarily active.
7. Open **Proxies** and confirm that groups or actual nodes appeared.

See the [official import implementation](https://github.com/chen08209/FlClash/blob/v0.8.99/lib/views/profiles/add.dart).

**File import:** Profiles → + → File → select the provider's complete YAML → select the resulting card. The repository's placeholder fragments are not complete importable profiles.

**Checkpoint:** a selected profile card and actual proxy members are visible. Solve import problems before adding DNS or TUN changes.

| Problem | First check |
| --- | --- |
| Download failed | Correct complete URL, working provider account page and active service; use the provider's complete file if needed |
| Invalid configuration | Correct Clash/Mihomo format; the response may instead be a login page |
| Old nodes still appear | Select the imported card on Profiles |
| Several indistinguishable cards | Give the intended profile an identifiable name in its edit screen |

## 4. Make your first browser connection

These are first-install steps. Existing users should record their state and preserve the currently selected residential connection.

### Rule mode

On **Dashboard**, find **Outbound Mode** and select **Rule**. Cards can be rearranged, so identify their labels.

- **Rule:** use routing matches for each destination. This is the mode for the policy below.
- **Global:** use the global group instead of ordinary per-site routing.
- **Direct:** connect through the device's network; this does not implement fixed proxy egress for overseas AI.

### Desktop: run the client and enable system proxy

Click the **▶ play icon** to start forwarding. It becomes a pause icon while running; some layouts also show elapsed time. Then enable **System Proxy** on Dashboard. Applications that follow the operating system's proxy setting can now use the local proxy. [Official run control](https://github.com/chen08209/FlClash/blob/v0.8.99/lib/views/dashboard/widgets/start_button.dart)

**Virtual Network Card / TUN is not required for this first browser step.** System proxy does not cover every development tool, game or UDP flow. Inspect those applications later rather than assuming browser success covers the whole device.

### Android: authorize VPN

Use the client's start control and accept Android's VPN connection prompt. Do not look for the desktop System Proxy card. Application exclusions and conflicts with other VPNs need their own checks. [Android VPN mechanism](https://developer.android.com/develop/connectivity/vpn)

### Choose an ordinary route

1. Open Proxies.
2. Locate the profile's ordinary-traffic group. Providers choose its name, such as Proxy or 节点列表; GLOBAL is not a universal ordinary-group name.
3. Open that group and inspect its members.
4. Choose its existing Auto Select / URLTest group if present, or a provider node. Clicking a card selects it for the group you are viewing.
5. If needed, use **Delay Test**; 0.8.99 may show a **⚡ icon**. A smaller number describes one probe target. Timeout means that probe did not finish successfully in time.
6. Open a familiar mainland site and a public overseas webpage such as [GitHub](https://github.com/) without logging in.

**Checkpoint:** the client is running, pages load and new requests appear in Requests/Connections. If not, check the active profile, mode, proxy/VPN authorization and selected member before changing more settings.

## 5. How the proxy page and rules work together

The order is: **a site opens a connection → the first matching rule chooses a target → if that target is a group, the group's current policy chooses its member**.

Suppose there are separate Foreign AI and Ordinary groups. Claude rules target Foreign AI; ordinary pages target Ordinary. Selecting Japan in Ordinary changes traffic using Ordinary. It does not automatically change the residential node in Foreign AI.

Tabs normally show different groups. Open the group name before checking its choice. A main group can select an automatic subgroup, which then selects the actual node.

Verify a **fresh request** in Requests/Connections: hostname, matched rule and connection chain. Existing video, download or AI streams may retain their old route. Do not close every connection merely to check a change.

## 6. Add a fixed AI exit when you need one

The latest originating policy is:

| Traffic | Intended route |
| --- | --- |
| Chinese AI, such as DeepSeek and Kimi | DIRECT |
| Ordinary mainland China sites, such as Douyin | DIRECT |
| Selected overseas AI, such as Claude | Verified fixed residential proxy, without an extra HK hop by default |
| Other overseas sites | Existing ordinary routing and automatic selection |

“Residential direct” still uses the residential proxy; it omits an additional upstream. It is different from Clash's DIRECT.

You can finish ordinary connectivity without buying a residential service. If you need that fixed exit, obtain its actual protocol and authorized connection information locally. Renaming an airport node does not establish residential service, and HTTP settings cannot be inserted into a VLESS node.

Record the existing residential node's **exact name**, including spaces and symbols. YAML references that name; authentication stays local. Classify Chinese AI according to the approved provider policy, not merely `.cn` or an assumed server country. Check the actual services, APIs and tools you use.

## 7. Learn to write a YAML change

YAML stores settings as plain text. You already imported a complete profile, so start with a local change to it rather than manually rebuilding every provider node.

### Read a group definition

```yaml
proxy-groups:
  - name: "Foreign AI"
    type: select
    proxies:
      - "My residential node"
```

`proxy-groups` introduces the group list. The dash starts one item. `name` is its label; `type: select` means manual selection. The indented `proxies` list names existing nodes or groups. Replace the example node name with the exact name in your own profile.

Use spaces, consistently indented; this example uses two spaces per level. Do not use tabs, smart quotes or a non-ASCII colon. A `#` starts a comment. Quotes keep spaces and symbols within one name.

### The three sections you need first

| Section | What it contains |
| --- | --- |
| `proxies` | Individual connection settings; preserve the provider's original entries |
| `proxy-groups` | Group membership and selection policies |
| `rules` | Destination matches and their targets |

Other provider and DNS sections can already exist. Leave them intact. The [portable template](../skills/flclash-ai-privacy/templates/routing-policy.portable.yaml) contains unresolved placeholders and is for planning, not replacing a complete subscription.

For a separately supplied **HTTP proxy**, recognize this node structure:

```yaml
proxies:
  - name: "My residential node"
    type: http
    server: "<provider-supplied-host>"
    port: <provider-supplied-port-number>
    username: "<provider-supplied-username>"
    password: "<provider-supplied-password>"
```

This is an unfilled fragment. Fill every placeholder **only in a private local editor**; the port is a number. For source-IP authorization without username/password, omit those lines according to provider instructions. Have a trusted local tool encode quotes/backslashes correctly without exposing passwords. HTTPS, SOCKS5 and VLESS require their own fields. Append the node to the existing list without a second top-level `proxies` key. Its name does not establish residential qualification. [HTTP fields](https://wiki.metacubex.one/en/config/proxies/http/)

### Before and after

Assume the complete profile already defines Auto Select and My residential node. These fragments show only the edited sections.

Before:

```yaml
proxy-groups:
  - name: "Ordinary"
    type: select
    proxies:
      - "Auto Select"
rules:
  - "MATCH,Ordinary"
```

After:

```yaml
proxy-groups:
  - name: "Ordinary"
    type: select
    proxies:
      - "Auto Select"
  - name: "Foreign AI"
    type: select
    proxies:
      - "My residential node"
rules:
  # Preserve existing earlier rejection/security/LAN/VPN priorities.
  - "DOMAIN-SUFFIX,deepseek.com,DIRECT"
  - "DOMAIN-SUFFIX,kimi.com,DIRECT"
  - "DOMAIN-SUFFIX,kimi.ai,DIRECT"
  - "DOMAIN-SUFFIX,moonshot.ai,DIRECT"
  - "DOMAIN-SUFFIX,anthropic.com,Foreign AI"
  - "DOMAIN-SUFFIX,claude.ai,Foreign AI"
  - "DOMAIN-SUFFIX,douyin.com,DIRECT"
  # Retain existing mainland and other rules here after checking order.
  - "MATCH,Ordinary"
```

A rule's comma-separated fields are match type, match content and target. DOMAIN-SUFFIX includes the root domain and its subdomains. MATCH is the final rule when none of the earlier entries match.

Chinese AI goes before broad AI matches; foreign AI goes before broad China matches. This tiny list does not cover all sites, login dependencies or AI providers. Preserve existing China classification and add approved missing domains. Do not delete the old rules and paste only these examples.

Add a group inside the one existing group list and rules inside the one existing rules list. Do not append duplicate top-level keys or duplicate group names. If your ordinary group lacks Auto Select, retain its complete original members. A referenced node must already exist.

### Edit, save and verify

The FlClash path is **profile-card menu → Edit → the Configuration row's ⋮ → Edit**. Save the inner editor, then save the outer edit screen; 0.8.99 uses a **✓ icon** with a Save tooltip. [Official edit implementation](https://github.com/chen08209/FlClash/blob/v0.8.99/lib/views/profiles/edit.dart)

1. Export a private backup: Profiles → the intended card's ⋮ → More → Export File. Full application backup is Tools → Backup and Restore → Local → Backup. Keep backup files private.
2. Edit with the client editor or a plain-text editor. Use plain text in macOS TextEdit, UTF-8 in Windows Notepad, and a `.yaml` filename rather than `.yaml.txt`.
3. Merge only the reviewed groups and rules; preserve credentials, providers, DNS and the final MATCH.
4. Check indentation, unique names, valid references and the exact core's supported fields. Correct errors before loading.
5. Load at a time when configuration reloading is acceptable. Existing connections can be affected; during an active meeting or stream, prepare the private copy without loading.
6. In Proxies select Foreign AI → the actual residential node and confirm the ordinary group's intended choice.
7. Check fresh requests for Claude, Chinese AI, Douyin and an ordinary overseas page.

Editing a URL subscription can be overwritten by updates. FlClash may offer to disable automatic updating; doing so is not preservation of subscription updates. For a durable patch, have the Skill plan the installed version's supported override/merge mechanism.

**Checkpoint:** no configuration error, expected new-request routes, working ordinary traffic and retained subscription behavior. A saved file alone is not proof of live application.

## 8. Install the Skill in your agent tool

A Skill contains instructions, references and an optional helper for a local agent such as **Codex or Claude Code**. FlClash still handles connections. The Skill supplies neither nodes nor account logins and grants no system permissions.

The main path below uses conversation, not Python. The original helper is a documented Mihomo-only advanced subset and does not automatically implement this Chinese-AI priority split or ordinary automatic selection.

### Codex: ask the installer

In a local Codex conversation, send:

> $skill-installer Install skills/flclash-ai-privacy from https://github.com/iPythoning/goglobal-infra. Install only the Skill; do not change my network. If that name already exists, show its source/version before overwriting anything. Report the actual installation location and how I invoke it next.

After completion, type `$flclash-ai-privacy` in the next message. If it is missing from the selector, try a new conversation, then follow the tool's restart instructions if necessary. Restarting Codex does not require restarting FlClash.

Current Codex documentation lists `~/.agents/skills` for user skills; an older installer can use its own location. Follow the installation report rather than installing duplicates. [Codex skills documentation](https://developers.openai.com/codex/skills/)

### Claude Code or manual download

1. Open the [repository's release downloads](https://github.com/iPythoning/goglobal-infra/releases/latest) and download `goglobal-infra-VERSION.zip`.
2. Extract it and find `skills/flclash-ai-privacy`. Keep the entire folder, including SKILL.md, references, templates and scripts.
3. Personal Claude Code skills belong at `~/.claude/skills/flclash-ai-privacy/`. Ask the running local Claude Code instance to create missing directories and copy the public folder using the message below. This avoids requiring beginners to create hidden dot-folders in Finder. Native Windows and WSL have different user directories; use the one where Claude Code runs.
4. Start a Claude Code session and type `/flclash-ai-privacy`. [Official locations and invocation](https://code.claude.com/docs/en/skills)

Installation message:

> Install the complete extracted public flclash-ai-privacy folder I identify into this user's personal skill directory; create missing folders. If that name exists, report it before overwriting. Install only these public files without reading/changing network configuration. Explain how to invoke it afterward.

If it needs the source location, select the folder in macOS Finder and press **Option + Command + C**, or use Windows Copy as path. Provide only the public Skill folder's location, not a private profile. Without local file capability, the tool must give manual steps rather than claim installation.

A browser-only chat or cloud session may not access this computer's files/apps. Such a tool can provide manual instructions, not claim it changed the local client.

**Checkpoint:** the tool identifies the loaded Skill and content. The installation name remains flclash-ai-privacy; its display title covers the Clash family.

## 9. What to say in each conversation round

Use `$flclash-ai-privacy` in Codex or `/flclash-ai-privacy` in Claude Code. Send one round at a time and read the result.

### Round 1: confirm capabilities

> $flclash-ai-privacy I am new to Clash. Confirm that you loaded this Skill and explain whether you can inspect this computer's client, configuration and fresh connections. If you cannot operate it, give me manual steps instead of claiming completion.

Expect a clear capability statement. Identify the actual device if needed; do not send passwords.

### Round 2: inspect without changes

> Read-only: identify the active profile, client/core versions, routing mode, system proxy/TUN and current group selections. Do not switch the residential node, restart the core, close connections or change DNS. Do not expose credentials, private subscription URLs or a raw profile. Explain what is confirmed and what remains untested.

Expect actual configuration/mode/group findings, not a conclusion based only on delay cards.

### Round 3: request a concrete plan

> Chinese AI and mainland sites should use DIRECT. The overseas AI I actually use should use my existing verified fixed residential node. Preserve ordinary routing, subscription updates and automatic-group membership. Prepare a private local candidate and explain the exact group/rule changes and recovery method. Do not load it yet.

Add real application names: Claude web, its API, your development tool, DeepSeek or Douyin. Node names are sufficient in chat; authentication stays local. A missing qualified exit must remain a missing requirement rather than being replaced with the fastest ordinary node.

Expect an inspectable patch, compatibility findings, reload effects and recovery steps.

### Round 4: choose when to apply

If the patch is right and a brief reconnection is acceptable:

> Apply the explained local patch. Keep FlClash running and preserve the current residential choice. Do not stop/restart the core or close all connections. I accept possible brief reconnections from configuration loading. Validate locally, load through the verified client workflow and check fresh requests.

If reloading is unacceptable now:

> Do not load now. Keep the checked private candidate and recovery steps; tell me where to resume when reloading is acceptable.

Existing authorization for the same change remains valid. If this client must restart to load, the agent must explain the limit and distinguish a source edit from live application.

### Round 5: verify outcomes

> Use fresh requests to verify my overseas AI, Chinese AI, douyin.com and ordinary overseas routing. Preserve ongoing connections. Report effective settings, actual paths, failures and untested layers separately. Do not treat a generic IP page, HTTP 401/404 or a third-party score as a complete pass.

Expect actual matched rules/groups. DNS, browser UDP/WebRTC and IPv6 are independent checks when available. Parsed YAML, reachable HTTP and a functioning account are different results.

### Later: a timeout or a new application

For a failure:

> This application suddenly timed out around this time. Inspect the current path, local network, DNS and actual request failure stage first. Do not switch my residential exit, test every node in bulk or restart networking. Give evidence and one staged diagnostic proposal.

For a new service:

> I added this AI application/domain. Check current coverage first, then prepare a local addition under our Chinese-AI DIRECT / overseas-AI fixed-exit policy. Preserve other routing and subscriptions.

## 10. Common first-time problems

| Symptom | First check |
| --- | --- |
| Installed app, no nodes | Import your authorized subscription in section 3 |
| Nodes appear, browser fails | Active profile, running state, Rule mode, proxy/VPN authorization and group choice |
| Browser works, development tool fails | Its own proxy behavior; inspect before considering TUN |
| Low delay but slow use | Actual business requests and failure stages, not one probe URL |
| Every card says Timeout | Shared probe target, DNS, access network and upstream; cards alone do not identify the cause |
| Chinese AI uses overseas proxy | Actual API hostname and Chinese-AI precedence before broad AI |
| YAML error | Spaces, punctuation, exact names, duplicate keys and groups |
| Update removed the patch | A direct subscription edit needs a durable override/merge plan |
| Agent claims success, nothing changed | Verify effective configuration and fresh requests rather than just the candidate file |

Claude eligibility follows [Anthropic's current policy](https://www.anthropic.com/supported-countries). A US address, residential label or third-party score does not guarantee account safety. Anonymous 401/404 responses may establish HTTP reachability, not authentication or model access.

## 11. Continue only when needed

You have completed the beginner path when you can identify client versus provider, import/select a profile, connect in Rule mode, explain group selection, edit a private YAML candidate and ask the Skill to inspect, prepare, apply and verify in separate rounds.

The [advanced guide](advanced-routing.en.md) preserves the historical Mihomo DNS, WebRTC, IPv6 and HK-chain investigation. Those settings need version-specific checks; chaining and TUN do not guarantee zero jitter. The [latest redacted case](../skills/flclash-ai-privacy/references/sanitized-network-case.md) records the current daily policy.

Project: [iPythoning/goglobal-infra](https://github.com/iPythoning/goglobal-infra) · [Skill](../skills/flclash-ai-privacy/SKILL.md) · Related: [shop.paibao.ai](https://shop.paibao.ai).
