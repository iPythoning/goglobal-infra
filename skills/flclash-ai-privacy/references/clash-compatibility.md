# Clash 家族适配与验收

本 Skill 按实际内核适配，不按客户端图标推断能力。保留 `flclash-ai-privacy` 安装名与路径，避免已有安装失效。兼容工作流覆盖传统 Clash、Clash Premium、Clash.Meta/Mihomo 及其前端；这不表示同一完整配置可以导入所有版本。只有 macOS FlClash 0.8.98 的原案例有实机操作记录，其他客户端须在目标设备验证。

## 先辨认内核，再选择模板

记录客户端版本、运行内核版本/分支、配置来源与最终生效配置。优先使用客户端“关于/内核”信息；已有且获准使用的本地控制接口或内核版本命令也可确认，不为探测而打开公网控制端口。Clash.Meta 是 Mihomo 的历史名称，但旧 Meta 构建也可能缺少新字段。

| 能力层 | 传统 Clash / Premium | Clash.Meta / Mihomo | 操作选择 |
| --- | --- | --- | --- |
| 内联 `DOMAIN`、`DOMAIN-SUFFIX` 与显式 `select` | 基础适配目标；以已安装版本为准 | 基础适配目标 | 使用 [portable 模板](../templates/routing-policy.portable.yaml)，复用原支持节点；保留原终端 MATCH。 |
| `IP-CIDR` / `IP-CIDR6`、`no-resolve` | 按版本检查 | 按版本检查 | 只展开支持的规则；不假设 GeoIP 数据完整或最新。 |
| `rule-providers` / `RULE-SET` | 不视为所有 legacy 构建共有；Premium 按对应版本资料核实 | 核实 payload、behavior、format 和下载字段 | 不支持时展开为内联规则；不以改扩展名转换内容。 |
| MRS | 不作为 legacy 兼容格式 | 仅在支持的版本启用；当前文档限定 domain/ipcidr | [redacted 模板](../templates/routing-policy.redacted.yaml) 属于 Mihomo 专用。 |
| 链式代理 | 不自动发出 `dialer-proxy`；旧 relay 须单独验证 | 验证 `dialer-proxy`；v1.19.32 已拒绝 relay | 不支持时保留住宅直连路径并给出待办，不强制迁移内核。 |
| 动态 AI 组为空时拒绝 | 不假设 `empty-fallback` 可用 | 核实 `empty-fallback: REJECT` | 基础方案使用显式、非空且全体合格的候选；避免 DIRECT/COMPATIBLE 兜底。 |
| DNS 出口组片段、respect-rules 等 | 不复制 Mihomo DNS 字段 | 按版本逐项检查 | 基础方案保留原 DNS；高级 DNS 与链路分开验收。 |
| TUN 与热加载 | 客户端、内核和系统共同决定 | 同样需要现场核实 | 规则分流不要求新开 TUN。加载若重建 VPN/TUN 或重启核心，先遵守用户连续性要求。 |

