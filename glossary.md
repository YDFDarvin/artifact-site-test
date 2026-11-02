# Glossary

- **Artifact**: a page published on claude.ai, with a URL such as `https://claude.ai/artifact/<id>`.
- **Mapped artifact**: an artifact with an entry in `artifacts.json`.
- **Source of truth**: the `src` file in this repo. All chats edit this file.
- **src file**: the page content, exactly as published to claude.ai.
- **Pages file**: the `docs/` copy that GitHub Pages serves.
- **Sync hook**: `scripts/artifact-sync.py`, called by Claude Code before and after the Artifact tool.
