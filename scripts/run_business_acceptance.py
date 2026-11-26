"""Run the feedback pilot on the selected checkout and emit JSON evidence."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
AU_SAMPLE = "samples/au-revised.csv"


def run(args, rule_file=None, parse_json=False):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if rule_file is not None:
        env["FEEDBACK_RULES_FILE"] = rule_file
    command = [sys.executable, *args]
    process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    output = {
        "command": ["python3", *args],
        "rules_override": rule_file,
        "exit_code": process.returncode,
    }
    if parse_json and process.stdout:
        try:
            output["result"] = json.loads(process.stdout)
        except json.JSONDecodeError:
            output["stdout"] = process.stdout
    elif process.stdout:
        output["stdout"] = process.stdout
    if process.stderr:
        output["stderr"] = process.stderr
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", choices=("A", "B"), required=True,
                        help="Operator-supplied role label")
    account = parser.parse_args().account
    config = json.loads((ROOT / "cloud/market-feedback-pilot.json").read_text(encoding="utf-8"))
    expected = config["acceptance"]
    original_batches = expected["original_samples"]
    evidence = {
        "account_label": account,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "python_version": sys.version.split()[0],
        "tests": run(["-m", "unittest", "-v"]),
        "active_environment": run(["verify_environment.py", "--expect", "v2"], parse_json=True),
        "au_v1": run(["feedback_check.py", AU_SAMPLE], "rules/v1.json", parse_json=True),
        "au_v2": run(["feedback_check.py", AU_SAMPLE], "rules/v2.json", parse_json=True),
        "regional_v2": run(
            ["feedback_check.py", *expected["samples"]],
            "rules/v2.json", parse_json=True,
        ),
        "coverage_v1": run(["feedback_review.py", *original_batches], "rules/v1.json", parse_json=True),
        "coverage_v2_on_original": run(
            ["feedback_review.py", *original_batches], "rules/v2.json", parse_json=True,
        ),
        "coverage_v2_after_review": run(
            ["feedback_review.py", *expected["samples"]], "rules/v2.json", parse_json=True,
        ),
    }
    v1 = evidence["au_v1"].get("result", {})
    v2 = evidence["au_v2"].get("result", {})
    regional = evidence["regional_v2"].get("result", {})
    regional_counts = expected["market_label_counts"]
    au_case_count = regional_counts["AU"]["refill_compatibility"]
    au_input = {Path(AU_SAMPLE).name: expected["input_fingerprints"][Path(AU_SAMPLE).name]}
    case_ids = expected["coverage_case_ids"]
    v1_flags = evidence["coverage_v1"].get("result", {}).get("flags", [])
    v2_flags = evidence["coverage_v2_on_original"].get("result", {}).get("flags", [])
    passed = (
        evidence["tests"]["exit_code"] == 0
        and evidence["au_v1"]["exit_code"] == 1
        and v1.get("status") == "BLOCKED"
        and v1.get("rules_fingerprint") == "76f86e31bd5e"
        and v1.get("input_fingerprints") == au_input
        and len(v1.get("issues", [])) == au_case_count
        and evidence["au_v2"]["exit_code"] == 0
        and v2.get("status") == "READY_FOR_REVIEW"
        and v2.get("rules_fingerprint") == expected["rule_fingerprint"]
        and v2.get("input_fingerprints") == au_input
        and v2.get("market_label_counts") == {"AU": regional_counts["AU"]}
        and evidence["regional_v2"]["exit_code"] == 0
        and regional.get("market_label_counts") == regional_counts
        and [(flag["id"], flag["code"]) for flag in v1_flags]
        == [(case_id, "COVERAGE_GAP") for case_id in case_ids]
        and [(flag["id"], flag["code"]) for flag in v2_flags]
        == [(case_id, "LABEL_MISMATCH") for case_id in case_ids]
        and evidence["coverage_v2_after_review"]["exit_code"] == 0
        and evidence["coverage_v2_after_review"].get("result", {}).get("flags") == []
    )
    evidence["repository_check"] = "PASS" if passed else "FAIL"
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
