#!/usr/bin/env python3
"""Check the ChatGPT and Claude plugin packages against the directory rules, and build the
ChatGPT upload zip.

Usage:
  python scripts/plugin-package.py check   # exit 1 and list every problem
  python scripts/plugin-package.py zip     # check, then write dist/asoscan-chatgpt-<version>.zip

Rules verified 2026-10-03 against developers.openai.com/plugins/deploy/submission-errors and
claude.com/docs/plugins/pre-submission-checklist. Standard library only.
"""
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EM_DASH = "—"
CATEGORIES = {
    "Productivity", "Creativity", "Developer Tools", "Business & Operations", "Data & Analytics",
    "Communication", "Education & Research", "Security", "Finance", "Healthcare", "Travel",
    "Entertainment", "Other",
}
MCP_URL = "https://asoscan.com/mcp"
SYSTEM_FILES = {".DS_Store", "Thumbs.db", "desktop.ini", "__MACOSX"}
ZIP_FILES = ["plugin.json", "mcp.json", "LICENSE", "README.md", "assets/logo.png", "assets/composer-icon.png"]

errors = []


def fail(message):
    errors.append(message)


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def png_size(path):
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def text(name, value, limit, one_line=True):
    if not isinstance(value, str) or not value.strip():
        fail(f"{name}: required")
        return
    if one_line and ("\n" in value or "\r" in value):
        fail(f"{name}: must be one line")
    if len(value) > limit:
        fail(f"{name}: {len(value)} characters, limit {limit}")
    if EM_DASH in value:
        fail(f"{name}: contains an em dash")


def url(name, value):
    ok = isinstance(value, str) and value.startswith("https://") and len(value) <= 1024
    if not ok or "@" in value.split("/")[2]:
        fail(f"{name}: must be an https URL of at most 1024 characters without credentials")


def square_png(name, rel, max_bytes=5 * 1024 * 1024):
    path = ROOT / rel.removeprefix("./")
    if not path.is_file():
        fail(f"{name}: {rel} not found")
        return None
    size = png_size(path)
    if size is None:
        fail(f"{name}: {rel} is not a PNG")
        return None
    width, height = size
    if width != height or not 48 <= width <= 4096:
        fail(f"{name}: {width}x{height}, must be square, 48 to 4096 px")
    if path.stat().st_size > max_bytes:
        fail(f"{name}: {path.stat().st_size} bytes, limit {max_bytes}")
    return size


def check_openai(manifest):
    if manifest.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        fail("plugin.json: wrong $schema")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        fail("plugin.json: version must be semver")
    ui = manifest.get("extensions", {}).get("com.openai", {}).get("interface", {})
    text("displayName", ui.get("displayName"), 30)
    text("shortDescription", ui.get("shortDescription"), 30)
    text("longDescription", ui.get("longDescription"), 4000, one_line=False)
    text("developerName", ui.get("developerName"), 80)
    if ui.get("category") not in CATEGORIES:
        fail(f"category: {ui.get('category')!r} is not an allowed value")
    capabilities = ui.get("capabilities", [])
    if len(capabilities) > 20:
        fail("capabilities: more than 20")
    for i, capability in enumerate(capabilities):
        text(f"capabilities[{i}]", capability, 120)
    prompts = ui.get("defaultPrompt", [])
    if len(prompts) > 3:
        fail("defaultPrompt: more than 3")
    for i, prompt in enumerate(prompts):
        text(f"defaultPrompt[{i}]", prompt, 128)
        if "@" in prompt:
            fail(f"defaultPrompt[{i}]: no @mentions")
    if len({p.casefold() for p in prompts}) != len(prompts):
        fail("defaultPrompt: entries must be unique")
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        url(key, ui.get(key))
    square_png("logo", ui.get("logo", ""))
    composer = square_png("composerIcon", ui.get("composerIcon", ""), max_bytes=5 * 1024)
    if composer and composer != (64, 64):
        fail("composerIcon: keep it 64x64 (spec 7: also meet the older 64x64 under 5 KB rule)")
    if not all(isinstance(k, str) and k.strip() for k in manifest.get("keywords", [])):
        fail("keywords: every entry must be a non-empty string")
    return ui


def check_mcp():
    expected = {"type": "streamable-http", "url": MCP_URL}
    if load("mcp.json").get("mcpServers", {}).get("asoscan") != expected:
        fail(f"mcp.json: mcpServers.asoscan must be {expected}")
    expected_claude = {"type": "http", "url": MCP_URL}
    if load(".mcp.json").get("mcpServers", {}).get("asoscan") != expected_claude:
        fail(f".mcp.json: mcpServers.asoscan must be {expected_claude}")


