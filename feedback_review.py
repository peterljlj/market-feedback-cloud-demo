"""Flag refill-compatibility cases for a human to review."""

import argparse
import csv
import json
import os
from pathlib import Path
import re
import sys

from feedback_check import check_batches


COMPATIBILITY = "refill_compatibility"
REFILL = re.compile(r"\brefills?\b|补充装", re.IGNORECASE)
SYMPTOM = re.compile(
    r"\b(?:does not fit|did not fit|would not fit|cannot fit|won't fit|"
    r"too wide|too narrow|would not seal|does not seal|could not seal|"
    r"did not lock|would not lock|cannot connect|would not connect|"
    r"leaked where (?:it|the refill) meets)\b|装不上|装不进|无法密封|接不上",
    re.IGNORECASE,
)


def review_batches(rules_file, batches):
    validation = check_batches(rules_file, batches)
    result = {
        "status": validation["status"],
        "rule_version": validation["rule_version"],
        "rules_fingerprint": validation["rules_fingerprint"],
        "input_fingerprints": validation["input_fingerprints"],
        "issues": validation["issues"],
        "scanned_records": 0,
        "flags": [],
    }
    if validation["issues"]:
        return result

    labels = json.loads(rules_file.read_text(encoding="utf-8"))["labels"]
    for batch in batches:
        with batch.open(encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                result["scanned_records"] += 1
                feedback = row["feedback"].strip()
                symptom = SYMPTOM.search(feedback)
                if not REFILL.search(feedback) or not symptom:
                    continue
                current_label = row["label"].strip()
                if current_label == COMPATIBILITY:
                    continue
                result["flags"].append({
                    "code": "LABEL_MISMATCH" if COMPATIBILITY in labels else "COVERAGE_GAP",
                    "batch": batch.name,
                    "id": row["id"].strip(),
                    "market": row["market"].strip(),
                    "current_label": current_label,
                    "suggested_label": COMPATIBILITY,
                    "matched_symptom": symptom.group(),
                    "feedback": feedback,
                })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path,
                        default=os.environ.get("FEEDBACK_RULES_FILE", "rules/v1.json"))
    parser.add_argument("batches", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        result = review_batches(args.rules, args.batches)
    except (OSError, ValueError, KeyError, csv.Error) as error:
        parser.exit(2, f"Unable to review feedback: {error}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
