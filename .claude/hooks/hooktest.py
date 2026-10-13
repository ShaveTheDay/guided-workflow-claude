#!/usr/bin/env python3
"""Regression test for the v19 template hooks. Usage: hooktest.py <template dir>"""
import json, os, re, shutil, subprocess, sys, tempfile, datetime, pathlib

SRC = pathlib.Path(sys.argv[1]).resolve()
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
fails = []

def fresh():
    d = pathlib.Path(tempfile.mkdtemp()) / "proj"
    shutil.copytree(SRC, d)
    return d

def hook(proj, name, payload):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(proj))
    r = subprocess.run([sys.executable, str(proj / ".claude/hooks" / name)],
                       input=json.dumps(payload), capture_output=True, text=True, env=env, cwd=proj)
    assert r.returncode == 0, (name, r.stderr)
    return json.loads(r.stdout) if r.stdout.strip() else None

def check(label, got, want_deny):
    denied = bool(got and got.get("hookSpecificOutput", {}).get("permissionDecision") == "deny")
    ok = denied == want_deny
    print(f"{'ok  ' if ok else 'FAIL'} {label}")
    if not ok: fails.append(label)

def bash(proj, cmd, sid=None):
    p = {"tool_name": "Bash", "tool_input": {"command": cmd}}
    if sid: p["session_id"] = sid
    return hook(proj, "guard_bash.py", p)

def edit(proj, path, old="a", new="b", tool="Edit", sid=None):
    p = {"tool_name": tool, "tool_input": {"file_path": path, "old_string": old, "new_string": new}}
    if tool == "Write": p["tool_input"] = {"file_path": path, "content": new}
    if sid: p["session_id"] = sid
    return hook(proj, "guard_edits.py", p)

def set_onboarded(proj, val):
    f = proj / ".claude/CLAUDE.md"; t = f.read_text()
    t = re.sub(r"\*\*Onboarded:\*\* `(true|false)`", f"**Onboarded:** `{val}`", t); f.write_text(t)

def populate_plan(proj, name, status, approved="The approved plan.\n"):
    f = proj / "plans" / name
    t = (proj / "plans/PLAN_TEMPLATE.md").read_text() if not f.exists() else f.read_text()
    t = re.sub(r"\| Status +\| `[^\n]*", f"| Status         | `{status}`", t, count=1)
    t = t.replace("YYYY-MM-DD HH:MM:SS", NOW).replace("_[not yet started]_", NOW)
    if approved: t += f"\n### Approved — {NOW}\n\n{approved}"
    f.write_text(t); (proj / "plans/CURRENT_PLAN").write_text(name + "\n")

# ---------- 1. bash guard, generic ----------
p = fresh(); set_onboarded(p, "true")
for cmd, deny in [("git status", 0), ("git log --oneline -5", 0), ("git branch --list", 0), ("git diff plans/x.md", 0),
                  ("git commit -m x", 1), ("cd src && git -C .. commit -m x", 1), ("FOO=1 git --no-pager push origin main", 1),
                  ("uv run pytest | tee out.txt; git add .", 1), ("echo $(git stash)", 1), ("git branch feature", 1),
                  ("git branch -d feature", 1), ("pip install requests", 1), ("rm -rf build", 1), ("rm build/x.txt", 0),
                  ("date '+%Y-%m-%d %H:%M:%S'", 0), ("uv run pytest", 0), ("uv add requests", 0), ("curl http://x", 1)]:
    check(f"bash: {cmd}", bash(p, cmd), bool(deny))
# protected paths via shell
for cmd, deny in [("python3 - <<'EOF'\np='plans/step-001.md'\nopen(p).read()\nEOF", 1), ("sed -i 's/a/b/' plans/step-001.md", 1),
                  ("echo hi >> plans/step-001.md", 1), ("cp plans/step-001.md /tmp/backup.md", 0), ("cp src/x.py baseline/x.py", 1),
                  ("cat plans/CURRENT_PLAN", 0), ("grep -n Status plans/step-001.md", 0), ("sed -n '1,20p' plans/step-001.md", 0),
                  ("python3 scripts/build.py > out/log.txt 2>&1", 0), ("ls -la plans/", 0), ("python3 -c \"print(1)\" | tee plans/x.md", 1),
                  ("echo x > .claude/hooks/guard_bash.py", 1)]:
    check(f"bash protected: {cmd.splitlines()[0]}", bash(p, cmd), bool(deny))
