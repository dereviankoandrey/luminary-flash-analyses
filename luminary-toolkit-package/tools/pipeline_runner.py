#!/usr/bin/env python3
"""Luminary Pipeline Runner — Execute underwriting agents via Ollama.

Usage:
    python pipeline_runner.py --prompt core_underwriter --deal deal.json
    python pipeline_runner.py --prompt risk_auditor --analysis analysis.json
    python pipeline_runner.py --all --address "123 Main St, Phoenix AZ"
"""

import json
import subprocess
from pathlib import Path

OLLAMA = "ollama"

SYSTEM_PROMPTS = {
    "core_underwriter": """You are a professional real estate underwriting analyst operating with strict deterministic logic.
RULES: NEVER fabricate data. ALWAYS show every calculation step. Default to conservative assumptions.
DEFAULT ASSUMPTIONS: Vacancy=5%, Maintenance=8% of gross rent, Management=10%, Capex=3% of gross rent.""",

    "risk_auditor": """You are a real estate investment risk auditor. Evaluate the deal analysis against standard criteria.
RISK CHECKLIST: 1) Cap rate within market range? 2) DSCR > 1.0? 3) CoC positive? 4) Data complete?
OUTPUT: risk_score (0-100), critical_issues[], warnings[], passes[], recommendation.""",

    "report_writer": """You are a professional real estate report writer. Convert analysis data into a clean markdown underwriting report with executive summary, all sections, and clear recommendation."""
}

def run_agent(prompt_name, user_input):
    prompt = SYSTEM_PROMPTS[prompt_name]
    result = subprocess.run(
        [OLLAMA, "run", "qwen2.5:14b"],
        input=f"{prompt}\n\nINPUT:\n{user_input}",
        capture_output=True, text=True, timeout=120
    )
    return result.stdout

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Luminary Agent Pipeline Runner")
    parser.add_argument("--prompt", choices=list(SYSTEM_PROMPTS.keys()), help="System prompt to use")
    parser.add_argument("--deal", type=str, help="JSON file with deal data")
    parser.add_argument("--address", type=str, help="Property address for extraction")
    args = parser.parse_args()
    
    if args.deal:
        with open(args.deal) as f:
            deal_data = json.load(f)
        output = run_agent(args.prompt, json.dumps(deal_data, indent=2))
        print(output)
