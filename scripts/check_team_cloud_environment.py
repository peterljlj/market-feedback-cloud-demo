"""Check the repository configuration or verify the active Cloud task."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "cloud" / "market-feedback-pilot.json"


def check(args, env):
    output = subprocess.check_output([sys.executable, *args], cwd=ROOT, env=env)
    return json.loads(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepare", action="store_true",
        help="Test the repository using the configured variables in child processes",
    )
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    variables = config["runtime"]["environment_variables"]
    expected = config["acceptance"]
    env = os.environ.copy()
    if args.prepare:
        env.update(variables)

    try:
        for key, value in variables.items():
            if env.get(key) != value:
                raise ValueError(f"Set {key}={value} in the Cloud environment, then start a new task.")
        release = check(["verify_environment.py", "--expect", expected["rule_version"]], env)
        regional = release["sample_result"]
        coverage = check(["feedback_review.py", *expected["samples"]], env)
        expected_fields = {
            "status": "READY_FOR_REVIEW",
            "rule_version": expected["rule_version"],
            "rules_fingerprint": expected["rule_fingerprint"],
            "input_fingerprints": expected["input_fingerprints"],
            "market_label_counts": expected["market_label_counts"],
        }
        for key, value in expected_fields.items():
            if regional.get(key) != value:
                raise ValueError(f"Regional result for {key} differs from the repository configuration.")
        if coverage["flags"]:
            raise ValueError("Reviewed market batches still have unresolved coverage flags.")
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Team Cloud check failed: {error}\n")

    print(json.dumps({
        "check": "PASS",
        "scope": "repository configuration" if args.prepare else "active task configuration",
        "environment_config_name": config["name"],
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "release_check": release,
        "regional_result": regional,
        "reviewed_coverage": coverage,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
