# HydraHub Package Schema

## Paket-Struktur

Jedes Paket liegt in einem eigenen Unterverzeichnis:

```
agents/{category}/{id}/
  meta.json      ← Metadaten (Name, Beschreibung, Tags, Icon, Autor)
  soul.md        ← System-Prompt / Persönlichkeit
  agent.yaml     ← HydraHive-Konfiguration (Modell, Tools, etc.)

extensions/{id}/
  meta.json
  extension.py   ← Python-Modul

tools/{id}/
  meta.json
  config.json    ← MCP-Server-Konfiguration
```

## meta.json Schema

```json
{
  "id": "code-reviewer",
  "type": "agent",
  "name": "Code Reviewer",
  "description": "Analysiert Code auf Qualität, Sicherheit und Best Practices.",
  "author": "HydraHive Team",
  "author_url": "https://hydrahive.org",
  "category": "engineering",
  "tags": ["coding", "review", "quality"],
  "icon": "🔍",
  "version": "1.0.0",
  "min_hydrahive_version": "1.0.0",
  "source": "agency-agents",
  "source_url": "https://github.com/msitarzewski/agency-agents",
  "license": "MIT"
}
```

## agent.yaml Schema (Minimal-Template)

```yaml
agent_id: code-reviewer
display_name: Code Reviewer
model: claude-sonnet-4-6
execution_mode: safe
tools:
  - read_file
  - list_directory
```

## index.json

Wird automatisch durch `scripts/build-index.py` aus allen meta.json generiert.
Nicht manuell bearbeiten.
