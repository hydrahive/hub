#!/usr/bin/env python3
"""
import-agency-agents.py
Zieht alle Agenten aus https://github.com/msitarzewski/agency-agents
und konvertiert sie ins HydraHub-Format.

Usage:
    python3 scripts/import-agency-agents.py
"""

import json
import os
import re
import sys
import urllib.request

REPO_API = "https://api.github.com/repos/msitarzewski/agency-agents/git/trees/main?recursive=1"
RAW_BASE = "https://raw.githubusercontent.com/msitarzewski/agency-agents/main"
HUB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Kategorie-Mapping: agency-agents Ordnername → HydraHub-Kategorie
CATEGORY_MAP = {
    "engineering":         "engineering",
    "design":              "design",
    "marketing":           "marketing",
    "sales":               "sales",
    "product":             "product",
    "project-management":  "management",
    "testing":             "testing",
    "support":             "support",
    "game-development":    "gamedev",
    "spatial-computing":   "gamedev",
    "academic":            "personal",
    "personal":            "personal",
}

# Standard-Tools je nach Kategorie
TOOLS_MAP = {
    "engineering":  ["read_file", "list_directory", "shell_exec", "write_file"],
    "design":       ["read_file", "list_directory", "write_file"],
    "testing":      ["read_file", "list_directory", "shell_exec"],
    "marketing":    ["read_file", "write_file", "web_search"],
    "sales":        ["read_file", "write_file"],
    "product":      ["read_file", "write_file"],
    "management":   ["read_file", "write_file"],
    "support":      ["read_file", "write_file"],
    "gamedev":      ["read_file", "list_directory", "write_file", "shell_exec"],
    "personal":     ["read_file", "write_file"],
}

# Icon je Kategorie
ICON_MAP = {
    "engineering":  "⚙️",
    "design":       "🎨",
    "marketing":    "📢",
    "sales":        "💼",
    "product":      "📦",
    "management":   "📋",
    "testing":      "🧪",
    "support":      "🎧",
    "gamedev":      "🎮",
    "personal":     "🧠",
}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "HydraHub-Importer/1.0"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "HydraHub-Importer/1.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8", errors="replace")


def slugify(name):
    """Dateiname → agent-id: Kleinbuchstaben, Bindestriche"""
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


def extract_description(soul_md):
    """Erste aussagekräftige Zeile aus soul.md als Beschreibung."""
    for line in soul_md.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Entferne Markdown-Formatierung
        line = re.sub(r"\*+", "", line)
        line = re.sub(r"`+", "", line)
        if len(line) > 20:
            return line[:200]
    return ""


def agent_yaml(agent_id, display_name, category):
    tools = TOOLS_MAP.get(category, ["read_file", "write_file"])
    tools_yaml = "\n".join(f"  - {t}" for t in tools)
    return f"""id: {agent_id}
identity: {display_name}
type: specialist
llm:
  model: claude-sonnet-4-6
  max_tokens: 4096
  temperature: 0.7
execution_mode: safe
tools:
{tools_yaml}
"""


def main():
    print("Lade Dateiliste von agency-agents Repo...")
    tree = fetch_json(REPO_API)
    md_files = [
        item["path"]
        for item in tree["tree"]
        if item["path"].endswith(".md")
        and "/" in item["path"]
        and not item["path"].startswith(".")
        and "README" not in item["path"].upper()
    ]

    print(f"{len(md_files)} Agent-Dateien gefunden.")
    imported = 0
    skipped = 0

    for path in md_files:
        parts = path.split("/")
        if len(parts) < 2:
            skipped += 1
            continue

        folder = parts[0]   # z.B. "engineering"
        filename = parts[-1]  # z.B. "engineering-frontend-developer.md"

        category = CATEGORY_MAP.get(folder)
        if not category:
            print(f"  SKIP (kein Kategorie-Mapping): {path}")
            skipped += 1
            continue

        # Agent-ID aus Dateiname ableiten (ohne Kategorie-Prefix)
        base = filename[:-3]  # ohne .md
        # Kategorie-Prefix entfernen falls vorhanden
        for prefix in [f"{folder}-", f"{folder.replace('-','')}-"]:
            if base.startswith(prefix):
                base = base[len(prefix):]
                break

        agent_id = slugify(base)
        # Display-Name: Bindestriche → Leerzeichen, Title Case
        display_name = base.replace("-", " ").title()

        out_dir = os.path.join(HUB_ROOT, "agents", category, agent_id)

        # Nicht überschreiben wenn schon vorhanden
        if os.path.exists(out_dir):
            print(f"  SKIP (bereits vorhanden): {agent_id}")
            skipped += 1
            continue

        print(f"  Importiere: {path} → agents/{category}/{agent_id}")

        try:
            soul = fetch_text(f"{RAW_BASE}/{path}")
        except Exception as e:
            print(f"    FEHLER beim Laden: {e}")
            skipped += 1
            continue

        description = extract_description(soul)

        meta = {
            "id": agent_id,
            "type": "agent",
            "name": display_name,
            "description": description,
            "author": "agency-agents",
            "author_url": "https://github.com/msitarzewski/agency-agents",
            "category": category,
            "tags": [category, "imported"],
            "icon": ICON_MAP.get(category, "🤖"),
            "version": "1.0.0",
            "min_hydrahive_version": "1.0.0",
            "source": "agency-agents",
            "source_url": f"https://github.com/msitarzewski/agency-agents/blob/main/{path}",
            "license": "MIT"
        }

        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        with open(os.path.join(out_dir, "soul.md"), "w") as f:
            f.write(soul)
        with open(os.path.join(out_dir, "agent.yaml"), "w") as f:
            f.write(agent_yaml(agent_id, display_name, category))

        imported += 1

    print(f"\nFertig: {imported} importiert, {skipped} übersprungen.")


if __name__ == "__main__":
    main()
