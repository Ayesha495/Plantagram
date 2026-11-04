"""Seed (or refresh) the Plantagram GitHub Project from docs/pm/backlog.yaml.

Idempotent: existing labels, milestones, issues, sub-issue links, project
fields and items are reused, so the script is safe to re-run after editing
the backlog. Requires the GitHub CLI logged in with the `project` scope.

    python scripts/pm/seed_github_project.py
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import yaml

OWNER, REPO, PROJECT_TITLE = "Ayesha495", "Plantagram", "Plantagram"
FULL = f"{OWNER}/{REPO}"
ROOT = Path(__file__).resolve().parents[2]
GH = os.environ.get("GH") or shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"

AREAS = ["platform", "backend", "app", "design", "ai", "gamification", "social", "content", "staff", "launch"]
PRIORITIES = ["P0", "P1", "P2", "P3"]
STATUSES = [("Backlog", "GRAY"), ("Ready", "BLUE"), ("In progress", "YELLOW"), ("In review", "PURPLE"), ("Done", "GREEN")]
LABELS = {
    "type:epic": "5319e7", "type:feature": "1d76db", "type:chore": "c5def5", "type:infra": "0e8a16",
    "type:bug": "d73a4a", "type:docs": "0075ca",
    **{f"area:{a}": "bfdadc" for a in AREAS},
    "priority:P0": "b60205", "priority:P1": "d93f0b", "priority:P2": "fbca04", "priority:P3": "c2e0c6",
}


def gh(*args, parse=True):
    # GitHub's API intermittently fails (GraphQL errors, 5xx); retry with backoff.
    for attempt in range(5):
        res = subprocess.run([GH, *args], capture_output=True, text=True, encoding="utf-8")
        if not res.returncode or not any(s in res.stderr for s in ("Something went wrong", "502", "503", "504", "timeout", "error connecting")):
            break
        time.sleep(2 ** attempt)
    if res.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {res.stderr.strip()}")
    out = res.stdout
    return json.loads(out) if parse and out.strip() else out


def graphql(query, **variables):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    return gh(*args)["data"]


def ensure_labels():
    existing = {l["name"] for l in gh("label", "list", "-R", FULL, "--limit", "200", "--json", "name")}
    for name, color in LABELS.items():
        if name not in existing:
            gh("label", "create", name, "-R", FULL, "--color", color, parse=False)


def ensure_milestones(epics):
    existing = {m["title"]: m["number"] for m in gh("api", f"repos/{FULL}/milestones?state=all&per_page=100")}
    for e in epics:
        if e["title"] not in existing:
            m = gh("api", f"repos/{FULL}/milestones", "-f", f"title={e['title']}")
            existing[e["title"]] = m["number"]
    return existing


def all_issues():
    pages = gh("api", f"repos/{FULL}/issues?state=all&per_page=100", "--paginate", "--slurp")
    return {i["title"]: i for page in pages for i in page if "pull_request" not in i}


def ensure_issue(issues, title, body, labels, milestone):
    if title in issues:
        return issues[title]
    args = ["api", f"repos/{FULL}/issues", "-f", f"title={title}", "-f", f"body={body}", "-F", f"milestone={milestone}"]
    for l in labels:
        args += ["-f", f"labels[]={l}"]
    issue = gh(*args)
    issues[title] = issue
    return issue


def link_sub_issues(epic, children):
    existing = {s["id"] for s in gh("api", f"repos/{FULL}/issues/{epic['number']}/sub_issues?per_page=100")}
    for c in children:
        if c["id"] not in existing:
            gh("api", f"repos/{FULL}/issues/{epic['number']}/sub_issues", "-F", f"sub_issue_id={c['id']}")


def ensure_project():
    projects = gh("project", "list", "--owner", OWNER, "--format", "json")["projects"]
    p = next((p for p in projects if p["title"] == PROJECT_TITLE), None)
    if not p:
        p = gh("project", "create", "--owner", OWNER, "--title", PROJECT_TITLE, "--format", "json")
        gh("project", "link", str(p["number"]), "--owner", OWNER, "--repo", FULL, parse=False)
    return p


def ensure_fields(project, cfg):
    fields = {f["name"]: f for f in gh("project", "field-list", str(project["number"]), "--owner", OWNER, "--format", "json", "--limit", "50")["fields"]}
    pid = project["id"]

    for name, kind, options in [("Story points", "NUMBER", None), ("Phase", "SINGLE_SELECT", [f"Phase {i}" for i in range(10)]),
                                ("Priority", "SINGLE_SELECT", PRIORITIES), ("Area", "SINGLE_SELECT", AREAS)]:
        if name not in fields:
            args = ["project", "field-create", str(project["number"]), "--owner", OWNER, "--name", name, "--data-type", kind, "--format", "json"]
            if options:
                args += ["--single-select-options", ",".join(options)]
            gh(*args)

    status = fields.get("Status")
    if status and [o["name"] for o in status.get("options", [])] != [s for s, _ in STATUSES]:
        opts = ", ".join(f'{{name: "{n}", color: {c}, description: ""}}' for n, c in STATUSES)
        graphql(f'mutation($id: ID!) {{ updateProjectV2Field(input: {{fieldId: $id, singleSelectOptions: [{opts}]}}) {{ clientMutationId }} }}', id=status["id"])

    if "Sprint" not in fields:
        start = cfg["first_sprint_start"]
        graphql(
            'mutation($pid: ID!, $start: Date!, $dur: Int!) { createProjectV2Field(input: {projectId: $pid, dataType: ITERATION, name: "Sprint", '
            'iterationConfiguration: {startDate: $start, duration: $dur, iterations: ['
            + ", ".join(f'{{title: "Sprint {i}", startDate: "{dt.date.fromisoformat(str(start)) + dt.timedelta(days=(i - 1) * cfg["sprint_length_days"])}", duration: {cfg["sprint_length_days"]}}}' for i in range(1, 13))
            + ']}}) { clientMutationId } }',
            pid=pid, start=str(start), dur=cfg["sprint_length_days"])

    data = graphql('query($pid: ID!) { node(id: $pid) { ... on ProjectV2 { fields(first: 50) { nodes { '
                   '... on ProjectV2Field { id name } '
                   '... on ProjectV2SingleSelectField { id name options { id name } } '
                   '... on ProjectV2IterationField { id name configuration { iterations { id title } } } } } } } }', pid=pid)
    return {f["name"]: f for f in data["node"]["fields"]["nodes"] if f}


def set_fields(project, fields, item_id, *, points, phase, priority, area, status, sprint):
    base = ["project", "item-edit", "--id", item_id, "--project-id", project["id"]]
    def opt(field, name):
        return next(o["id"] for o in fields[field]["options"] if o["name"] == name)
    gh(*base, "--field-id", fields["Story points"]["id"], "--number", str(points), parse=False)
    gh(*base, "--field-id", fields["Phase"]["id"], "--single-select-option-id", opt("Phase", f"Phase {phase}"), parse=False)
    gh(*base, "--field-id", fields["Priority"]["id"], "--single-select-option-id", opt("Priority", priority), parse=False)
    gh(*base, "--field-id", fields["Area"]["id"], "--single-select-option-id", opt("Area", area), parse=False)
    gh(*base, "--field-id", fields["Status"]["id"], "--single-select-option-id", opt("Status", status), parse=False)
    if sprint:
        it = next(i["id"] for i in fields["Sprint"]["configuration"]["iterations"] if i["title"] == sprint)
        gh(*base, "--field-id", fields["Sprint"]["id"], "--iteration-id", it, parse=False)


def main():
    cfg = yaml.safe_load((ROOT / "docs/pm/backlog.yaml").read_text(encoding="utf-8"))
    epics = cfg["epics"]
    ensure_labels()
    milestones = ensure_milestones(epics)
    issues = all_issues()
    project = ensure_project()
    fields = ensure_fields(project, cfg)
    done = {"Move Django secrets to env and add root .gitignore", "Obsidian project map vault",
            "GitHub Project, labels, milestones and backlog seed"}

    for e in epics:
        ph, ms = e["phase"], milestones[e["title"]]
        sprint = "Sprint 1" if ph in cfg["sprint_1_phases"] else None
        children = []
        for title, points, prio, area in e["tasks"]:
            kind = "type:infra" if area == "platform" else "type:feature"
            body = f"Part of **{e['title']}**.\n\n### Acceptance criteria\n- [ ] Implemented as described in the approved plan\n- [ ] Tests added and CI green\n- [ ] Related notes in `docs/vault` updated"
            issue = ensure_issue(issues, title, body, [kind, f"area:{area}", f"priority:{prio}"], ms)
            children.append(issue)
            item = gh("project", "item-add", str(project["number"]), "--owner", OWNER, "--url", issue["html_url"], "--format", "json")
            status = "Done" if title in done else ("Ready" if sprint else "Backlog")
            set_fields(project, fields, item["id"], points=points, phase=ph, priority=prio, area=area, status=status, sprint=sprint)
            print(f"  #{issue['number']} {title}")

        epic_body = f"Epic for {e['title']}. Tasks are tracked as sub-issues."
        epic = ensure_issue(issues, e["title"], epic_body, ["type:epic"], ms)
        link_sub_issues(epic, children)
        item = gh("project", "item-add", str(project["number"]), "--owner", OWNER, "--url", epic["html_url"], "--format", "json")
        set_fields(project, fields, item["id"], points=sum(t[1] for t in e["tasks"]), phase=ph, priority="P0",
                   area="platform" if ph < 2 else e["tasks"][0][3], status="Ready" if sprint else "Backlog", sprint=sprint)
        print(f"Epic #{epic['number']} {e['title']}")

    print(f"Project: {project.get('url')}")


if __name__ == "__main__":
    main()