def check_claude(openai_manifest, ui):
    claude = load(".claude-plugin/plugin.json")
    for key in ("name", "version", "keywords"):
        if claude.get(key) != openai_manifest.get(key):
            fail(f".claude-plugin/plugin.json: {key} differs from plugin.json")
    if claude.get("displayName") != ui.get("displayName"):
        fail(".claude-plugin/plugin.json: displayName differs from the ChatGPT displayName")
    text("claude description", claude.get("description"), 1000)
    for key in ("homepage", "documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl"):
        url(f"claude {key}", claude.get(key))
    square_png("claude icon", claude.get("icon", ""))
    if not claude.get("author", {}).get("name"):
        fail(".claude-plugin/plugin.json: author.name required")
    market = load(".claude-plugin/marketplace.json")
    entries = market.get("plugins", [])
    if len(entries) != 1 or entries[0].get("name") != claude.get("name") or entries[0].get("source") != "./":
        fail("marketplace.json: exactly one entry, same name as plugin.json, source './'")
    if not market.get("owner", {}).get("name"):
        fail("marketplace.json: owner.name required")
    if not market.get("metadata", {}).get("description"):
        fail("marketplace.json: metadata.description required (claude plugin validate --strict)")


def check_skills(plugin_name, version):
    count = 0
    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        count += 1
        folder = skill_md.parent.name
        match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", skill_md.read_text(encoding="utf-8"), re.S)
        if not match:
            fail(f"{folder}: no YAML front matter")
            continue
        front, body = match.groups()
        name = re.search(r"^name:\s*(\S+)\s*$", front, re.M)
        description = re.search(r"^description:\s*(.+)$", front, re.M)
        skill_version = re.search(r"^\s+version:\s*(\S+)\s*$", front, re.M)
        if not name or name.group(1) != folder:
            fail(f"{folder}: front matter name must equal the folder name")
        if not description or description.group(1).strip() in (">-", "|", ">"):
            fail(f"{folder}: description must be a single-line value")
        elif len(description.group(1).strip()) > 1024:
            fail(f"{folder}: description over 1024 characters")
        elif ": " in description.group(1) and description.group(1).strip()[0] not in "\"'":
            fail(f"{folder}: unquoted description contains ': ', which breaks YAML")
        if len(f"{plugin_name}:{folder}") > 64:
            fail(f"{folder}: plugin:skill identity over 64 characters")
        if not skill_version or skill_version.group(1) != version:
            fail(f"{folder}: metadata.version must be {version}")
        if not body.strip():
            fail(f"{folder}: empty body")
    if count != 9:
        fail(f"skills: expected 9, found {count}")


def check_repo():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    prose = re.sub(r"```.*?```", " ", readme, flags=re.S)
    if len(re.findall(r"[A-Za-z0-9][\w'-]*", prose)) < 40:
        fail("README.md: at least 40 words outside code blocks")
    if not (ROOT / "LICENSE").is_file():
        fail("LICENSE missing")
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or "dist" in path.parts:
            continue
        if path.name in SYSTEM_FILES:
            fail(f"system file: {path.relative_to(ROOT)}")
        if path.is_file() and path.stat().st_size >= 5 * 1024 * 1024:
            fail(f"file over 5 MiB: {path.relative_to(ROOT)}")


def check():
    manifest = load("plugin.json")
    ui = check_openai(manifest)
    check_mcp()
    check_claude(manifest, ui)
    check_skills(manifest.get("name", ""), manifest.get("version", ""))
    check_repo()
    return manifest


def build_zip(manifest):
    out = ROOT / "dist" / f"asoscan-chatgpt-{manifest['version']}.zip"
    out.parent.mkdir(exist_ok=True)
    files = ZIP_FILES + [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "skills").rglob("*")) if p.is_file()]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for rel in files:
            archive.write(ROOT / rel, rel)
    print(f"wrote {out.relative_to(ROOT).as_posix()} with {len(files)} files")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("check", "zip"):
        print(__doc__)
        return 2
    manifest = check()
    if errors:
        print("\n".join(f"FAIL {e}" for e in errors))
        return 1
    print("OK: ChatGPT and Claude packages pass every local check")
    if sys.argv[1] == "zip":
        build_zip(manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
