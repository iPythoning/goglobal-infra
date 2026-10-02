"""Build the static navigation site from its public manifest and Markdown guides."""
import argparse
import html
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

import markdown


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def within(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("manifest path outside site root")
    return path


def page_shell(config: dict[str, Any], title: str, description: str, language: str,
               path: str, body: str, structured: dict[str, Any]) -> str:
    canonical = urljoin(config["base_url"], path)
    alternates = "".join(
        f'<link rel="alternate" hreflang="{escape(a["language"])}" href="{escape(urljoin(config["base_url"], a["output"]))}">'
        for a in config["articles"]
    ) if path else ""
    data = json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c")
    style = urljoin(config["base_url"], config["stylesheet"])
    return f'''<!doctype html>
<html lang="{escape(language)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description)}">
<link rel="canonical" href="{escape(canonical)}">{alternates}
<meta property="og:type" content="{"article" if path else "website"}">
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(canonical)}"><meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{escape(style)}"><script type="application/ld+json">{data}</script>
</head><body><a class="skip" href="#content">Skip to content / 跳至正文</a>
<header><a class="brand" href="{escape(config["base_url"])}">{escape(config["name"])}</a>
<nav aria-label="Project"><a href="{escape(config["repository"])}">GitHub</a><a href="{escape(urljoin(config["repository"] + "/blob/main/", config["skill_path"]))}">Agent Skill</a><a href="{escape(config["shop_url"])}">shop.paibao.ai</a></nav></header>
<main id="content">{body}</main>
<footer><p>GoGlobal Infra · <a href="{escape(config["repository"])}">Source &amp; updates</a> · <a href="{escape(config["shop_url"])}">Related: shop.paibao.ai</a></p>
<p>Verify each layer. A fixed address alone does not prove residential access or account safety.</p></footer></body></html>'''


def rewrite_links(rendered: str, config: dict[str, Any], article: dict[str, str]) -> str:
    translations = {Path(a["source"]).name: urljoin(config["base_url"], a["output"]) for a in config["articles"]}
    source_url = urljoin(config["repository"] + "/blob/main/", article["source"])

    def replacement(match: re.Match[str]) -> str:
        target = html.unescape(match.group(1))
        if target.startswith("#") or urlsplit(target).scheme:
            return match.group(0)
        new_url = translations.get(target) or urljoin(source_url, target)
        return f'href="{escape(new_url)}"'

    return re.sub(r'href="([^"]+)"', replacement, rendered)


def build(root: Path, config: dict[str, Any]) -> None:
    parsed = urlsplit(config["base_url"])
    if parsed.scheme != "https" or not parsed.hostname or parsed.query or parsed.fragment:
        raise ValueError("invalid canonical base")
    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    links = []
    for article in config["articles"]:
        source = within(root, article["source"]).read_text(encoding="utf-8")
        rendered = markdown.markdown(source, extensions=["fenced_code", "tables", "toc"])
        rendered = rewrite_links(rendered, config, article)
        sibling = " · ".join(f'<a lang="{escape(a["language"])}" href="{escape(urljoin(config["base_url"], a["output"]))}">{escape(a["language"])}</a>' for a in config["articles"])
        body = f'<div class="breadcrumb"><a href="{escape(config["base_url"])}">GoGlobal Infra</a> / AI network privacy</div><div class="languages">{sibling}</div><article>{rendered}</article>'
        structured = {"@context": "https://schema.org", "@type": "Article", "headline": article["title"],
            "description": article["description"], "inLanguage": article["language"],
            "datePublished": config["published"], "dateModified": config["modified"],
            "author": {"@type": "Person", "name": config["author"]},
            "mainEntityOfPage": urljoin(config["base_url"], article["output"])}
        target = within(docs, article["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page_shell(config, article["title"], article["description"], article["language"], article["output"], body, structured), encoding="utf-8")
        links.append(f'<li><span class="eyebrow">{escape(article["language"])}</span><h3><a href="{escape(urljoin(config["base_url"], article["output"]))}">{escape(article["title"])}</a></h3><p>{escape(article["description"])}</p></li>')
    home = config["homepage"]
    body = f'''<section class="hero"><p class="eyebrow">FIELD GUIDES / 实践指南</p><h1>让出海基础设施<br>可以配置，也可以核验。</h1>
<p class="intro">{escape(home["intro"])}</p><p lang="en">{escape(home["english_intro"])}</p></section>
<section aria-labelledby="guides"><div class="section-head"><h2 id="guides">AI 网络出口与 DNS 隐私</h2><span>01 / NETWORK</span></div>
<ul class="cards">{"".join(links)}</ul></section>
<section class="skill"><p class="eyebrow">PORTABLE AGENT SKILL</p><h2>先审阅配置，再应用修改。</h2><p>智能体读取同一套说明，使用局部修改助手，并分别验收 AI TCP、DNS、WebRTC 和 IPv6。需要实际的本地权限；助手不会停止网络核心。</p>
<p lang="en">A tool-independent workflow with a review-first helper. Local permissions and live acceptance checks are still required.</p>
<a class="button" href="{escape(urljoin(config["repository"] + "/blob/main/", config["skill_path"]))}">Read the Skill / 阅读 Skill</a></section>
<aside class="related"><h2>相关服务</h2><p><a href="{escape(config["shop_url"])}">shop.paibao.ai</a></p></aside>'''
    structured = {"@context": "https://schema.org", "@type": "CollectionPage", "name": config["name"], "description": home["description"], "url": config["base_url"],
        "hasPart": [{"@type": "Article", "name": a["title"], "url": urljoin(config["base_url"], a["output"])} for a in config["articles"]]}
    (docs / "index.html").write_text(page_shell(config, home["title"], home["description"], "zh-CN", "", body, structured), encoding="utf-8")
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    sitemap = ET.Element(f"{{{namespace}}}urlset")
    for path in [""] + [a["output"] for a in config["articles"]]:
        entry = ET.SubElement(sitemap, f"{{{namespace}}}url")
        ET.SubElement(entry, f"{{{namespace}}}loc").text = urljoin(config["base_url"], path)
        ET.SubElement(entry, f"{{{namespace}}}lastmod").text = config["modified"]
    ET.ElementTree(sitemap).write(docs / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (docs / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {urljoin(config["base_url"], "sitemap.xml")}\n', encoding="utf-8")
    (docs / ".nojekyll").touch()
    (docs / "llms.txt").write_text(f'# {config["name"]}\n\n{home["description"]}\n\n' + "\n".join(f'- [{a["title"]}]({urljoin(config["base_url"], a["output"])})' for a in config["articles"]) + f'\n- [Agent Skill]({urljoin(config["repository"] + "/blob/main/", config["skill_path"])})\n', encoding="utf-8")
    print(json.dumps({"pages": len(config["articles"]) + 1, "base_url": config["base_url"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    manifest = Path(args.config).resolve()
    build(manifest.parent, json.loads(manifest.read_text(encoding="utf-8")))