Mihomo 的规则与格式定义见 [路由规则](https://wiki.metacubex.one/en/config/rules/)、[rule-provider](https://wiki.metacubex.one/en/config/rule-providers/)、[组字段](https://wiki.metacubex.one/en/config/proxy-groups/)、[DNS](https://wiki.metacubex.one/en/config/dns/)。这些现行文档不能替代 legacy Clash/Premium 的版本证据。原 Dreamacro 官方仓在本次检查不可访问，无法据此证明每个历史构建；没有可核版本资料的字段保持禁用。

Relay 移除依据为 [Mihomo 官方说明](https://wiki.metacubex.one/en/config/proxy-groups/relay/) 与 [v1.19.32 解析源码](https://github.com/MetaCubeX/mihomo/blob/v1.19.32/adapter/outboundgroup/parser.go)。可用的 dialer 链路另见 [官方 dialer-proxy 文档](https://wiki.metacubex.one/en/config/proxies/dialer-proxy/)，必须核实具体协议、传输和 UDP 能力。

## 客户端入口与持久化

下面是发现入口与适配方式，不是所有版本都可照抄的按钮步骤。各客户端加载可能影响现有连接；不承诺热加载绝无断流。

| 客户端类型 | 内核线索与配置方式 | 加载前必须核实 |
| --- | --- | --- |
| [FlClash](https://github.com/chen08209/FlClash) | 官方介绍为 Mihomo/Clash.Meta；按版本选择本地配置、自定义规则/组或覆盖机制。 | 源配置与全局覆盖优先级；具体操作是否重启核心/TUN。原案例见 [脱敏记录](sanitized-network-case.md)。 |
| [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) | 官方提供 Mihomo 与 Merge/Script 配置增强。 | 增强生成的最终配置、数组覆盖/追加顺序；不要把整个 rules 数组替换掉。 |
| [Clash Party（原 Mihomo Party）](https://github.com/mihomo-party-org/clash-party) | Mihomo GUI；使用安装版本支持的本地覆写/配置管理。 | 覆写关联到哪个订阅、更新后是否保留、内核 Stable/Alpha 的实际版本。 |
| [Clash Meta for Android](https://github.com/MetaCubeX/ClashMetaForAndroid) | 官方为 Meta Android GUI，内核含 Android 分支修改。 | 活跃配置与应用覆盖、VPN 接管范围、重新加载是否重建 VPN；不能套桌面步骤。 |
| [OpenClash](https://github.com/vernesong/OpenClash) | 当前官方为 OpenWrt Mihomo 客户端；旧安装仍须发现实际核心。 | 插件生成配置、自定义规则/覆写顺序，以及 dnsmasq、LAN、IPv6 和防火墙影响。不得直接照搬桌面 DNS/TUN 设置。 |
| [Clash Nyanpasu](https://github.com/libnyanpasu/clash-nyanpasu)及可切换内核的前端 | 以实际选中的内核为准；客户端版本不等于核心版本。 | 当前引擎、持久化覆写、最终 rules 与选择缓存。 |
| 已安装的 Clash for Windows / ClashX / ClashX Pro / Clash for Android / 原 Clash Verge 等历史前端 | 名称不能证明装的是 Clash、Premium、Meta 或第三方替换核心。 | 用本地版本证据选择基础适配；复用该版本的持久本地配置/增强方式。无法验证加载方式时交付计划，保留现有服务。 |
| 其他 Clash 兼容衍生客户端、裸核心或容器 | 有自己的解析器、入口或生成层；先验证共同规则子集。 | 配置挂载/服务所有者、最终格式、加载与回滚。容器配置保存不等于运行实例已经生效。 |

不把第三方重新打包的历史安装包当官方新版本，也不为兼容自动安装/替换核心。若衍生客户端只有自己的非 Clash 配置格式，需另做经审核的格式适配；不宣称本 YAML 可直接导入。

## 通用规则的合并方法

按用户批准政策保留以下相对次序：原前置 REJECT/安全/私网与优先例外 → 中国 AI DIRECT → 海外 AI 固定出口 → 中国大陆普通流量 DIRECT → 其他原规则 → 原来唯一 MATCH。中国 AI 按供应商政策分类，`.ai`、`intl`、`us` 都不能单独决定去向。原案例普通海外流量通过既有自动组，其成员可同时含机场与住宅节点；不擅自变为机场专用组。

完整分类仍由明确选择的规则源维护。两份模板里的显式域名只是原案例补充，不是“所有 AI/中国网站”的穷尽清单。来源选择、URL、修订/日期、刷新间隔、缓存路径和测速参数由读者明确提供。可以审阅 [MetaCubeX 规则数据](https://github.com/MetaCubeX/meta-rules-dat) 或 [ACL4SSR 规则源](https://github.com/ACL4SSR/ACL4SSR)，不只凭“最强”标签判断完整性。

旧核心缺少 provider 时，获取批准规则源的公开可读格式，在受信任本地运行时转换为静态内联快照：

1. 选择来源对应的 domain/ipcidr/classical 内容，核实 payload 格式。不要把 MRS 二进制改成 `.yaml`，也不要把源清单直接作为完整客户端配置。
2. 仅转换能准确表达的条目：普通精确域名 → `DOMAIN`；来源明确表示包含根域与子域的条目 → `DOMAIN-SUFFIX`；CIDR → 已验证的 IP 规则。为类别添加批准的目标组。通配符、正则、逻辑规则或其他未知语法不能静默放宽成后缀；无法等价转换就留待处理。
3. 保留源顺序与类别优先级，确认批准内容已覆盖所需业务域名。合并到原规则列表，而不是以分类快照替换整份规则。后续更新也须经同样审阅，静态快照没有自动刷新能力。
4. 保留所有旧节点协议与凭据、订阅设置、LAN/VPN、DNS/TUN、旧自动组成员及单个 MATCH。确认新组名唯一、引用存在且无环；海外 AI 组的每个间接候选都必须符合批准出口要求。

在 GUI 中确认 Rule 模式和父组选择：规则决定流量去哪个组，代理页面决定该组使用哪个候选。节点延迟卡测的是指定 URL，不等于 AI 业务的实际出口、吞吐或连续稳定性。URLTest 按延迟/健康策略选择；Fallback 按顺序选可用候选，不能把 URLTest 的 tolerance 当成通用 Fallback 防抖字段。参见 [URLTest](https://wiki.metacubex.one/en/config/proxy-groups/url-test/) 与 [Fallback](https://wiki.metacubex.one/en/config/proxy-groups/fallback/)。

## 每个目标客户端的验收

- 使用实际安装核心的官方配置检查方法，隔离候选文件与缓存，不启动第二个转发服务。输出只保留脱敏结果。未知 YAML 字段可能被忽略，因此解析成功之后还需核对支持证据与最终生效配置。
- 核实客户端生成层没有覆盖规则次序、目标组或选择；订阅刷新仍能保留补丁。若用户要求不中断，不以重启/VPN 重建来完成验收。
- 用新连接验证中国 AI、Claude/API、其他海外 AI、大陆网站（如 douyin.com）、普通海外网站和 LAN/VPN 的实际匹配规则/链路。通用查 IP 网站可能走另一个规则；旧 TCP/SSE/WebSocket 流仍可能保留旧路径。
- 抖动排查分开观察本地网关、DNS、已有上游和实际业务请求。记录失败阶段和连续样本；HTTP 请求总耗时不等于 RTT jitter，所有卡片 Timeout 也可能共用坏的探测目标或解析路径。不换住宅出口来制造对比证据，除非已经授权。
- DNS、WebRTC/STUN、IPv6、住宅归属/固定性与账号资格分别验收；未测明示。链式中转、TUN、udp: true 或任何拥塞控制设置都不能保证公网零抖动。

Python [helper contract](plan-schema.md) 仍仅覆盖 Mihomo 高级 DNS/链路子集，不探测核心，不实现本次中国 AI 优先/普通自动组选路。所有 Clash 家族可使用的是上述发现、局部合并与验收工作流；可用高级能力随实际内核而定。
