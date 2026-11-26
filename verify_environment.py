import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


PROJECT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description='Verify the active feedback release with a known sample.')
    parser.add_argument('--expect', required=True, choices=('v1', 'v2'))
    expected = parser.parse_args().expect
    configured = os.environ.get('FEEDBACK_RULES_FILE')
    if not configured or (PROJECT / configured).resolve() != PROJECT / 'rules' / f'{expected}.json':
        parser.exit(2, f'Set FEEDBACK_RULES_FILE to rules/{expected}.json in the environment configuration.\n')

    result = subprocess.run(
        [sys.executable, 'feedback_check.py', 'samples/au-revised.csv'],
        cwd=PROJECT, capture_output=True, text=True,
    )
    expected_exit = 1 if expected == 'v1' else 0
    if result.returncode != expected_exit:
        parser.exit(2, f'Unexpected checker exit code {result.returncode}:\n{result.stderr or result.stdout}')

    report = json.loads(result.stdout)
    specification = json.loads((PROJECT / 'cloud/market-feedback-pilot.json').read_text(encoding='utf-8'))
    expected_cases = len(specification['acceptance']['coverage_case_ids'])
    if expected == 'v1':
        correct = report['status'] == 'BLOCKED' and len(report['issues']) == expected_cases and all(
            "label 'refill_compatibility' is absent from v1" in issue for issue in report['issues']
        )
    else:
        correct = (
            report['status'] == 'READY_FOR_REVIEW'
            and report['market_label_counts'].get('AU', {}).get('refill_compatibility') == expected_cases
        )
    if not correct or report['rule_version'] != expected:
        parser.exit(2, f'Unexpected rule version or validation result:\n{result.stdout}')

    print(json.dumps({'environment_check': 'PASS', 'sample_result': report}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