# baseline snapshot during onboarding
p2 = fresh()  # Onboarded false
check("bash onboarding: cp into baseline allowed", bash(p2, "cp -r /src/legacy/. baseline/"), False)
check("bash onboarding: mkdir+cp into baseline allowed", bash(p2, "mkdir -p baseline/pkg && cp a.py baseline/pkg/"), False)
check("bash onboarding: plans still protected", bash(p2, "sed -i s/a/b/ plans/step-000-initial.md"), True)
check("edit onboarding: Write baseline allowed", edit(p2, "baseline/app.py", tool="Write"), False)
check("edit onboarded: Write baseline denied", edit(p, "baseline/app.py", tool="Write"), True)

# ---------- 2. edit guard, files ----------
check("edit: hooks protected", edit(p, ".claude/hooks/guard_bash.py"), True)
check("edit: settings protected", edit(p, ".claude/settings.json"), True)
check("edit: skills editable", edit(p, ".claude/skills/next-step/SKILL.md"), False)
check("edit: agents editable", edit(p, ".claude/agents/reviewer.md"), False)
check("edit: src editable", edit(p, "src/main.py"), False)
check("edit: Write placeholder goal allowed", edit(p, "plans/000-goal.md", tool="Write"), False)
check("edit: Write new plan allowed", edit(p, "plans/step-001-new.md", tool="Write"), False)
populate_plan(p, "step-000-initial.md", "completed")
check("edit: Write populated plan denied", edit(p, "plans/step-000-initial.md", tool="Write"), True)
check("edit: frozen plan denied", edit(p, "plans/step-000-initial.md", "- _[nothing yet]_", "- done"), True)
check("edit: frozen plan rollback allowed", edit(p, "plans/step-000-initial.md", "| Status         | `completed`", "| Status         | `rolled-back`"), False)
populate_plan(p, "step-000-initial.md", "in-progress")
check("edit: approved text change denied", edit(p, "plans/step-000-initial.md", "The approved plan.", "changed"), True)
check("edit: approved append allowed", edit(p, "plans/step-000-initial.md", "The approved plan.\n", "The approved plan.\n\n### Plan Revision — x\n\nRevised.\n"), False)
check("edit: section before approved allowed", edit(p, "plans/step-000-initial.md", "- _[nothing yet]_", "- done"), False)

