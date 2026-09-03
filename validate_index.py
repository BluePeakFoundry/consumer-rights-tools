#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
CANONICAL = "https://bluepeakfoundry.github.io/consumer-rights-tools/"
REQUIRED_LINKS = {
    "https://bluepeakfoundry.github.io/sepa-direct-debit-refund-draft/",
    "https://bluepeakfoundry.github.io/rail-delay-compensation/",
    "https://bluepeakfoundry.github.io/b2b-refund-leakage-checklist/",
    "https://bluepeakfoundry.github.io/ap-duplicate-payment-sql-checks/",
    "https://bluepeakfoundry.github.io/freelance-quote-late-payment-tool/",
    "https://github.com/BluePeakFoundry/consumer-rights-tools/issues/new?template=consumer-tools-feedback.yml",
}
REQUIRED_TOOL_LINKS = {
    "https://bluepeakfoundry.github.io/sepa-direct-debit-refund-draft/",
    "https://bluepeakfoundry.github.io/rail-delay-compensation/",
    "https://bluepeakfoundry.github.io/b2b-refund-leakage-checklist/",
    "https://bluepeakfoundry.github.io/ap-duplicate-payment-sql-checks/",
    "https://bluepeakfoundry.github.io/freelance-quote-late-payment-tool/",
}
REQUIRED_EVENTS = {
    "cta:index:open-sepa",
    "cta:index:open-rail",
    "cta:index:open-b2b",
    "cta:index:open-ap-sql",
    "cta:index:open-freelance",
    "lead:consumer-tools-feedback",
}
PROHIBITED_TERMS = [
    r"\bsergi\b",
    r"\brex\b",
    r"\bagent\b",
    r"\bbot\b",
    r"\bautonomous\b",
    r"\bcycle\b",
    r"money verified",
    r"monetization matrix",
]
REMOTE_RUNTIME_RE = re.compile(
    r"<(script|img|iframe|source|video|audio)\b[^>]*src=[\"']https?://|"
    r"<link\b(?=[^>]*rel=[\"'](?:stylesheet|preload|modulepreload|icon)[\"'])[^>]*href=[\"']https?://",
    re.I,
)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.events = set()
        self.canonical = None
        self.stylesheets = []
        self.json_ld = []
        self.ids = set()
        self.skip_links = []
        self._in_json_ld = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if "id" in data:
            self.ids.add(data["id"])
        if "data-analytics-event" in data:
            self.events.add(data["data-analytics-event"])
        if tag == "a" and data.get("href"):
            self.links.add(data["href"])
            if data.get("class") == "skip-link":
                self.skip_links.append(data["href"])
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href")
        if tag == "link" and data.get("rel") == "stylesheet":
            self.stylesheets.append(data.get("href"))
        self._in_json_ld = tag == "script" and data.get("type") == "application/ld+json"

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_json_ld = False

    def handle_data(self, data):
        if self._in_json_ld:
            self.json_ld.append(data)


def fail(message):
    print(f"FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_html():
    html_path = ROOT / "index.html"
    text = html_path.read_text(encoding="utf-8")
    lowered = text.lower()
    for term in PROHIBITED_TERMS:
        if re.search(term, lowered):
            fail(f"prohibited public language: {term}")
    remote_runtime_text = re.sub(r"<script[^>]+src=['\"]https://gc\.zgo\.at/count\.js['\"][^>]*></script>", "", text, flags=re.I)
    if REMOTE_RUNTIME_RE.search(remote_runtime_text):
        fail("remote runtime resource detected")
    parser = Parser()
    parser.feed(text)
    if parser.canonical != CANONICAL:
        fail(f"canonical mismatch: {parser.canonical}")
    missing = REQUIRED_LINKS - parser.links
    if missing:
        fail(f"missing crawlable tool links: {sorted(missing)}")
    missing_events = REQUIRED_EVENTS - parser.events
    if missing_events:
        fail(f"missing analytics events: {sorted(missing_events)}")
    if parser.stylesheets != ["style.css"]:
        fail(f"unexpected stylesheet refs: {parser.stylesheets}")
    if "#tools" not in parser.skip_links or "tools" not in parser.ids:
        fail("skip link target missing")
    raw_json = "".join(parser.json_ld).strip()
    if not raw_json:
        fail("missing JSON-LD")
    payload = json.loads(raw_json)
    graph = payload.get("@graph", [])
    types = {entry.get("@type") for entry in graph if isinstance(entry, dict)}
    if not {"WebSite", "ItemList"}.issubset(types):
        fail(f"missing JSON-LD types: {types}")
    item_list = next(entry for entry in graph if entry.get("@type") == "ItemList")
    listed = {item.get("url") for item in item_list.get("itemListElement", [])}
    if REQUIRED_TOOL_LINKS - listed:
        fail("JSON-LD ItemList does not include all public tools")


def validate_robots_sitemap():
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Allow: /" not in robots or f"Sitemap: {CANONICAL}sitemap.xml" not in robots:
        fail("robots.txt missing allow or sitemap")
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = {node.text for node in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
    if CANONICAL not in locs:
        fail("sitemap missing canonical URL")


def validate_manifest():
    manifest_path = ROOT / "manifest.json"
    if not manifest_path.exists():
        fail("manifest.json missing; run build manifest step")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("money_verified_eur") != 0:
        fail("manifest money_verified_eur must be 0")
    external_actions = data.get("external_actions_performed")
    if not isinstance(external_actions, list) or "public_feedback_issue_form" not in external_actions:
        fail("manifest must record public_feedback_issue_form external action")
    included = set(data.get("included_tools", []))
    if REQUIRED_LINKS - included:
        fail("manifest missing included public tools")
    files = {entry["path"]: entry for entry in data.get("files", [])}
    required = {"index.html", "analytics.js", "style.css", "robots.txt", "sitemap.xml", "README.md", "validate_index.py", ".github/ISSUE_TEMPLATE/consumer-tools-feedback.yml"}
    if not required.issubset(files):
        fail(f"manifest missing files: {sorted(required - set(files))}")
    for rel, entry in files.items():
        path = ROOT / rel
        if path.exists() and rel != "manifest.json" and entry.get("sha256") != sha256(path):
            fail(f"manifest hash mismatch: {rel}")


def main():
    validate_html()
    validate_robots_sitemap()
    validate_manifest()
    data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    print(f"OK tools hub files={len(data.get('files', []))} links={len(data.get('included_tools', []))} money_verified_eur={data['money_verified_eur']} external_actions={len(data['external_actions_performed'])}")

if __name__ == "__main__":
    main()
