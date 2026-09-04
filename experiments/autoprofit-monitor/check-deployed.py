#!/usr/bin/env python3
"""Nightly deployed-audit tool for AutoProfit pipeline.

Checks all 11 Luminary repos via HTTP and produces JSON + markdown reports.
Designed to run from the AutoProfit cron job.
"""
import subprocess, os, json
from datetime import datetime

BASE = "https://dereviankoandrey.github.io/"
REPOS = [
    ("luminary-product-hub",     "All-in-one product hub"),
    ("luminary-seo-landing-pages","SEO redirect pages"),
    ("luminary-flash-analyses",  "Flash deal analyses (25 markets)"),
    ("deal-screener-demo",       "Chrome extension demo"),
    ("luminary-dealaudit-verifier","AI audit tool"),
    ("luminary-safedeal-analyzer","Risk assessment framework"),
    ("luminary-deal-scoring-matrix", "Deterministic scoring tool"),
    ("luminary-verified-brief",  "Market intelligence briefs"),
    ("luminary-ai-agent-monitor","Agent performance monitor"),
    ("luminary-ai-detection-checklist","AI content detection"),
    ("luminary-re-underwriting-skill","Underwriting methodology docs"),
]

def check(repo_name):
    """Check a single repo's health via curl."""
    url = f"{BASE}{repo_name}/"
    start_time = __import__('time').monotonic()
    try:
        result = subprocess.run(
            ["curl", "-sfLw", "{http_code}|{size_download}|{time_total}",
             "--max-time", "10", url],
            capture_output=True, text=True, timeout=15)
        
        elapsed_ms = (__import__('time').monotonic() - start_time) * 1000
        
        if result.returncode == 0:
            parts = result.stdout.strip().split("|")
            code = int(parts[0])
            size = int(parts[1]) if len(parts) > 1 else 0
            healthy = (200 <= code < 400) and size > 50
        else:
            code, size, healthy = -1, 0, False

        return {
            "name": repo_name,
            "status_code": code,
            "size_bytes": size,
            "response_time_ms": round(elapsed_ms),
            "healthy": healthy,
        }
    except Exception:
        elapsed_ms = (__import__('time').monotonic() - start_time) * 1000
        return {"name": repo_name, "status_code": -1, "size_bytes": 0,
                "response_time_ms": round(elapsed_ms), "healthy": False}


def git_last_commit(repo_path_dir):
    """Get last commit from a local git repo."""
    try:
        r = subprocess.run(
            ["git", "-C", repo_path_dir, "log", "-1",
             "--format=%ci %s"],
            capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()[:120]
    except Exception:
        pass
    return None


def resolve_path_for(name):
    """Find the local checkout path for a repo."""
    for p in [f"/home/andrey/.openclaw/workspace/{name}/.git"]:
        if os.path.isdir(p):
            return p.replace("/.git", "")
    for p in [f"~/{name}/.git"]:# home directory check
        expanded = os.path.expanduser(p)
        if os.path.isdir(expanded):
            return expanded # return the dir before .git
    return None


def main():
    ts = datetime.utcnow()

    print("Running deployed-audit for", len(REPOS), "repos...")
    repo_health = [check(n) for n, _ in REPOS]
    
    online = sum(1 for r in repo_health if r["healthy"])
    offline_count = len(repo_health) - online
    total_response = sum(r["response_time_ms"] for r in repo_health)

    report_data = {
        "timestamp": ts.isoformat() + "Z",
        "night_number": 156,
        "summary": {
            "total_repos": len(REPOS),
            "online": online,
            "offline": offline_count,
            "avg_response_ms": round(total_response / max(online, 1)),
            "overall_healthy": (online == len(REPOS))
        },
        "repos": [],
    }

    for r in repo_health:
        local_path = resolve_path_for(r["name"])
        gc = git_last_commit(local_path) if local_path else None
        
        report_data["repos"].append({**r, "git_last_commit": gc})

    # Write JSON report
    os.makedirs("/home/andrey/.openclaw/workspace/experiments/autoprofit-monitor", exist_ok=True)
    json_path = f"/home/andrey/.openclaw/workspace/experiments/autoprofit-monitor/report-{ts.strftime('%Y-%m-%d')}-{ts.strftime('%H%M')}.json"
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)

    # Markdown report for memory/ tracking
    md_lines = [f"# AutoProfit Health Audit Night 156 ({ts.strftime('%B %d, %Y')})\n", "",
                f"**Status:** {'All online' if online == len(REPOS) else str(online) + '/' + str(len(REPOS)) + ' healthy'\n                , ""]

        for i,r in enumerate(report_data ["repos"], 1):
            ch = "OK" if r["healthy"] else "DOWN"
            gc = (r. get("git_last_commit", "" or "").split(":")[0][:35] or "-")
            md_lines.append(f"| {i} | {ch}| {r['name']} | {gc} | HTTP/{r['status_code']} | {(r['size_bytes']/ 1024: .1f}K|{r['response_time_ms']}ms ")

    md_path = f"/home/andrey/.openclaw/workspace/memory/{ts.strftime('%Y-%m-%d')}-health.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines))

if __name__ == "__main__":
    main()