# ---------- 3. check_plan ----------
p3 = fresh(); set_onboarded(p3, "true")
populate_plan(p3, "step-000-initial.md", "completed", approved="## Context\n\nFile: `2026-10-20 Holiday Fiji.md`.\n\n## Implementation\n\n- x\n")
r = hook(p3, "check_plan.py", {"tool_name": "Edit", "tool_input": {"file_path": "plans/step-000-initial.md"}})
check("check_plan: silent on good plan with ## in approved + filename date", r, False) if r is None else (print("FAIL check_plan false alarm:", r), fails.append("check_plan false alarm"))
f = p3 / "plans/step-000-initial.md"; t = f.read_text().replace(f"| Created        | {NOW}", "| Created        | 2026-10-07") + "\n## Session State (Handoff Context)\n"; f.write_text(t)
r = hook(p3, "check_plan.py", {"tool_name": "Edit", "tool_input": {"file_path": "plans/step-000-initial.md"}})
ctx = (r or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
ok = "last template section" in ctx and "timestamp field" in ctx
print(("ok   " if ok else "FAIL ") + "check_plan: real problems reported"); ok or fails.append("check_plan real")
populate_plan(fresh_p := fresh(), "step-000-initial.md", "planned", approved="")
r = hook(fresh_p, "check_plan.py", {"tool_name": "Edit", "tool_input": {"file_path": "plans/step-000-initial.md"}})
ctx = (r or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
ok = "is empty" in ctx; print(("ok   " if ok else "FAIL ") + "check_plan: empty approved section reported"); ok or fails.append("check_plan empty")

# ---------- 4. session kinds ----------
p4 = fresh(); set_onboarded(p4, "true"); populate_plan(p4, "step-000-initial.md", "completed")
r = hook(p4, "session_context.py", {"hook_event_name": "SessionStart", "source": "clear", "session_id": "S1"})
ctx = r["hookSpecificOutput"]["additionalContext"]
ok = "Session kind: planning" in ctx and "Role: Planner" in ctx; print(("ok   " if ok else "FAIL ") + "session: completed -> planning"); ok or fails.append("session planning")
check("planning: edit src denied", edit(p4, "src/main.py", sid="S1"), True)
check("planning: write new plan allowed", edit(p4, "plans/step-001-x.md", tool="Write", sid="S1"), False)
check("planning: edit CLAUDE.md allowed", edit(p4, ".claude/CLAUDE.md", sid="S1"), False)
check("planning: edit plans/CURRENT_PLAN allowed", edit(p4, "plans/CURRENT_PLAN", "step-000-initial.md", "step-001-x.md", sid="S1"), False)
check("planning: Write plans/CURRENT_PLAN allowed", edit(p4, "plans/CURRENT_PLAN", tool="Write", new="step-001-x.md\n", sid="S1"), False)
check("planning: bash write denied", bash(p4, "echo x > src/main.py", "S1"), True)
check("planning: bash touch denied", bash(p4, "touch src/new.py", "S1"), True)
check("planning: uv run allowed", bash(p4, "uv run pytest", "S1"), False)
check("planning: cat allowed", bash(p4, "cat src/main.py", "S1"), False)
populate_plan(p4, "step-001-x.md", "planned")
check("planning: status->in-progress denied", edit(p4, "plans/step-001-x.md", "| Status         | `planned`", "| Status         | `in-progress`", sid="S1"), True)
r = hook(p4, "session_context.py", {"hook_event_name": "SessionStart", "source": "clear", "session_id": "S2"})
ok = "Session kind: implementing" in r["hookSpecificOutput"]["additionalContext"]; print(("ok   " if ok else "FAIL ") + "session: planned -> implementing"); ok or fails.append("session impl")
check("implementing: edit src allowed", edit(p4, "src/main.py", sid="S2"), False)
check("implementing: status->in-progress allowed", edit(p4, "plans/step-001-x.md", "| Status         | `planned`", "| Status         | `in-progress`", sid="S2"), False)
check("implementing: bash write allowed", bash(p4, "echo x > src/main.py", "S2"), False)
check("unknown session: edit src allowed", edit(p4, "src/main.py"), False)
# S2 reviews, passes, records step-002 in the same session -> becomes planning
populate_plan(p4, "step-001-x.md", "completed"); populate_plan(p4, "step-002-y.md", "planned")
check("implementing->new plan recorded: edit src denied", edit(p4, "src/main.py", sid="S2"), True)
check("implementing->new plan recorded: bash write denied", bash(p4, "echo x > src/main.py", "S2"), True)
check("implementing->new plan recorded: edit CURRENT_PLAN allowed", edit(p4, "plans/CURRENT_PLAN", "a", "b", sid="S2"), False)
check("implementing->new plan recorded: status->in-progress denied", edit(p4, "plans/step-002-y.md", "| Status         | `planned`", "| Status         | `in-progress`", sid="S2"), True)
p5 = fresh()
r = hook(p5, "session_context.py", {"hook_event_name": "SessionStart", "source": "startup", "session_id": "S0"})
ok = "Session kind: onboarding" in r["hookSpecificOutput"]["additionalContext"] and "run /start" in r["hookSpecificOutput"]["additionalContext"]
print(("ok   " if ok else "FAIL ") + "session: fresh template -> onboarding, route /start"); ok or fails.append("session onboarding")
check("onboarding: edit src allowed", edit(p5, "src/main.py", sid="S0"), False)
r = hook(p5, "prompt_time.py", {"hook_event_name": "UserPromptSubmit", "prompt": "hi"})
ok = "System time at the start of this turn" in r["hookSpecificOutput"]["additionalContext"]; print(("ok   " if ok else "FAIL ") + "prompt_time injects"); ok or fails.append("prompt_time")

# ---------- 5. skill injections ----------
for skill in ("start", "next-step"):
    txt = (SRC / f".claude/skills/{skill}/SKILL.md").read_text()
    cmds = re.findall(r"!`(.*?)`(?=\n|$)", txt)
    for c in cmds:
        for val in ("false", "true"):
            pp = fresh(); set_onboarded(pp, val)
            r = subprocess.run(["bash", "-c", c], capture_output=True, text=True, cwd=pp)
            out = r.stdout.strip()
            bad = r.returncode != 0 and "git" not in c
            if "Onboarded" in c: bad = bad or out != val
            print(("FAIL " if bad else "ok   ") + f"{skill} inject [{val}]: {c[:60]} -> {out.splitlines()[:1]}")
            bad and fails.append(f"inject {skill} {c[:30]}")

print("\nFAILURES:", fails or "none")
sys.exit(1 if fails else 0)
