#!/usr/bin/env python3
"""Keep claude.ai artifacts and this repo in sync.

Claude Code hooks call this script (see .claude/settings.json):
  start  SessionStart: pull the repo, list the mapped artifacts.
  pre    PreToolUse on Artifact: pull the repo before a read or a publish.
         Block a publish of a mapped artifact that does not use its src file.
  post   PostToolUse on Artifact: after a publish of a mapped artifact,
         build the GitHub Pages file, commit and push.
  build  Build all GitHub Pages files from src (manual use).

Exit code 2 blocks the tool call. Claude reads the message on stderr.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "artifacts.json")
HEAD = os.path.join(ROOT, "scripts", "page-head.html")
TAIL = "\n</body></html>"


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def artifacts():
    with open(MAP, encoding="utf-8") as f:
        return json.load(f)["artifacts"]


def find(tool_input):
    url = tool_input.get("url") or ""
    path = os.path.abspath(tool_input.get("file_path") or "/nonexistent")
    for a in artifacts():
        if any(i in url for i in a["ids"]):
            return a
        if path == os.path.join(ROOT, a["src"]):
            return a
    return None


def pull():
    r = git("pull", "--ff-only", "--quiet")
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def build(a):
    with open(HEAD, encoding="utf-8") as f:
        head = f.read()
    with open(os.path.join(ROOT, a["src"]), encoding="utf-8") as f:
        body = f.read()
    with open(os.path.join(ROOT, a["page"]), "w", encoding="utf-8") as f:
        f.write(head + body + TAIL)


def context(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def is_publish(tool_input):
    return (tool_input.get("action") or "publish") == "publish" and not tool_input.get("asset")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "build":
        for a in artifacts():
            build(a)
        return 0
    event = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    tool_input = event.get("tool_input") or {}

    if mode == "start":
        ok, msg = pull()
        rows = "\n".join(f"- {a['name']}: {a['url']} -> {os.path.join(ROOT, a['src'])}" for a in artifacts())
        state = "Repo pulled." if ok else f"Repo pull failed: {msg}"
        context("SessionStart", f"{state} These artifacts use this repo as the source of truth. "
                f"Edit the src file and publish it with the Artifact url:\n{rows}")
        return 0

    a = find(tool_input)
    if not a:
        return 0

    if mode == "pre":
        ok, msg = pull()
        if not ok:
            print(f"Stop. git pull failed in {ROOT}: {msg}. Fix the repo state, then try again.", file=sys.stderr)
            return 2
        src = os.path.join(ROOT, a["src"])
        if is_publish(tool_input):
            if os.path.abspath(tool_input.get("file_path") or "") != src:
                print(f"Stop. Publish {a['name']} from {src} (the source of truth), "
                      f"with url {a['url']}.", file=sys.stderr)
                return 2
        else:
            context("PreToolUse", f"Repo pulled. The source of truth for {a['name']} is {src}.")
        return 0

    if mode == "post":
        if not is_publish(tool_input):
            return 0
        build(a)
        git("add", a["src"], a["page"])
        if git("diff", "--cached", "--quiet").returncode == 0:
            return 0
        git("commit", "-m", f"Publish {a['name']}", "--quiet")
        r = git("push", "--quiet")
        if r.returncode != 0:
            git("pull", "--rebase", "--quiet")
            r = git("push", "--quiet")
        note = "pushed" if r.returncode == 0 else f"NOT pushed: {(r.stderr or '').strip()}"
        context("PostToolUse", f"{a['name']}: built {a['page']}, committed, {note}.")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
