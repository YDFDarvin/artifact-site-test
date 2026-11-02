# Artifact repo

This repo is the source of truth for the claude.ai artifacts in `artifacts.json`.
GitHub Pages serves `docs/`: https://ydfdarvin.github.io/artifact-site-test/

## Rules

1. Before you read or write a mapped artifact, run `git pull --ff-only`.
2. Edit the `src` file of the artifact. Do not edit `docs/` by hand.
3. Publish with the Artifact tool: `file_path` = the `src` file, `url` = the artifact `url`.
4. After the publish, build `docs/`, commit and push.
5. If the Artifact tool refuses a publish because of a newer version, merge that version into the `src` file, then publish again.

The hooks in `.claude/settings.json` do steps 1 and 4 automatically.
They block a publish of a mapped artifact that does not use its `src` file.

## Files

- `artifacts.json`: artifact URL to `src` file and `docs` page.
- `src/*.html`: the page content, as published to claude.ai.
- `docs/*.html`: the GitHub Pages copy (`scripts/page-head.html` + `src` + closing tags).
- `scripts/artifact-sync.py`: the hook script. `python3 scripts/artifact-sync.py build` builds all `docs/` pages.

## Add an artifact

1. Read the artifact with the Artifact tool. Save its source to `src/<name>.html`.
2. Add an entry to `artifacts.json`: `name`, `ids` (the ids in the artifact URLs), `url`, `src`, `page`.
3. Run `python3 scripts/artifact-sync.py build`. Commit and push.

New terms go in `glossary.md`.
