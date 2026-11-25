import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sys


FIELDS = ('id', 'market', 'feedback', 'label')


def check_batches(rules_file, batches):
    rules_bytes = rules_file.read_bytes()
    rules = json.loads(rules_bytes)
    version, labels, markets = rules['version'], rules['labels'], rules['markets']
    issues = []
    ids = set()
    counts = {}
    fingerprints = {}

    for batch in batches:
        if batch.name in fingerprints:
            raise ValueError(f'Duplicate batch filename: {batch.name}')
        batch_bytes = batch.read_bytes()
        fingerprints[batch.name] = hashlib.sha256(batch_bytes).hexdigest()[:12]
        with io.StringIO(batch_bytes.decode('utf-8-sig'), newline='') as stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames is None or sorted(reader.fieldnames) != sorted(FIELDS):
                issues.append(f'{batch.name}: expected headers {", ".join(FIELDS)}')
                continue
            rows = 0
            for row in reader:
                rows += 1
                location = f'{batch.name}:{reader.line_num}'
                if None in row or any(not row[field] or not row[field].strip() for field in FIELDS):
                    issues.append(f'{location}: fill in all four fields')
                    continue
                item_id, market, _, label = (row[field].strip() for field in FIELDS)
                if item_id in ids:
                    issues.append(f'{location}: duplicate feedback id {item_id!r}')
                ids.add(item_id)
                if market not in markets:
                    issues.append(f'{location}: unknown market {market!r}')
                if label not in labels:
                    issues.append(f'{location}: label {label!r} is absent from {version}')
                if market in markets and label in labels:
                    counts.setdefault(market, Counter())[label] += 1
            if not rows:
                issues.append(f'{batch.name}: no feedback rows')

    return {
        'status': 'BLOCKED' if issues else 'READY_FOR_REVIEW',
        'rule_version': version,
        'rules_fingerprint': hashlib.sha256(rules_bytes).hexdigest()[:12],
        'input_fingerprints': fingerprints,
        'market_label_counts': None if issues else counts,
        'issues': issues,
    }


def main():
    parser = argparse.ArgumentParser(description='Validate human-labeled market feedback against a shared taxonomy.')
    parser.add_argument('--rules', type=Path, default=os.environ.get('FEEDBACK_RULES_FILE', 'rules/v1.json'))
    parser.add_argument('batches', nargs='+', type=Path)
    args = parser.parse_args()
    try:
        result = check_batches(args.rules, args.batches)
    except (OSError, ValueError, KeyError, csv.Error) as error:
        parser.exit(2, f'Unable to validate feedback: {error}\n')
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    sys.exit(1 if result['issues'] else 0)


if __name__ == '__main__':
    main()
